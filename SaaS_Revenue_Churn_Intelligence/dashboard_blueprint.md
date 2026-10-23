# Power BI dashboard blueprint

**Canvas:** 16:9, 1366 x 768; slate/navy backgrounds, accessible labels, consistent decimals and business units.

### Page 1 - Executive overview
- Cards: MRR, ARR, Active Customers, Logo Churn Rate, NRR
- Line chart: monthly MRR and customers
- Waterfall: MRR bridge (start + new + expansion - contraction - churn)
- Slicers: month, segment, industry, region
### Page 2 - Retention and cohorts
- Cohort retention matrix by SignupMonth and reporting month (requires cohort calculation)
- Trend: NRR vs GRR
- Segment-level churn bars
- Customer drill-through: account timeline
### Page 3 - Customer support
- Tickets by priority and CSAT
- Resolution SLA trend
- Tickets vs churn correlation (descriptive only)

## Interactions
- Page-level slicers: Year/Month, primary segment and one operational dimension.
- Sync time slicers across pages and configure drill-through details.
- Tooltip page: KPI definition, period, numerator and denominator.
- Bookmark: Reset filters; navigation: Overview / Drivers / Details.
- Test cross-filter direction, totals, no-data months, empty selections, and long segment names.
