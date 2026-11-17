// =====================================================================
// Project Controls BI - Power Query (M) queries.  SAMPLE DATA ONLY.
// In Power BI Desktop: Home > Transform data > New Source > Blank Query,
// open Advanced Editor, paste ONE query block, and rename the query to
// the name shown above it. Create the three parameters first
// (Home > Manage Parameters > New Parameter).
// =====================================================================

// ---------- PARAMETERS ----------
// Name: ServerName      Type: Text   Current value: localhost:5432
// Name: DatabaseName    Type: Text   Current value: pcbi
// Name: SourceMode      Type: Text   Current value: Postgres   (or: CSV)
// Name: CsvFolder       Type: Text   Current value: C:\pcbi\data\   (only for CSV mode)

// ---------- QUERY: fnSource (helper function, do not load) ----------
// Returns a table from PostgreSQL (schema pc) or from the CSV folder,
// so the same report works with or without a database.
(objectName as text, csvFile as text) as table =>
let
    FromPostgres = () =>
        let
            Db   = PostgreSQL.Database(ServerName, DatabaseName),
            Item = Db{[Schema = "pc", Item = objectName]}[Data]
        in
            Item,
    FromCsv = () =>
        let
            Raw     = Csv.Document(File.Contents(CsvFolder & csvFile), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
            Headers = Table.PromoteHeaders(Raw, [PromoteAllScalars = true])
        in
            Headers,
    Result = if SourceMode = "CSV" then FromCsv() else FromPostgres()
in
    Result

// ---------- QUERY: DimWBS ----------
let
    Source = fnSource("wbs", "wbs.csv"),
    Typed  = Table.TransformColumnTypes(Source, {
                {"wbs_code", type text}, {"wbs_name", type text}, {"parent_code", type text},
                {"level", Int64.Type}, {"bac_usd", Currency.Type}}),
    Label  = Table.AddColumn(Typed, "wbs_label", each [wbs_code] & " " & [wbs_name], type text)
in
    Label

// ---------- QUERY: FactCost ----------
// Uses the monthly table; cumulative values are built with DAX measures.
// (In Postgres mode you can point this at "vw_cost_cumulative" instead.)
let
    Source = fnSource("cost_monthly", "cost_monthly.csv"),
    Typed  = Table.TransformColumnTypes(Source, {
                {"wbs_code", type text}, {"period_start", type date},
                {"pv_usd", Currency.Type}, {"ev_usd", Currency.Type}, {"ac_usd", Currency.Type},
                {"labor_hours", Int64.Type}, {"overtime_hours", Int64.Type}}),
    // CSV mode reads blanks as empty text; make them true nulls
    Nulls  = Table.ReplaceValue(Typed, "", null, Replacer.ReplaceValue, {"ev_usd", "ac_usd", "labor_hours", "overtime_hours"}),
    HasAct = Table.AddColumn(Nulls, "has_actuals", each [ac_usd] <> null, type logical)
in
    HasAct

// ---------- QUERY: FactMilestone ----------
let
    Source = fnSource("milestones", "milestones.csv"),
    Typed  = Table.TransformColumnTypes(Source, {
                {"milestone_id", type text}, {"wbs_code", type text}, {"milestone_name", type text},
                {"planned_date", type date}, {"actual_or_forecast_date", type date}, {"status", type text}}),
    Var    = Table.AddColumn(Typed, "variance_days",
                each Duration.Days([actual_or_forecast_date] - [planned_date]), Int64.Type)
in
    Var

// ---------- QUERY: FactRisk ----------
// Combines the base register with new risk updates from the Microsoft Forms /
// Power Apps intake (see intake/README.md). Remove the Intake steps if not used.
let
    Source = fnSource("risk_register", "risk_register.csv"),
    Typed  = Table.TransformColumnTypes(Source, {
                {"risk_id", type text}, {"wbs_code", type text}, {"risk_title", type text},
                {"owner_role", type text}, {"impact_1to5", Int64.Type}, {"likelihood_1to5", Int64.Type},
                {"cost_exposure_usd", Currency.Type}, {"date_raised", type date},
                {"date_closed", type date}, {"status", type text}, {"mitigation", type text}}),
    Score  = Table.AddColumn(Typed, "risk_score", each [impact_1to5] * [likelihood_1to5], Int64.Type)
in
    Score

// ---------- QUERY: FactTrend ----------
let
    Source = fnSource("cost_trends", "cost_trends.csv"),
    Typed  = Table.TransformColumnTypes(Source, {
                {"trend_id", type text}, {"wbs_code", type text}, {"trend_description", type text},
                {"date_raised", type date}, {"est_cost_impact_usd", Currency.Type}, {"status", type text},
                {"recovery_type", type text}})   // Client = recover by change order, Internal = our overrun
in
    Typed

// ---------- QUERY: DimDate ----------
let
    StartDate = #date(2026, 1, 1),
    EndDate   = #date(2027, 3, 31),
    Dates     = List.Dates(StartDate, Duration.Days(EndDate - StartDate) + 1, #duration(1, 0, 0, 0)),
    AsTable   = Table.FromList(Dates, Splitter.SplitByNothing(), {"Date"}),
    Typed     = Table.TransformColumnTypes(AsTable, {{"Date", type date}}),
    MonthStart= Table.AddColumn(Typed, "MonthStart", each Date.StartOfMonth([Date]), type date),
    MonthName = Table.AddColumn(MonthStart, "Month", each Date.ToText([Date], "MMM yyyy"), type text),
    MonthSort = Table.AddColumn(MonthName, "MonthSort", each Date.Year([Date]) * 100 + Date.Month([Date]), Int64.Type)
in
    MonthSort
