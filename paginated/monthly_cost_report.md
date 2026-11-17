# Monthly paginated cost report (Power BI Report Builder)

A print-ready, multi-page PDF that goes out once a month. Report Builder is a free
Microsoft download and runs on Windows only.

## Dataset query (PostgreSQL, uses the views in sql/03_views.sql)

Data source: PostgreSQL (via ODBC or the Npgsql provider), database `pcbi`.

```sql
SELECT s.wbs_code,
       s.wbs_name,
       s.bac_usd,
       s.pv_usd, s.ev_usd, s.ac_usd,
       s.cpi, s.spi, s.cost_variance_usd, s.schedule_variance_usd, s.eac_usd, s.vac_usd,
       CASE WHEN s.cpi >= 0.98 THEN 'Green' WHEN s.cpi >= 0.95 THEN 'Amber' ELSE 'Red' END AS cpi_rag,
       CASE WHEN s.spi >= 0.98 THEN 'Green' WHEN s.spi >= 0.95 THEN 'Amber' ELSE 'Red' END AS spi_rag,
       d.status_month
FROM pc.vw_package_status s
CROSS JOIN pc.vw_status_date d
ORDER BY s.wbs_code;
```

Second dataset (open risks, page 2):

```sql
SELECT risk_id, wbs_code, risk_title, owner_role,
       impact_1to5 * likelihood_1to5 AS score, cost_exposure_usd, mitigation
FROM pc.risk_register
WHERE status = 'Open'
ORDER BY score DESC, cost_exposure_usd DESC;
```

Third dataset (milestones, page 3): `SELECT * FROM pc.vw_milestone_variance ORDER BY planned_date;`

## Layout
- Page header: "Infrastructure Cost Report (sample data)" + status month + page X of Y.
- Page 1: KPI row (Total BAC, EV, AC, CPI, SPI, EAC) using Sum/aggregate expressions, then a
  table by package. CPI/SPI cell fill expression:
  `=Switch(Fields!cpi_rag.Value="Green","#DFF0D8", Fields!cpi_rag.Value="Amber","#FCF3CF", True,"#F5B7B1")`
- Page 2: open risks table (insert a page break before the tablix).
- Page 3: milestone variance table.
- Footer: "Prepared from pc views; figures are cumulative to the status month."

## Steps
1. Install Power BI Report Builder.
2. New report > Blank report. Data Sources > Add > connection to PostgreSQL.
3. Datasets > Add the three queries above.
4. Insert > Table for each dataset; add the KPI textboxes on page 1.
5. Run > check numbers match the Power BI Executive Summary page (CPI 0.974, SPI 1.004 for the sample).
6. Export > PDF. Optional: publish the .rdl to a Premium or Fabric workspace and add an email subscription.
   (Publishing paginated reports to the service needs a paid capacity; exporting a PDF locally does not.)
