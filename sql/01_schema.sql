-- Project Controls BI: schema (PostgreSQL). SAMPLE DATA ONLY.
DROP SCHEMA IF EXISTS pc CASCADE;
CREATE SCHEMA pc;

CREATE TABLE pc.wbs (
  wbs_code     TEXT PRIMARY KEY,
  wbs_name     TEXT NOT NULL,
  parent_code  TEXT,
  level        INT  NOT NULL,
  bac_usd      NUMERIC(14,2) NOT NULL
);

CREATE TABLE pc.cost_monthly (
  wbs_code       TEXT NOT NULL REFERENCES pc.wbs(wbs_code),
  period_start   DATE NOT NULL,
  pv_usd         NUMERIC(14,2) NOT NULL,
  ev_usd         NUMERIC(14,2),          -- NULL = no actuals yet (future month)
  ac_usd         NUMERIC(14,2),
  labor_hours    NUMERIC(12,0),
  overtime_hours NUMERIC(12,0),
  PRIMARY KEY (wbs_code, period_start)
);

CREATE TABLE pc.milestones (
  milestone_id            TEXT PRIMARY KEY,
  wbs_code                TEXT NOT NULL REFERENCES pc.wbs(wbs_code),
  milestone_name          TEXT NOT NULL,
  planned_date            DATE NOT NULL,
  actual_or_forecast_date DATE NOT NULL,
  status                  TEXT NOT NULL CHECK (status IN ('Complete','Forecast'))
);

CREATE TABLE pc.risk_register (
  risk_id           TEXT PRIMARY KEY,
  wbs_code          TEXT NOT NULL REFERENCES pc.wbs(wbs_code),
  risk_title        TEXT NOT NULL,
  owner_role        TEXT NOT NULL,
  impact_1to5       INT  NOT NULL CHECK (impact_1to5 BETWEEN 1 AND 5),
  likelihood_1to5   INT  NOT NULL CHECK (likelihood_1to5 BETWEEN 1 AND 5),
  cost_exposure_usd NUMERIC(14,2) NOT NULL,
  date_raised       DATE NOT NULL,
  date_closed       DATE,
  status            TEXT NOT NULL CHECK (status IN ('Open','Closed')),
  mitigation        TEXT
);

CREATE TABLE pc.cost_trends (
  trend_id            TEXT PRIMARY KEY,
  wbs_code            TEXT NOT NULL REFERENCES pc.wbs(wbs_code),
  trend_description   TEXT NOT NULL,
  date_raised         DATE NOT NULL,
  est_cost_impact_usd NUMERIC(14,2) NOT NULL,
  status              TEXT NOT NULL CHECK (status IN ('Pending','Approved','Rejected')),
  recovery_type       TEXT NOT NULL CHECK (recovery_type IN ('Client','Internal'))  -- Client = recover by change order
);
