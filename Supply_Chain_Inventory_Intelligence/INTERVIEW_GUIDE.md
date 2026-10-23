# Interview Q&A | Supply Chain & Inventory Optimization

### Q1. What business decision does this dashboard support?
Operations asks which fulfillment locations and suppliers drive low OTIF and stockouts.

### Q2. Explain the data model and its grain.
Customer orders: one order line. Inventory: one SKU x warehouse x month. Procurement: one purchase order.

### Q3. What are the most important model/design trade-offs?
- Separate orders, inventory snapshots, and purchase orders to keep each fact grain consistent.
- Avoid duplicate active filter paths from suppliers to procurement.
- Use a consistent snapshot month definition before aggregating inventory value or stockout counts.

### Q4. How did you validate the numbers?
Unique IDs, foreign key integrity and business reconciliations are tested in validate_all.py. Dashboard aggregate measures should match metrics.json under unfiltered or documented period context.

### Q5. How does filter context change the KPIs?
A category or date slicer changes the selected rows before DAX aggregation. Snapshot measures take the final visible period; ratio measures use filtered numerators and denominators instead of averaging displayed percentages.

### Q6. Where would you take this solution next?
Deploy through a managed semantic model, implement scheduled refresh from governed production sources, apply RLS where needed, add automated measure tests, document lineage and monitor adoption.

### Q7. What are the limitations?
OTIF is measured per original order line; cancelled orders count as failures. Inventory turnover is a simplified proxy.
The HTML dashboard is an offline design prototype. Native PBIX/PBIP and published Power BI report must still be built and tested in Microsoft Power BI.
