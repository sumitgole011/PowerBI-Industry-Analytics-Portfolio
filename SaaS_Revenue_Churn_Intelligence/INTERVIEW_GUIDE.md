# Interview Q&A | SaaS Revenue & Customer Churn Intelligence

## December SMB walkthrough

1. Open the [SaaS dashboard](https://sumitgole011.github.io/PowerBI-Industry-Analytics-Portfolio/SaaS_Revenue_Churn_Intelligence/dashboard_preview.html). Choose December 2025 and leave **Customer segment** on **All segments**.
2. Switch **Customer segment** to **SMB**. Compare the three metrics below.

   | December 2025 | MRR | Logo churn | Net revenue retention |
   | --- | ---: | ---: | ---: |
   | All segments | $47,257.58 | 1.89% | 99.11% |
   | SMB | $17,211.26 | 2.17% | 98.95% |

3. Explain the denominator. SMB lost one of its 46 starting customers, and net revenue retention was 0.16 percentage points below the overall figure. Look at the churned account, downgrades and several months of retention before calling this a trend. All numbers come from the synthetic dataset.

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
Current MRR uses the latest month-end snapshot. The interactive dashboard uses synthetic data. The editable Power BI project is included, with Desktop verification and the `.pbix` export still pending.
