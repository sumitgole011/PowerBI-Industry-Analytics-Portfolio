# Interview Q&A | SaaS Revenue & Customer Churn Intelligence

### Q1. What business decision does this dashboard support?
Leadership asks which segments have weakening retention and whether expansion offsets churn.

### Q2. Explain the data model and its grain.
One row per account x calendar month for subscription data; support tickets have ticket grain.

### Q3. What are the most important model/design trade-offs?
- Use a monthly snapshot fact for MRR, ARR and customer lifecycle measures.
- Use distinct ticket facts instead of adding ticket counts to monthly account rows.
- Measure retention using starting MRR denominators and explicitly distinguish gross/net retention.

### Q4. How did you validate the numbers?
Unique IDs, foreign key integrity and business reconciliations are tested in validate_all.py. Dashboard aggregate measures should match metrics.json under unfiltered or documented period context.

### Q5. How does filter context change the KPIs?
A category or date slicer changes the selected rows before DAX aggregation. Snapshot measures take the final visible period; ratio measures use filtered numerators and denominators instead of averaging displayed percentages.

### Q6. Where would you take this solution next?
Deploy through a managed semantic model, implement scheduled refresh from governed production sources, apply RLS where needed, add automated measure tests, document lineage and monitor adoption.

### Q7. What are the limitations?
Do not sum end-of-month MRR to measure current run-rate.
The HTML dashboard is an offline design prototype. Native PBIX/PBIP and published Power BI report must still be built and tested in Microsoft Power BI.
