# Power BI dashboard blueprint

**Canvas:** 16:9, 1366 x 768; slate/navy backgrounds, accessible labels, consistent decimals and business units.

### Page 1 - Fulfillment overview
- Cards: Net Sales, OTIF, Fill Rate, Gross Margin
- Monthly shipped order lines and on-time rate
- Warehouse ranking for OTIF and fill rate
### Page 2 - Inventory health
- Monthly inventory value and turnover proxy
- Stockout snapshot rate by warehouse/category
- SKU drill-through with current snapshot inventory
### Page 3 - Supplier scorecard
- Lead time and receipt reliability by supplier
- Top late suppliers and regional distribution
- Purchase order trend and detail table

## Interactions
- Page-level slicers: Year/Month, primary segment and one operational dimension.
- Sync time slicers across pages and configure drill-through details.
- Tooltip page: KPI definition, period, numerator and denominator.
- Bookmark: Reset filters; navigation: Overview / Drivers / Details.
- Test cross-filter direction, totals, no-data months, empty selections, and long segment names.
