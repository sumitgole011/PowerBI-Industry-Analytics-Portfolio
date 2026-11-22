# SaaS Revenue & Customer Churn Intelligence

> **Original synthetic-data Power BI case study**. All organizations, account IDs, financial outcomes and events are simulated. Not real customer/patient/credit data.

## Business problem
A B2B SaaS leadership team wants to understand recurring revenue expansion and customer retention. Avoid double-counting end-of-month MRR across selected months.

## Power BI report project

[Open the Power BI project folder](power-bi/) · [View the report design preview](report-design-preview.png)

The one-page report has cards for monthly recurring revenue, logo churn and net revenue retention, plus an MRR trend and Month and Customer segment slicers. Use it to see whether a segment's retention and churn warrant investigation even while recurring revenue grows.

In Power BI Desktop for Windows, open `power-bi/SaaS Revenue and Churn.pbip` from the cloned or extracted repository and select **Refresh** to load the embedded data. Use **Save As** to export a `.pbix` copy after confirming the numbers below. The project files were checked against Microsoft's report schemas. Opening, rendering and exporting the report in Power BI Desktop remain to be verified. The linked image previews the design and data.

### KPI reconciliation

The model embeds 72 month-and-segment totals from the 4,320-row [starter CSV](POWERBI_SERVICE_STARTER.csv). Values in the table were independently recalculated from the CSV, with no model credentials or machine-specific data path required.

| Filter selection | Monthly recurring revenue | Logo churn | Net revenue retention |
| --- | ---: | ---: | ---: |
| All months (Jan 2024 to Dec 2025), all segments | $47,257.58 | 1.17% | 99.94% |
| Dec 2025, all segments | $47,257.58 | 1.89% | 99.11% |
| Dec 2025, SMB | $17,211.26 | 2.17% | 98.95% |

MRR uses the latest selected month. Logo churn divides churned customers by starting active customers. NRR adjusts starting MRR for expansion, contraction and churn. For multiple months, the last two columns are weighted monthly rates across the selection. The baseline also reconciles to 156 active customers in Dec 2025 and 24 churn events across the full period, as recorded in [metrics.json](metrics.json).

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
- **Current MRR:** 47257.58
- **Current Active Customers:** 156
- **Period Logo Churns:** 24
- **Support Tickets:** 630

## Decisions this project supports
- Investigate whether churn clusters in SMB accounts
- Compare expansion MRR contribution against churned MRR
- Prioritize support capacity where resolution times trend upward

## Portfolio caution
The data has engineered patterns to support demonstration, so it is unsuitable for production forecasts, clinical decisions, lending decisions or real-world inferential claims. Power BI Desktop verification and the `.pbix` export remain open. The self-contained HTML is a functional design preview.
