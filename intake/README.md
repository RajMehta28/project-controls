# Risk update intake (Microsoft Forms + Power Apps)

Purpose: field leads send risk updates in a consistent shape, so the register feeds
the dashboard without retyping. Needs a Microsoft 365 work or school account.

## Option A: Microsoft Forms (quickest)
Form title: "Weekly Risk Update (sample project)"

| # | Question | Type | Maps to column |
|---|----------|------|----------------|
| 1 | Risk ID (leave blank if new) | Text | risk_id |
| 2 | Work package | Choice: 1.0 Whole project, 1.1 Drilled Piers, 1.2 Earthworks and Grading, 1.3 Concrete Foundations, 1.4 Underground Utilities, 1.5 Electrical Duct Bank, 1.6 Site Management and Permits | wbs_code |
| 3 | Risk title | Text | risk_title |
| 4 | Owner role | Choice: Pier Superintendent, Earthworks Manager, Concrete Manager, Field Engineer, Design Lead, Cost Lead, Project Controls Lead, Buyer, Expediter, Equipment Manager, Labor Relations, Permits Coordinator | owner_role |
| 5 | Impact (1 low to 5 high) | Rating 1 to 5 | impact_1to5 |
| 6 | Likelihood (1 low to 5 high) | Rating 1 to 5 | likelihood_1to5 |
| 7 | Estimated cost exposure (USD) | Text, number restriction | cost_exposure_usd |
| 8 | Status | Choice: Open, Closed | status |
| 9 | Mitigation / action | Long text | mitigation |

Responses > Open in Excel. Save that workbook to OneDrive or SharePoint and add it in
Power Query as `RiskIntake` (Excel.Workbook from the SharePoint folder), rename the
columns to match the table above, then in FactRisk: `Table.Combine({Score, RiskIntake})`
and keep the latest row per risk_id (Group By risk_id, max of Completion time).

## Option B: Power Apps canvas app (better control)
- Data: a SharePoint list "RiskRegister" with the same columns (Number columns for 5, 6, 7;
  Choice columns for 2, 4, 8).
- Screens:
  1. Browse: gallery of open risks, filter by work package, sorted by score.
  2. Edit: EditForm bound to RiskRegister; validation so Impact and Likelihood are 1 to 5
     and exposure is not negative. Submit: `SubmitForm(frmRisk); Navigate(scrBrowse)`.
  3. New: same form in New mode, risk_id defaulted to `"R" & Text(CountRows(RiskRegister)+1,"00")`.
- Power BI reads the SharePoint list (SharePoint Online List connector) instead of the CSV.

## What to show in an interview
A screenshot of the form, one submitted update, and the risk page changing after refresh.
