"""Generate SAMPLE project controls data for a fab-site infrastructure scope.
Sample data only. Not affiliated with any real project, client or contractor.
Run: python scripts/generate_data.py  (writes CSVs into ../data)
"""
import csv, math, random, os
from datetime import date

random.seed(42)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
MONTHS = [date(2026, m, 1) for m in range(1, 13)]   # plan Jan-Dec 2026
STATUS_MONTH = 9                                       # actuals through Sep 2026

# code, name, BAC ($), start month, end month, target SPI pattern, target CPI pattern
PACKAGES = [
 ("1.1", "Drilled Piers",               42_000_000, 1, 10, "ahead",   "cpi_drift"),
 ("1.2", "Earthworks and Grading",      18_000_000, 1,  7, "weather", "steady_98"),
 ("1.3", "Concrete Foundations",        30_000_000, 4, 12, "on_plan", "good_102"),
 ("1.4", "Underground Utilities",       14_000_000, 5, 11, "late",    "steady_96"),
 ("1.5", "Electrical Duct Bank",         8_000_000, 7, 12, "on_plan", "on_100"),
 ("1.6", "Site Management and Permits",  8_000_000, 1, 12, "flat",    "steady_97"),
]

def s_curve_weights(n):
    # bell-shaped monthly weights so cumulative PV forms an S-curve
    w = [math.sin(math.pi * (i + 0.5) / n) for i in range(n)]
    t = sum(w); return [x / t for x in w]

def spi_for(pattern, m):
    if pattern == "ahead":   return 1.03 + 0.005 * min(m, 6)
    if pattern == "weather": return [0.80, 0.84, 0.90, 0.97, 1.02, 1.04, 1.03][min(m - 1, 6)]
    if pattern == "late":    return 0.90 + 0.004 * m
    return 1.00

def cpi_for(pattern, m):
    if pattern == "cpi_drift": return 1.01 - 0.012 * (m - 1)      # 1.01 -> ~0.91
    if pattern == "steady_98": return 0.98
    if pattern == "good_102":  return 1.02
    if pattern == "steady_96": return 0.96
    if pattern == "on_100":    return 1.00
    if pattern == "steady_97": return 0.97
    return 1.0

wbs_rows, cost_rows = [], []
wbs_rows.append(["1.0", "Infrastructure (sample)", "", 1, sum(p[2] for p in PACKAGES)])
for code, name, bac, s, e, sp, cp in PACKAGES:
    wbs_rows.append([code, name, "1.0", 2, bac])
    n = e - s + 1
    if sp == "flat":
        weights = [1 / n] * n
    else:
        weights = s_curve_weights(n)
    cum_pv = cum_ev = 0.0
    for i, mth in enumerate(MONTHS):
        mi = i + 1
        pv = bac * weights[mi - s] if s <= mi <= e else 0.0
        if mi <= STATUS_MONTH and pv > 0:
            rel = mi - s + 1
            ev = pv * spi_for(sp, rel) * random.uniform(0.985, 1.015)
            # Earned value can never pass the budget: a package that runs ahead
            # closes only part of its remaining gap each month.
            cap = (cum_pv + pv) + 0.7 * (bac - (cum_pv + pv))
            ev = max(0.0, min(ev, cap - cum_ev))
            cum_pv += pv
            cum_ev += ev
            ac = ev / (cpi_for(cp, rel) * random.uniform(0.99, 1.01))
            base_hours = ac / 95.0                      # rough blended labour rate
            ot_share = 0.06
            if cp == "cpi_drift": ot_share = 0.08 + 0.02 * (rel - 1)   # overtime climbing
            if sp == "weather" and rel in (4, 5): ot_share = 0.16      # recovery push
            ot = base_hours * ot_share
            cost_rows.append([code, mth.isoformat(), round(pv, -3), round(ev, -3), round(ac, -3),
                              round(base_hours), round(ot)])
        else:
            cost_rows.append([code, mth.isoformat(), round(pv, -3), "", "", "", ""])

milestones = [
 ("M01","1.2","Mass grading complete, Area A","2026-03-31","2026-04-24","Complete"),
 ("M02","1.1","Test piers accepted","2026-02-27","2026-02-20","Complete"),
 ("M03","1.1","50% of production piers drilled","2026-05-29","2026-05-15","Complete"),
 ("M04","1.2","Site drainage operational","2026-06-30","2026-07-10","Complete"),
 ("M05","1.3","First foundation pour","2026-04-30","2026-04-28","Complete"),
 ("M06","1.4","Main water line tie-in","2026-07-31","2026-08-21","Complete"),
 ("M07","1.1","All production piers drilled","2026-09-30","2026-09-18","Complete"),
 ("M08","1.3","Foundations 50% complete","2026-08-31","2026-09-04","Complete"),
 ("M09","1.5","Duct bank route energized","2026-11-30","2026-12-04","Forecast"),
 ("M10","1.4","Utilities substantially complete","2026-11-30","2026-12-11","Forecast"),
 ("M11","1.3","Foundations complete","2026-12-18","2026-12-18","Forecast"),
 ("M12","1.0","Infrastructure turnover","2026-12-31","2027-01-08","Forecast"),
]

risks = [
 ("R01","1.1","Rig productivity drops in hard rock layer","Pier Superintendent",4,3,1_200_000,"2026-01-15","2026-04-10","Closed","Added second rig crew; re-sequenced piers"),
 ("R02","1.1","Overtime needed to hold pier schedule","Cost Lead",3,4,1_800_000,"2026-03-02",None,"Open","Weekly overtime vs CPI review"),
 ("R03","1.2","Wet weather delays mass grading","Earthworks Manager",4,4,900_000,"2026-01-10","2026-06-05","Closed","Weather days built in; dewatering"),
 ("R04","1.2","Unsuitable soils require over-excavation","Field Engineer",3,2,600_000,"2026-02-12","2026-05-20","Closed","Geotech test pits ahead of crews"),
 ("R05","1.3","Rebar price escalation","Buyer",3,3,750_000,"2026-03-20","2026-07-15","Closed","Locked supplier pricing for two quarters"),
 ("R06","1.3","Concrete supply constrained at peak pours","Concrete Manager",4,2,500_000,"2026-04-05",None,"Open","Second batch plant on standby"),
 ("R07","1.4","Late delivery of large-bore pipe","Expediter",4,4,1_100_000,"2026-05-03",None,"Open","Expedite supplier; backup vendor quoted"),
 ("R08","1.4","Unknown buried utilities found","Field Engineer",3,3,450_000,"2026-05-18","2026-08-30","Closed","Ground-penetrating radar survey"),
 ("R09","1.5","Duct bank conflicts with utility routing","Design Lead",3,3,400_000,"2026-06-22",None,"Open","Clash review before each segment"),
 ("R10","1.5","Long lead on switchgear interface parts","Expediter",4,2,350_000,"2026-07-07",None,"Open","Early release of purchase order"),
 ("R11","1.6","Permit renewal timing","Permits Coordinator",2,2,150_000,"2026-02-01","2026-03-15","Closed","Renewal filed 60 days early"),
 ("R12","1.6","Craft labor availability at peak","Labor Relations",4,3,1_000_000,"2026-04-11",None,"Open","Hiring plan with union halls"),
 ("R13","1.1","Equipment breakdown on primary rig","Equipment Manager",2,3,250_000,"2026-02-18","2026-03-30","Closed","Spare parts kit on site"),
 ("R14","1.3","Cold weather concrete curing","Concrete Manager",3,4,600_000,"2026-09-10",None,"Open","Heated enclosures and blankets"),
 ("R15","1.0","Scope change from client design update","Project Controls Lead",4,3,1_500_000,"2026-08-14",None,"Open","Change control with cost and schedule impact"),
]

trends = [
 ("T01","1.1","Second drilling crew for hard rock","2026-03-05",850_000,"Approved"),
 ("T02","1.1","Overtime to hold pier schedule (Q2)","2026-06-30",1_200_000,"Approved"),
 ("T03","1.2","Dewatering for wet season","2026-02-20",300_000,"Approved"),
 ("T04","1.2","Over-excavation of unsuitable soils","2026-04-15",420_000,"Approved"),
 ("T05","1.3","Rebar price lock savings","2026-07-15",-380_000,"Approved"),
 ("T06","1.4","Backup pipe vendor premium","2026-08-10",260_000,"Pending"),
 ("T07","1.4","Utility conflict rework","2026-08-28",310_000,"Approved"),
 ("T08","1.5","Re-route duct bank segment 3","2026-09-12",180_000,"Pending"),
 ("T09","1.3","Cold weather protection","2026-09-25",450_000,"Pending"),
 ("T10","1.0","Client design update (scope change)","2026-09-02",2_400_000,"Pending"),
]

def write(name, header, rows):
    with open(os.path.join(OUT, name), "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)

write("wbs.csv", ["wbs_code","wbs_name","parent_code","level","bac_usd"], wbs_rows)
write("cost_monthly.csv", ["wbs_code","period_start","pv_usd","ev_usd","ac_usd","labor_hours","overtime_hours"], cost_rows)
write("milestones.csv", ["milestone_id","wbs_code","milestone_name","planned_date","actual_or_forecast_date","status"], milestones)
write("risk_register.csv", ["risk_id","wbs_code","risk_title","owner_role","impact_1to5","likelihood_1to5","cost_exposure_usd","date_raised","date_closed","status","mitigation"],
      [[*r[:8], r[8] or "", *r[9:]] for r in risks])
# Who pays if the trend is approved: Client = new scope recovered by change order, Internal = our overrun
CLIENT_RECOVERABLE = {"T10"}
trends = [t + ("Client" if t[0] in CLIENT_RECOVERABLE else "Internal",) for t in trends]
write("cost_trends.csv", ["trend_id","wbs_code","trend_description","date_raised","est_cost_impact_usd","status","recovery_type"], trends)
print("wrote", len(cost_rows), "cost rows")
