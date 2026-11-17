-- Reporting views that Power BI reads. Window functions build cumulative earned value.
-- Status date is the last month with actuals.

CREATE OR REPLACE VIEW pc.vw_status_date AS
SELECT MAX(period_start) AS status_month FROM pc.cost_monthly WHERE ac_usd IS NOT NULL;

-- 1) Monthly fact with cumulative PV / EV / AC per work package
CREATE OR REPLACE VIEW pc.vw_cost_cumulative AS
SELECT
  c.wbs_code,
  c.period_start,
  c.pv_usd, c.ev_usd, c.ac_usd, c.labor_hours, c.overtime_hours,
  SUM(c.pv_usd) OVER w AS cum_pv_usd,
  SUM(c.ev_usd) OVER w AS cum_ev_usd,
  SUM(c.ac_usd) OVER w AS cum_ac_usd,
  CASE WHEN c.labor_hours > 0 THEN c.overtime_hours / c.labor_hours END AS overtime_share,
  (c.ac_usd IS NOT NULL) AS has_actuals
FROM pc.cost_monthly c
WINDOW w AS (PARTITION BY c.wbs_code ORDER BY c.period_start
             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW);

-- 2) Earned value status by work package at the status date
CREATE OR REPLACE VIEW pc.vw_package_status AS
WITH s AS (SELECT status_month FROM pc.vw_status_date),
cum AS (
  SELECT v.* FROM pc.vw_cost_cumulative v, s WHERE v.period_start = s.status_month
)
SELECT
  w.wbs_code, w.wbs_name, w.bac_usd,
  cum.cum_pv_usd AS pv_usd, cum.cum_ev_usd AS ev_usd, cum.cum_ac_usd AS ac_usd,
  ROUND(cum.cum_ev_usd / NULLIF(cum.cum_ac_usd,0), 3) AS cpi,
  ROUND(cum.cum_ev_usd / NULLIF(cum.cum_pv_usd,0), 3) AS spi,
  cum.cum_ev_usd - cum.cum_ac_usd AS cost_variance_usd,
  cum.cum_ev_usd - cum.cum_pv_usd AS schedule_variance_usd,
  ROUND(w.bac_usd / NULLIF(cum.cum_ev_usd / NULLIF(cum.cum_ac_usd,0),0), 0) AS eac_usd,
  ROUND(w.bac_usd - w.bac_usd / NULLIF(cum.cum_ev_usd / NULLIF(cum.cum_ac_usd,0),0), 0) AS vac_usd
FROM pc.wbs w
JOIN cum ON cum.wbs_code = w.wbs_code
WHERE w.level = 2;

-- 3) Risk summary by work package
CREATE OR REPLACE VIEW pc.vw_risk_summary AS
SELECT
  r.wbs_code,
  COUNT(*)                                        AS risks_total,
  COUNT(*) FILTER (WHERE r.status = 'Closed')     AS risks_closed,
  COUNT(*) FILTER (WHERE r.status = 'Open')       AS risks_open,
  SUM(r.cost_exposure_usd) FILTER (WHERE r.status = 'Open') AS open_exposure_usd,
  MAX(r.impact_1to5 * r.likelihood_1to5) FILTER (WHERE r.status = 'Open') AS top_open_score
FROM pc.risk_register r
GROUP BY r.wbs_code;

-- 4) Milestone variance in days (positive = late)
CREATE OR REPLACE VIEW pc.vw_milestone_variance AS
SELECT m.*, (m.actual_or_forecast_date - m.planned_date) AS variance_days
FROM pc.milestones m;

-- 5) Early-warning check: months where overtime share rose AND monthly CPI fell (with noise thresholds)
CREATE OR REPLACE VIEW pc.vw_overtime_warning AS
WITH m AS (
  SELECT wbs_code, period_start,
         ev_usd / NULLIF(ac_usd,0) AS monthly_cpi,
         overtime_hours / NULLIF(labor_hours,0) AS ot_share
  FROM pc.cost_monthly WHERE ac_usd IS NOT NULL
)
SELECT wbs_code, period_start,
       ROUND(monthly_cpi, 3) AS monthly_cpi,
       ROUND(ot_share, 3)    AS overtime_share,
       (ot_share - LAG(ot_share) OVER p >= 0.01             -- overtime share up at least 1 point
        AND LAG(monthly_cpi) OVER p - monthly_cpi >= 0.005) -- and monthly CPI down at least 0.005
       AS warning_flag
FROM m
WINDOW p AS (PARTITION BY wbs_code ORDER BY period_start);

-- =====================================================================
-- Cost studies (page 6)
-- =====================================================================

-- Study 1: monthly cost lost to inefficiency (AC - EV) with overtime share,
-- so overtime months can be priced.
CREATE OR REPLACE VIEW pc.vw_study_overtime_cost AS
SELECT c.wbs_code,
       c.period_start,
       ROUND(c.overtime_hours::numeric / NULLIF(c.labor_hours, 0), 3) AS overtime_share,
       ROUND(c.ev_usd / NULLIF(c.ac_usd, 0), 3)                       AS monthly_cpi,
       c.ac_usd - c.ev_usd                                            AS cost_lost_usd
FROM pc.cost_monthly c
WHERE c.ac_usd IS NOT NULL;

-- Study 2: three standard EAC methods side by side, per package.
CREATE OR REPLACE VIEW pc.vw_study_eac_methods AS
SELECT wbs_code, wbs_name, bac_usd, ac_usd, cpi, spi,
       ROUND(ac_usd + (bac_usd - ev_usd))                    AS eac_remaining_to_plan,
       -- use unrounded CPI = EV/AC and SPI = EV/PV so the dollars are exact
       ROUND(bac_usd * ac_usd / NULLIF(ev_usd, 0))                              AS eac_cpi,
       ROUND(ac_usd + (bac_usd - ev_usd) * ac_usd * pv_usd / NULLIF(ev_usd * ev_usd, 0)) AS eac_cpi_spi
FROM pc.vw_package_status;

-- Study 3: pending trend exposure split by who pays.
CREATE OR REPLACE VIEW pc.vw_study_trend_exposure AS
SELECT status, recovery_type,
       COUNT(*)                 AS trends,
       SUM(est_cost_impact_usd) AS impact_usd
FROM pc.cost_trends
GROUP BY status, recovery_type;
