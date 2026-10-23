# Data dictionary and data contracts

**SaaS Revenue & Customer Churn Intelligence**

## Table grain
One row per account x calendar month for subscription data; support tickets have ticket grain.

## Tables and columns

### DimDate (731 records)

| Field | Inferred type | Example |
|---|---|---|
| `Date` | Date (ISO) | `2024-01-01` |
| `Year` | Number | `2024` |
| `Quarter` | Text | `Q1` |
| `MonthNumber` | Number | `1` |
| `MonthName` | Text | `January` |
| `YearMonth` | Text | `2024-01` |
| `MonthStart` | Date (ISO) | `2024-01-01` |
| `DayOfWeek` | Text | `Monday` |

### DimCustomer (180 records)

| Field | Inferred type | Example |
|---|---|---|
| `CustomerID` | Text | `C0001` |
| `Company` | Text | `Synthetic Account 0001` |
| `Industry` | Text | `Retail` |
| `Segment` | Text | `Mid-Market` |
| `Region` | Text | `India` |
| `PlanID` | Text | `PL1` |
| `SignupMonth` | Date (ISO) | `2024-01-01` |

### DimPlan (3 records)

| Field | Inferred type | Example |
|---|---|---|
| `PlanID` | Text | `PL1` |
| `PlanName` | Text | `Starter` |
| `BaseMRR` | Number | `99` |

### FactSubscriptionMonthly (4,320 records)

| Field | Inferred type | Example |
|---|---|---|
| `CustomerID` | Text | `C0001` |
| `MonthStart` | Date (ISO) | `2024-01-01` |
| `StartingMRR` | Number | `0` |
| `EndingMRR` | Number | `99` |
| `NewMRR` | Number | `99` |
| `ExpansionMRR` | Number | `0` |
| `ContractionMRR` | Number | `0` |
| `ChurnMRR` | Number | `0` |
| `NewLogos` | Number | `1` |
| `ChurnedLogos` | Number | `0` |
| `ActiveBOM` | Number | `0` |
| `ActiveEOM` | Number | `1` |

### FactSupportTickets (630 records)

| Field | Inferred type | Example |
|---|---|---|
| `TicketID` | Text | `T00001` |
| `CustomerID` | Text | `C0001` |
| `OpenedDate` | Date (ISO) | `2024-02-07` |
| `Priority` | Text | `Medium` |
| `ResolutionHours` | Number | `18.0` |
| `CSAT` | Number | `5` |

## Data-quality policy
- Keys must be non-null and unique on each dimension/primary fact grain.
- Every foreign key in a fact must resolve to its dimension.
- Date-like CSV fields require explicit Date typing after import; do not leave as alphabetic text.
- Ratio measures must use DIVIDE and have meaningful blank/zero denominators.
- Validate baseline measures against metrics.json.
- Never report the values as real business data.

**Known interpretation risk:** Do not sum end-of-month MRR to measure current run-rate.
