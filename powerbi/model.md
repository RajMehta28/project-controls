# Semantic model and report pages

Sample data only. Not affiliated with Bechtel, Micron or any real project.

## Star schema

```
                 DimDate (Date, MonthStart, Month, MonthSort)
                    |  1
                    |  * (MonthStart -> period_start)
DimWBS 1 ---- * FactCost        (monthly PV, EV, AC, labor and overtime hours)
  (wbs_code) 1 -- * FactMilestone  (planned vs actual/forecast date)
             1 -- * FactRisk       (risk register + intake updates)
             1 -- * FactTrend      (cost trends: Approved / Pending)
```

Relationships (Model view, all single direction, dimension filters fact):

| From (many)               | To (one)            |
|---------------------------|---------------------|
| FactCost[wbs_code]        | DimWBS[wbs_code]    |
| FactCost[period_start]    | DimDate[Date]       |
| FactMilestone[wbs_code]   | DimWBS[wbs_code]    |
| FactRisk[wbs_code]        | DimWBS[wbs_code]    |
| FactTrend[wbs_code]       | DimWBS[wbs_code]    |

Setup notes:
- Mark DimDate as a date table (Table tools > Mark as date table > Date).
- Sort DimDate[Month] by DimDate[MonthSort].
- Hide all wbs_code and period_start columns in fact tables; slicers use DimWBS and DimDate.
- Put all measures in a `_Measures` table (see dax_measures.dax).
- In visuals, filter DimWBS[level] = 2 so the "1.0" roll-up row is not shown as a package.

## Report pages

### 1. Executive Summary
- Cards: BAC, EV to Date, AC to Date, CPI, SPI, EAC, VAC, Percent Complete, Status Month.
- CPI and SPI cards colored with CPI RAG Color / SPI RAG Color (Format > Callout value > fx > Field value).
- Table "Package status": wbs_label, BAC, CPI, SPI, EAC, VAC, CPI RAG, SPI RAG. RAG columns colored by field value.
- Line chart (S-curve): x = DimDate[Month]; values = PV to Date, EV Curve, AC Curve.
- Text box: "Sample data. Status as of" + Status Month.

### 2. Cost by Work Package
- Clustered bar: wbs_label by BAC and EAC (overrun visible at a glance).
- Matrix: rows wbs_label, columns Month, values Monthly CPI (conditional color scale, red under 0.95).
- Line + column combo: Overtime Share (line) vs Monthly CPI (column) for the selected package; slicer on wbs_label.
- Table: months where Overtime Warning = "Warning".

### 3. Schedule and Milestones
- Table: milestone_name, planned_date, actual_or_forecast_date, variance_days, status. Variance colored red when > 0.
- Bar chart: variance_days by milestone (positive = late).
- Cards: Milestones Late, Avg Milestone Variance (days), SPI.

### 4. Risk
- Cards: Risks Open, Risks Closed, Risk Closure %, Open Risk Exposure.
- Scatter (heat map style): x = likelihood_1to5, y = impact_1to5, size = cost_exposure_usd, legend = status.
- Table: open risks sorted by risk_score desc with owner_role and mitigation.

### 5. Cost Trends
- Cards: Trends Approved, Trends Pending, Budget incl. Approved Trends, Exposure if Pending Approved.
- Table: trend_id, wbs_code, trend_description, date_raised, est_cost_impact_usd, status.

### 6. Cost Studies
Three cards, each laid out as Question > Data > Finding > $ Impact > Recommendation
(text boxes for the words, measures for the numbers, so the findings update on refresh).
- Study 1 "Did we pay for speed nobody used?": combo chart Overtime Share (line) vs Monthly CPI
  (column) filtered to 1.1; cards Cost Lost in High-Overtime Months, OT vs CPI Correlation;
  small table of milestones M07 (piers, early) and M08 (foundations, late).
- Study 2 "Which forecast should we believe?": clustered bar of EAC Remaining to Plan, EAC CPI
  Method, EAC CPI SPI Method with BAC as a constant line, filtered to 1.4; card Possible Understatement.
- Study 3 "Is the pending money really our problem?": stacked bar of pending trends by recovery_type;
  cards Pending Client Recoverable, Pending Internal Exposure, EAC incl. Internal Pending.
- Footer text: "Sample data. Shows the method, not real project results."

## Reusable template
After the pages look right: File > Export > Power BI template (.pbit). Save as
`ProjectControls_Template.pbit`. Opening it asks for ServerName, DatabaseName,
SourceMode and CsvFolder, so the same report can point at another project's data.

## Scheduled refresh through a data gateway
Needs: Windows PC that stays on, Power BI Service sign-in (work or school account).
1. Publish the report: Home > Publish > choose a workspace.
2. Install "On-premises data gateway (standard mode)" from Microsoft on the PC that can reach PostgreSQL. Sign in with the same account. Name the gateway.
3. Power BI Service > Settings (gear) > Manage connections and gateways > New > On-premises > select your gateway > Data source type PostgreSQL > Server and Database the same as the parameters > Basic auth (Postgres user and password).
4. Workspace > dataset (semantic model) > Settings > Gateway and cloud connections > map the PostgreSQL source to the connection from step 3.
5. Same page > Refresh > turn on scheduled refresh, set a daily time (for example 6:00 AM).
6. Test: Refresh now, then check Refresh history.

If you have no Power BI Service account, skip this section and do not claim
"gateway" or "scheduled refresh" on the resume.
