-- Load CSVs. Run from the project root with psql:  psql -d pcbi -f sql/02_load.sql
\copy pc.wbs           FROM 'data/wbs.csv'           WITH (FORMAT csv, HEADER true, NULL '')
\copy pc.cost_monthly  FROM 'data/cost_monthly.csv'  WITH (FORMAT csv, HEADER true, NULL '')
\copy pc.milestones    FROM 'data/milestones.csv'    WITH (FORMAT csv, HEADER true, NULL '')
\copy pc.risk_register FROM 'data/risk_register.csv' WITH (FORMAT csv, HEADER true, NULL '')
\copy pc.cost_trends   FROM 'data/cost_trends.csv'   WITH (FORMAT csv, HEADER true, NULL '')
