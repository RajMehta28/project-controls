"""Recompute every KPI from the raw CSVs with pandas, independent of SQL,
and (optionally) compare with the PostgreSQL views.

Run from the project root:
    python scripts/validate.py                 # CSV-only checks
    python scripts/validate.py --postgres "postgresql://postgres@localhost:5432/pcbi"
(the --postgres check calls the psql command line tool, so psql must be on PATH)
"""
import argparse, io, subprocess, sys
import pandas as pd

def sql(conn, query):
    out = subprocess.run(["psql", conn, "--csv", "-c", query], capture_output=True, text=True, check=True).stdout
    return pd.read_csv(io.StringIO(out), dtype={"wbs_code": str})

D = "data/"
wbs = pd.read_csv(D + "wbs.csv", dtype={"wbs_code": str, "parent_code": str})
cost = pd.read_csv(D + "cost_monthly.csv", dtype={"wbs_code": str}, parse_dates=["period_start"])
ms = pd.read_csv(D + "milestones.csv", parse_dates=["planned_date", "actual_or_forecast_date"])
risk = pd.read_csv(D + "risk_register.csv")
trend = pd.read_csv(D + "cost_trends.csv")

problems = []
def check(cond, msg):
    if not cond:
        problems.append(msg)

# ---- data quality ----
pk = wbs[wbs.level == 2]
check(abs(pk.bac_usd.sum() - wbs.loc[wbs.level == 1, "bac_usd"].iloc[0]) < 1, "Package BAC does not add to root BAC")
for code, g in cost.groupby("wbs_code"):
    bac = pk.set_index("wbs_code").bac_usd[code]
    check(abs(g.pv_usd.sum() - bac) <= 0.005 * bac, f"{code}: total PV {g.pv_usd.sum():,.0f} != BAC {bac:,.0f}")
check(not cost.duplicated(["wbs_code", "period_start"]).any(), "Duplicate wbs/month rows")
check(cost.wbs_code.isin(pk.wbs_code).all(), "Cost rows with unknown WBS")
check(risk.impact_1to5.between(1, 5).all() and risk.likelihood_1to5.between(1, 5).all(), "Risk scores out of 1-5")
check(((risk.status == "Closed") == risk.date_closed.notna()).all(), "Closed risks must have a close date (and only they)")
act = cost[cost.labor_hours.notna()]
check((act.overtime_hours <= act.labor_hours).all(), "Overtime hours exceed labor hours")
check(cost.groupby("wbs_code").ev_usd.sum().le(pk.set_index("wbs_code").bac_usd * 1.0001).all(), "EV to date exceeds BAC")

# ---- KPIs at the status month ----
status = cost.loc[cost.ac_usd.notna(), "period_start"].max()
to_date = cost[cost.period_start <= status]
pkg = to_date.groupby("wbs_code")[["pv_usd", "ev_usd", "ac_usd"]].sum().join(pk.set_index("wbs_code")[["wbs_name", "bac_usd"]])
pkg["cpi"] = pkg.ev_usd / pkg.ac_usd
pkg["spi"] = pkg.ev_usd / pkg.pv_usd
pkg["eac"] = pkg.bac_usd / pkg.cpi
pkg["vac"] = pkg.bac_usd - pkg.eac
# TCPI on BAC has no meaning once actual cost passes the budget
pkg["tcpi"] = ((pkg.bac_usd - pkg.ev_usd) / (pkg.bac_usd - pkg.ac_usd)).where(pkg.ac_usd < pkg.bac_usd)

tot = pkg[["pv_usd", "ev_usd", "ac_usd", "bac_usd"]].sum()
proj_cpi, proj_spi = tot.ev_usd / tot.ac_usd, tot.ev_usd / tot.pv_usd

print(f"Status month: {status:%b %Y}")
show = pkg[["wbs_name", "bac_usd", "ac_usd", "cpi", "spi", "eac", "vac", "tcpi"]].copy()
for c in ["bac_usd", "ac_usd", "eac", "vac"]: show[c] = (show[c] / 1e6).round(2)
print("($ in millions; TCPI blank = budget already spent)")
print(show.round(3).to_string())
print(f"\nProject: PV {tot.pv_usd/1e6:.3f}M  EV {tot.ev_usd/1e6:.3f}M  AC {tot.ac_usd/1e6:.3f}M  "
      f"CPI {proj_cpi:.3f}  SPI {proj_spi:.3f}  EAC {tot.bac_usd/proj_cpi/1e6:.2f}M")
print(f"Risk closure: {(risk.status=='Closed').sum()} of {len(risk)} "
      f"({(risk.status=='Closed').mean():.0%}); open exposure ${risk.loc[risk.status=='Open','cost_exposure_usd'].sum():,.0f}")
print(f"Trends approved ${trend.loc[trend.status=='Approved','est_cost_impact_usd'].sum():,.0f}; "
      f"pending ${trend.loc[trend.status=='Pending','est_cost_impact_usd'].sum():,.0f}")
ms["variance_days"] = (ms.actual_or_forecast_date - ms.planned_date).dt.days
print("Milestones late:", (ms.variance_days > 0).sum(), "of", len(ms))

# ---- overtime early warning (same rule as SQL and DAX) ----
m = cost[cost.ac_usd.notna()].sort_values(["wbs_code", "period_start"]).copy()
m["mcpi"] = m.ev_usd / m.ac_usd
m["ot"] = m.overtime_hours / m.labor_hours
g = m.groupby("wbs_code")
m["warn"] = (m.ot - g.ot.shift() >= 0.01) & (g.mcpi.shift() - m.mcpi >= 0.005)
w = m[m.warn]
print("Overtime warnings:", ", ".join(f"{r.wbs_code} {r.period_start:%b}" for r in w.itertuples()) or "none")

# ---- cost studies ----
pr = m[m.wbs_code == "1.1"].copy()
study1 = (pr.ac_usd - pr.ev_usd)[pr.ot.round(3) >= 0.14].sum()
corr = pr.ot.corr(pr.mcpi)
u = pkg.loc["1.4"]
eac_cs = u.ac_usd + (u.bac_usd - u.ev_usd) / (u.cpi * u.spi)
pend = trend[trend.status == "Pending"].groupby("recovery_type").est_cost_impact_usd.sum()
print(f"Study 1: piers cost lost in 14%+ overtime months ${study1:,.0f}; OT vs CPI correlation {corr:.2f}")
print(f"Study 2: utilities EAC CPI ${u.eac:,.0f} vs CPI*SPI ${eac_cs:,.0f} (gap ${eac_cs-u.eac:,.0f})")
print(f"Study 3: pending client ${pend.get('Client',0):,.0f}, internal ${pend.get('Internal',0):,.0f}; "
      f"EAC incl. internal pending ${tot.bac_usd/proj_cpi + pend.get('Internal',0):,.0f}")

# ---- optional: compare with PostgreSQL views ----
ap = argparse.ArgumentParser(); ap.add_argument("--postgres"); a = ap.parse_args()
if a.postgres:
    v = sql(a.postgres, "SELECT wbs_code, cpi, spi, eac_usd FROM pc.vw_package_status").set_index("wbs_code")
    vw = sql(a.postgres, "SELECT wbs_code, period_start FROM pc.vw_overtime_warning WHERE warning_flag")
    for code in pkg.index:
        check(abs(float(v.cpi[code]) - pkg.cpi[code]) < 0.001, f"{code}: CPI SQL {v.cpi[code]} vs pandas {pkg.cpi[code]:.3f}")
        check(abs(float(v.spi[code]) - pkg.spi[code]) < 0.001, f"{code}: SPI SQL {v.spi[code]} vs pandas {pkg.spi[code]:.3f}")
        check(abs(float(v.eac_usd[code]) - pkg.eac[code]) < 0.001 * pkg.eac[code], f"{code}: EAC mismatch")
    check(len(vw) == len(w), f"Overtime warnings: SQL {len(vw)} vs pandas {len(w)}")
    s1 = sql(a.postgres, "SELECT SUM(cost_lost_usd) AS v FROM pc.vw_study_overtime_cost WHERE wbs_code='1.1' AND overtime_share >= 0.14").v[0]
    check(abs(float(s1) - study1) < 1, f"Study 1: SQL {s1} vs pandas {study1}")
    s2 = sql(a.postgres, "SELECT eac_cpi_spi AS v FROM pc.vw_study_eac_methods WHERE wbs_code='1.4'").v[0]
    check(abs(float(s2) - eac_cs) < 2, f"Study 2: SQL {s2} vs pandas {eac_cs:.0f}")
    print("Compared with PostgreSQL views.")

print("\nALL CHECKS PASSED" if not problems else "\nPROBLEMS:\n- " + "\n- ".join(problems))
sys.exit(1 if problems else 0)
