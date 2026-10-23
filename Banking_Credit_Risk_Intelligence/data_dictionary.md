# Data dictionary and data contracts

**Banking Credit Risk & Loan Portfolio Intelligence**

## Table grain
Applications: one row per application. Loans: one row per approved loan. Installments: one row per due installment.

## Tables and columns

### DimDate (638 records)

| Field | Inferred type | Example |
|---|---|---|
| `Date` | Date (ISO) | `2025-01-01` |
| `Year` | Number | `2025` |
| `Quarter` | Text | `Q1` |
| `MonthNumber` | Number | `1` |
| `MonthName` | Text | `January` |
| `YearMonth` | Text | `2025-01` |
| `MonthStart` | Date (ISO) | `2025-01-01` |
| `DayOfWeek` | Text | `Wednesday` |

### DimBorrower (650 records)

| Field | Inferred type | Example |
|---|---|---|
| `BorrowerID` | Text | `B0001` |
| `AgeBand` | Text | `31-40` |
| `Region` | Text | `East` |
| `AnnualIncome` | Number | `72643.0` |
| `CreditScoreAtApplication` | Number | `755` |
| `DebtToIncomeAtApplication` | Number | `0.342` |

### DimProduct (4 records)

| Field | Inferred type | Example |
|---|---|---|
| `ProductID` | Text | `P1` |
| `ProductName` | Text | `Personal Loan` |

### FactApplications (650 records)

| Field | Inferred type | Example |
|---|---|---|
| `ApplicationID` | Text | `A0001` |
| `BorrowerID` | Text | `B0001` |
| `ProductID` | Text | `P3` |
| `ApplicationDate` | Date (ISO) | `2025-06-04` |
| `RequestedAmount` | Number | `36942.42` |
| `ApprovedFlag` | Number | `1` |
| `Decision` | Text | `Approved` |

### DimLoan (504 records)

| Field | Inferred type | Example |
|---|---|---|
| `LoanID` | Text | `L0001` |
| `ApplicationID` | Text | `A0001` |
| `BorrowerID` | Text | `B0001` |
| `ProductID` | Text | `P3` |
| `OriginationDate` | Date (ISO) | `2025-06-04` |
| `Principal` | Number | `30307.18` |
| `TermMonths` | Number | `24` |
| `APR` | Number | `0.245` |
| `InstallmentAmount` | Number | `1881.57` |
| `DaysPastDueAsOf` | Number | `0` |
| `LoanStatusAsOf` | Text | `Current` |
| `AsOfDate` | Date (ISO) | `2026-09-30` |

### FactInstallments (6,977 records)

| Field | Inferred type | Example |
|---|---|---|
| `PaymentID` | Text | `L0001-01` |
| `LoanID` | Text | `L0001` |
| `DueDate` | Date (ISO) | `2025-07-01` |
| `DueAmount` | Number | `1881.57` |
| `PaidAmount` | Number | `1881.57` |
| `UnpaidAmount` | Number | `0.0` |
| `InstallmentNumber` | Number | `1` |

## Data-quality policy
- Keys must be non-null and unique on each dimension/primary fact grain.
- Every foreign key in a fact must resolve to its dimension.
- Date-like CSV fields require explicit Date typing after import; do not leave as alphabetic text.
- Ratio measures must use DIVIDE and have meaningful blank/zero denominators.
- Validate baseline measures against metrics.json.
- Never report the values as real business data.

**Known interpretation risk:** Default and delinquency are fixed status as-of September 30, 2026. They must not be presented as historically known at origination.
