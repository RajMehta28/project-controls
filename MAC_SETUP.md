# Building this on a Mac

Power BI Desktop and Power BI Report Builder are Windows-only. Everything else here
(PostgreSQL, SQL, Python, the preview) runs on a Mac as is.

Options for the Power BI part, cheapest first:
1. **A Windows PC** you can borrow, or a campus lab machine (ask Syracuse ITS whether
   alumni can still use the virtual lab).
2. **Parallels Desktop** with Windows 11 on Apple Silicon. Parallels has a 14-day free trial.
   Give the VM at least 8 GB RAM. Install Power BI Desktop from the
   Microsoft Store inside Windows.
3. **Power BI Service in a browser** (app.powerbi.com) can edit reports, but it needs a work or
   school account, and data modeling there is limited. Fine for viewing and small edits.

PostgreSQL on Mac: `brew install postgresql@16 && brew services start postgresql@16`.
For Power BI inside Parallels to reach Postgres on the Mac, either use CSV mode
(SourceMode = CSV, CsvFolder = the shared Mac folder), or set `listen_addresses='*'` in
postgresql.conf, allow the VM subnet in pg_hba.conf, and use the Mac's IP as ServerName.
CSV mode is the easy path.
