# Interview Q&A | Healthcare Operations & Hospital Performance

### Q1. What business decision does this dashboard support?
Hospital management wants to reduce wait times while monitoring staffed-bed occupancy.

### Q2. Explain the data model and its grain.
Encounters: one admission encounter. Capacity: one department per calendar day.

### Q3. What are the most important model/design trade-offs?
- Separate daily bed staffing/occupancy from encounters to prevent double counting.
- Use a shared department/date dimension to compare activity with capacity.
- Synthetic patient IDs protect privacy; do not present simulated figures as clinical evidence.

### Q4. How did you validate the numbers?
Unique IDs, foreign key integrity and business reconciliations are tested in validate_all.py. Dashboard aggregate measures should match metrics.json under unfiltered or documented period context.

### Q5. How does filter context change the KPIs?
A category or date slicer changes the selected rows before DAX aggregation. Snapshot measures take the final visible period; ratio measures use filtered numerators and denominators instead of averaging displayed percentages.

### Q6. Where would you take this solution next?
Deploy through a managed semantic model, implement scheduled refresh from governed production sources, apply RLS where needed, add automated measure tests, document lineage and monitor adoption.

### Q7. What are the limitations?
30-day return visit rate is a simple descriptive proxy, not a medically validated readmission rate.
The HTML dashboard is an offline design prototype. Native PBIX/PBIP and published Power BI report must still be built and tested in Microsoft Power BI.
