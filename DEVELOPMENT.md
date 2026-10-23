# Reproducible development workflow

All datasets were produced with deterministic Python standard-library random generators. The report documents require `reportlab` for regeneration; HTML previews and CSV generation require only Python's standard library.

```bash
python scripts/generate_data.py
python scripts/generate_previews.py
python scripts/generate_docs_service_data.py
python validate_all.py
```

**Important:** regeneration overwrites generated data and portfolio documentation. Manual edits to dashboards or data may be lost. Do not rerun unless you intend to rebuild the generated sources. The committed dataset snapshots are the tested sample baseline.

Power BI Desktop on Windows is required to author and validate `.pbix`/`.pbip` assets. For Mac, use the `POWERBI_SERVICE_STARTER.csv` with Power BI Service for the quick-start report.
