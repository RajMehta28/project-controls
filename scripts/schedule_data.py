"""Activity-level schedule for the sample project (Planner Dashboard).
Milestone finishes match data/milestones.csv. Status date 2026-09-30. Calendar days."""
import csv
STATUS = "2026-09-30"
# id, name, package, baseline start, baseline finish, actual start, actual finish, forecast finish (in progress), forecast duration (not started), predecessors, milestone
ACTS = [
 ("A01","Mobilize drill rigs","1.1","2026-01-05","2026-01-23","2026-01-05","2026-01-20",None,None,"",""),
 ("A02","Test piers and load tests","1.1","2026-01-23","2026-02-27","2026-01-20","2026-02-20",None,None,"A01","M02"),
 ("A03","Production piers, zone 1","1.1","2026-02-27","2026-05-29","2026-02-20","2026-05-15",None,None,"A02","M03"),
 ("A04","Production piers, zone 2","1.1","2026-05-29","2026-09-30","2026-05-15","2026-09-18",None,None,"A03","M07"),
 ("A05","Clearing and erosion control","1.2","2026-01-05","2026-02-06","2026-01-05","2026-02-13",None,None,"",""),
 ("A06","Mass grading, Area A","1.2","2026-02-06","2026-03-31","2026-02-13","2026-04-24",None,None,"A05","M01"),
 ("A07","Site drainage","1.2","2026-03-31","2026-06-30","2026-04-24","2026-07-10",None,None,"A06","M04"),
 ("A08","Forms and rebar, first foundations","1.3","2026-04-01","2026-04-30","2026-03-30","2026-04-28",None,None,"A02","M05"),
 ("A09","Foundations, zone 1","1.3","2026-04-30","2026-08-31","2026-04-28","2026-09-04",None,None,"A08","M08"),
 ("A10","Foundations, zone 2","1.3","2026-09-30","2026-12-18","2026-09-18",None,"2026-12-18",None,"A04;A09","M11"),
 ("A11","Water line and tie-in","1.4","2026-05-01","2026-07-31","2026-05-08","2026-08-21",None,None,"A06","M06"),
 ("A12","Remaining utility runs","1.4","2026-07-31","2026-11-30","2026-08-21",None,"2026-12-11",None,"A11","M10"),
 ("A13","Duct bank trenching","1.5","2026-07-01","2026-09-15","2026-07-01","2026-09-22",None,None,"A06",""),
 ("A14","Duct bank encasement and cable pull","1.5","2026-09-15","2026-11-30","2026-09-22",None,"2026-12-04",None,"A13","M09"),
 ("A15","Utility testing and flushing","1.4","2026-11-30","2026-12-21",None,None,None,18,"A12",""),
 ("A16","Final inspections and turnover","1.0","2026-12-21","2026-12-31",None,None,None,10,"A10;A14;A15","M12"),
]
COLS = ["activity_id","activity_name","wbs_code","bl_start","bl_finish","act_start","act_finish","fc_finish","fc_duration_days","predecessors","milestone_id"]
if __name__ == "__main__":
    with open("data/schedule_activities.csv","w",newline="") as f:
        w = csv.writer(f); w.writerow(COLS); w.writerows([[("" if v is None else v) for v in r] for r in ACTS])
    print("wrote data/schedule_activities.csv")

# ---- 3-week look-ahead (weeks starting Mon Oct 5, 12, 19) ----
# week, activity, task, quantity, unit, constraint ("" = none), constraint status, constraint owner, need-by date, link to register
LOOKAHEAD = [
 ("2026-10-05","A12","Storm line run S-4",320,"LF","","Ready","","",""),
 ("2026-10-05","A12","Sanitary line MH-12 to MH-14",260,"LF","Large-bore pipe delivery","Open","Expediter","2026-10-02","R07"),
 ("2026-10-05","A10","Pour footings F-21 to F-24",4,"pours","","Ready","","",""),
 ("2026-10-05","A14","Encase duct bank segment DB-3",180,"LF","","Ready","","",""),
 ("2026-10-12","A12","Fire water loop segment FW-3",400,"LF","Road crossing permit","Open","Permits Coordinator","2026-10-09",""),
 ("2026-10-12","A12","Sanitary line MH-14 to MH-16",280,"LF","Large-bore pipe delivery","Open","Expediter","2026-10-09","R07"),
 ("2026-10-12","A10","Pour footings F-25 to F-28",4,"pours","Rebar delivery","Cleared","Buyer","2026-10-08",""),
 ("2026-10-12","A14","Encase duct bank segment DB-4",200,"LF","Re-route design for segment 3","Open","Design Lead","2026-10-09","T08"),
 ("2026-10-19","A12","Pressure test storm line S-4",1,"test","","Ready","","",""),
 ("2026-10-19","A12","Storm line run S-5",350,"LF","","Ready","","",""),
 ("2026-10-19","A10","Pour grade beams GB-7 to GB-9",3,"pours","Cold weather protection approval","Open","Cost Lead","2026-10-16","T09"),
 ("2026-10-19","A14","Cable pull DB-1 to DB-2",2,"pulls","","Ready","","",""),
]
LA_COLS = ["week_start","activity_id","task","quantity","unit","constraint","constraint_status","constraint_owner","need_by","register_link"]
if __name__ == "__main__":
    with open("data/lookahead.csv","w",newline="") as f:
        w = csv.writer(f); w.writerow(LA_COLS); w.writerows(LOOKAHEAD)
    print("wrote data/lookahead.csv")
