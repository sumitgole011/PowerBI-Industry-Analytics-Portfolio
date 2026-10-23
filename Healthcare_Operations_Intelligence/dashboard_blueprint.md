# Power BI dashboard blueprint

**Canvas:** 16:9, 1366 x 768; slate/navy backgrounds, accessible labels, consistent decimals and business units.

### Page 1 - Operations command center
- Cards: Encounters, ALOS, Occupancy, Avg Wait
- Line chart: weekly encounters
- Bed occupancy trend by department
- Department heatmap of wait time
### Page 2 - Patient experience
- Visit types and waiting times
- 30-day return visit rate by department
- Patient counts by age band/payer (synthetic)
### Page 3 - Unit economics
- Collected revenue vs direct cost
- Contribution margin by department
- Outlier drill-through: stay-days and cost

## Interactions
- Page-level slicers: Year/Month, primary segment and one operational dimension.
- Sync time slicers across pages and configure drill-through details.
- Tooltip page: KPI definition, period, numerator and denominator.
- Bookmark: Reset filters; navigation: Overview / Drivers / Details.
- Test cross-filter direction, totals, no-data months, empty selections, and long segment names.
