# Interview Q&A | Banking Credit Risk & Loan Portfolio Intelligence

### Q1. What business decision does this dashboard support?
Risk operations asks which product cohorts have late payments and how fast collections perform.

### Q2. Explain the data model and its grain.
Applications: one row per application. Loans: one row per approved loan. Installments: one row per due installment.

### Q3. What are the most important model/design trade-offs?
- Separate application approvals from the originated loan and installment grains.
- Use role-playing Date tables for application date, origination and due date.
- Protect against target leakage in any future predictive modelling and avoid credit decisions on fictional data.

### Q4. How did you validate the numbers?
Unique IDs, foreign key integrity and business reconciliations are tested in validate_all.py. Dashboard aggregate measures should match metrics.json under unfiltered or documented period context.

### Q5. How does filter context change the KPIs?
A category or date slicer changes the selected rows before DAX aggregation. Snapshot measures take the final visible period; ratio measures use filtered numerators and denominators instead of averaging displayed percentages.

### Q6. Where would you take this solution next?
Deploy through a managed semantic model, implement scheduled refresh from governed production sources, apply RLS where needed, add automated measure tests, document lineage and monitor adoption.

### Q7. What are the limitations?
Default and delinquency are fixed status as-of September 30, 2026. They must not be presented as historically known at origination.
The HTML dashboard is an offline design prototype. Native PBIX/PBIP and published Power BI report must still be built and tested in Microsoft Power BI.
