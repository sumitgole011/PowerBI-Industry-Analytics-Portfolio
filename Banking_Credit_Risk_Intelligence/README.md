# Banking Credit Risk & Loan Portfolio Intelligence

> **Original synthetic-data Power BI case study**. All organizations, account IDs, financial outcomes and events are simulated. Not real customer/patient/credit data.

## Business problem
Credit portfolio managers need to track approval decisions, origination mix, delinquency and repayments without leaking future default outcomes into historical approval analysis.

## Included artifacts
- `data/*.csv`: source tables with explicit grains and stable surrogate IDs
- `POWERBI_SERVICE_STARTER.csv`: denormalized primary-fact CSV for a quick Power BI Service browser report (secondary flat CSVs provided when relevant)
- `measures.dax`: analyst-reviewed starter measures (paste into Power BI as individual measures)
- `relationships.md`: modelling and filter directions
- `dashboard_blueprint.md`: wireframe-by-page, visuals and navigation
- `dashboard_preview.html`: interactive standalone mock dashboard (NOT an actual .pbix or a published Power BI report)
- `project_brief.pdf`: business questions, KPI contract, build steps and interview talking points
- `metrics.json`, `schema.json`, `data_dictionary.md` and `INTERVIEW_GUIDE.md`: QA inputs, field definitions and interview explanations

## Getting started on a Mac
1. In Power BI Service go to **My workspace > New item > Semantic model > CSV** and import `POWERBI_SERVICE_STARTER.csv`. This creates a starter single-table model.
2. In the semantic model, verify dates/number types; build a basic one-table report using its fields. For the **advanced multi-table model** and all measures in `measures.dax`, import every file under `data/` using Power BI Desktop on Windows or a suitably provisioned Fabric data workflow, then create relationships from `relationships.md`. Web modelling features vary by license and workspace.
3. Create a report and reproduce the applicable visuals in `dashboard_blueprint.md`. To replicate all 3 pages and multi-fact KPIs, use the advanced multi-table model.
4. Export screenshots and PDF after validating totals; save a native `.pbix` / `.pbip` when using Power BI Desktop.

## KPIs and sample baseline
- **Applications:** 650
- **Approval Rate:** 77.54
- **Disbursed Principal:** 11296861.93
- **Defaulted Loans As Of 2026-09-30:** 45

## Decisions this project supports
- Review 30+ day arrears and monitor collections
- Locate product cohorts with deteriorating loan performance
- Separate application approval metrics from as-of delinquency status

## Portfolio caution
The data has engineered patterns to support demonstration, so it is unsuitable for production forecasts, clinical decisions, lending decisions or real-world inferential claims. Native Power BI report files and Power BI-hosted links must be completed in Microsoft Power BI; the self-contained HTML is a functional design preview.
