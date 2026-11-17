"""Build planner/index.html (Planner Dashboard) from data/schedule_activities.csv and data/milestones.csv."""
import csv, json
from schedule_data import STATUS
acts = list(csv.DictReader(open("data/schedule_activities.csv")))
ms = list(csv.DictReader(open("data/milestones.csv")))
la = list(csv.DictReader(open("data/lookahead.csv")))
cm = [r for r in csv.DictReader(open("data/cost_monthly.csv")) if r["ac_usd"] and r["period_start"] <= "2026-09-01"]
spi = sum(float(r["ev_usd"]) for r in cm) / sum(float(r["pv_usd"]) for r in cm)
html = open("scripts/planner_template.html").read().replace("/*DATA*/null", json.dumps({"status": STATUS, "acts": acts, "ms": ms, "la": la, "spi": round(spi, 3)}))
open("planner/index.html", "w").write(html); print("planner/index.html written")
