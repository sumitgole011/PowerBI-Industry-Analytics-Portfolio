# Power BI dashboard blueprint

**Canvas:** 16:9, 1366 x 768; slate/navy backgrounds, accessible labels, consistent decimals and business units.

### Page 1 - Credit portfolio overview
- Cards: Applications, Approval Rate, Disbursed Principal, Default Rate
- Monthly originations and applications
- Origination mix by product and region
- Approval rate by credit score bands
### Page 2 - Risk quality
- 30+ DPD loan rate and 90+ DPD count
- Risk matrix: DTI band x credit score band
- Default status by original loan size
- Important disclosure: status measured only at 2026-09-30
### Page 3 - Collections
- Installments due vs paid by due month
- Collection rate trend by product
- Loan-level delinquency drill-through

## Interactions
- Page-level slicers: Year/Month, primary segment and one operational dimension.
- Sync time slicers across pages and configure drill-through details.
- Tooltip page: KPI definition, period, numerator and denominator.
- Bookmark: Reset filters; navigation: Overview / Drivers / Details.
- Test cross-filter direction, totals, no-data months, empty selections, and long segment names.
