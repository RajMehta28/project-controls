"""Build preview/index.html (a browser mock of the Power BI pages) from data/*.csv."""
import json, pandas as pd
D="data/"
wbs=pd.read_csv(D+"wbs.csv",dtype={"wbs_code":str}); cost=pd.read_csv(D+"cost_monthly.csv",dtype={"wbs_code":str},parse_dates=["period_start"])
ms=pd.read_csv(D+"milestones.csv",parse_dates=["planned_date","actual_or_forecast_date"]); risk=pd.read_csv(D+"risk_register.csv",dtype={"wbs_code":str}); tr=pd.read_csv(D+"cost_trends.csv",dtype={"wbs_code":str})
pk=wbs[wbs.level==2].set_index("wbs_code")
status=cost.loc[cost.ac_usd.notna(),"period_start"].max()
td=cost[cost.period_start<=status]
g=td.groupby("wbs_code")[["pv_usd","ev_usd","ac_usd"]].sum().join(pk[["wbs_name","bac_usd"]])
g["cpi"]=g.ev_usd/g.ac_usd; g["spi"]=g.ev_usd/g.pv_usd; g["eac"]=g.bac_usd/g.cpi; g["vac"]=g.bac_usd-g.eac
g["tcpi"]=((g.bac_usd-g.ev_usd)/(g.bac_usd-g.ac_usd)).where(g.ac_usd<g.bac_usd)
t=g[["pv_usd","ev_usd","ac_usd","bac_usd"]].sum(); cpi=t.ev_usd/t.ac_usd; spi=t.ev_usd/t.pv_usd
months=sorted(cost.period_start.unique()); mlab=[pd.Timestamp(m).strftime("%b") for m in months]
def curve(code=None):
    c=cost if code is None else cost[cost.wbs_code==code]
    m=c.groupby("period_start")[["pv_usd","ev_usd","ac_usd"]].sum(min_count=1).reindex(months)
    pv=m.pv_usd.cumsum(); ev=m.ev_usd.fillna(0).cumsum(); ac=m.ac_usd.fillna(0).cumsum()
    act=[pd.Timestamp(x)<=status for x in months]
    r=lambda s:[round(v/1e6,2) for v in s]
    return {"pv":r(pv),"ev":[v if a else None for v,a in zip(r(ev),act)],"ac":[v if a else None for v,a in zip(r(ac),act)]}
curves={"all":curve(),**{c:curve(c) for c in pk.index}}
ot={}
for code in pk.index:
    m=cost[(cost.wbs_code==code)&cost.ac_usd.notna()].sort_values("period_start").copy()
    m["mcpi"]=m.ev_usd/m.ac_usd; m["ots"]=m.overtime_hours/m.labor_hours
    m["warn"]=(m.ots-m.ots.shift()>=0.01)&(m.mcpi.shift()-m.mcpi>=0.005)
    ot[code]={"m":[d.strftime("%b") for d in m.period_start],"cpi":m.mcpi.round(3).tolist(),"ot":(m.ots*100).round(1).tolist(),"warn":m.warn.tolist()}
ms["var"]=(ms.actual_or_forecast_date-ms.planned_date).dt.days
data={"status":status.strftime("%b %Y"),"bac":t.bac_usd,"ev":t.ev_usd,"ac":t.ac_usd,"pv":t.pv_usd,"cpi":cpi,"spi":spi,"eac":t.bac_usd/cpi,
 "pkgs":[{"code":c,"name":r.wbs_name,"bac":r.bac_usd,"ac":r.ac_usd,"cpi":r.cpi,"spi":r.spi,"eac":r.eac,"vac":r.vac,"tcpi":None if pd.isna(r.tcpi) else r.tcpi} for c,r in g.iterrows()],
 "months":mlab,"curves":curves,"ot":ot,
 "ms":[{"id":r.milestone_id,"name":r.milestone_name,"wbs":r.wbs_code,"plan":r.planned_date.strftime("%b %d"),"act":r.actual_or_forecast_date.strftime("%b %d"),"var":int(r["var"]),"status":r.status} for _,r in ms.sort_values("planned_date").iterrows()],
 "risks":[{"id":r.risk_id,"wbs":r.wbs_code,"title":r.risk_title,"owner":r.owner_role,"i":int(r.impact_1to5),"l":int(r.likelihood_1to5),"exp":r.cost_exposure_usd,"status":r.status,"mit":r.mitigation} for _,r in risk.iterrows()],
 "trends":[{"id":r.trend_id,"wbs":r.wbs_code,"desc":r.trend_description,"date":r.date_raised,"amt":r.est_cost_impact_usd,"status":r.status} for _,r in tr.iterrows()]}
# ---- cost studies ----
pr=cost[(cost.wbs_code=="1.1")&cost.ac_usd.notna()].copy(); pr["ots"]=(pr.overtime_hours/pr.labor_hours).round(3); pr["mcpi"]=pr.ev_usd/pr.ac_usd
s1=float((pr.ac_usd-pr.ev_usd)[pr.ots>=0.14].sum()); corr=float(pr.ots.corr(pr.mcpi))
msx=ms.set_index("milestone_id")
u=g.loc["1.4"]; eac_plan=u.ac_usd+(u.bac_usd-u.ev_usd); eac_cs=u.ac_usd+(u.bac_usd-u.ev_usd)/(u.cpi*u.spi)
pend=tr[tr.status=="Pending"].groupby("recovery_type").est_cost_impact_usd.sum()
data["studies"]={"s1":{"lost":s1,"corr":corr,"m07":int(msx.loc["M07","var"]),"m08":int(msx.loc["M08","var"]),
  "otFrom":float(pr.ots.iloc[0]),"otTo":float(pr.ots.iloc[-1]),"cpiFrom":float(pr.mcpi.iloc[0]),"cpiTo":float(pr.mcpi.iloc[-1])},
 "s2":{"bac":u.bac_usd,"plan":eac_plan,"cpi":u.eac,"cs":eac_cs,"m06":int(msx.loc["M06","var"]),"m10":int(msx.loc["M10","var"])},
 "s3":{"client":float(pend.get("Client",0)),"internal":float(pend.get("Internal",0)),"eac":float(data["eac"]),
  "items":[{"id":r.trend_id,"desc":r.trend_description,"amt":r.est_cost_impact_usd,"rec":r.recovery_type} for _,r in tr[tr.status=="Pending"].iterrows()]}}
html=open("scripts/preview_template.html").read().replace("/*DATA*/null",json.dumps(data,default=float))
open("preview/index.html","w").write(html); print("preview/index.html written")
