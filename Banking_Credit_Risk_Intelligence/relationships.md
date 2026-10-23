# Star-schema relationships

- DimBorrower[BorrowerID] 1 -> * FactApplications[BorrowerID]
- DimBorrower[BorrowerID] 1 -> * DimLoan[BorrowerID]
- DimProduct[ProductID] 1 -> * FactApplications[ProductID]
- DimProduct[ProductID] 1 -> * DimLoan[ProductID]
- DimLoan[LoanID] 1 -> * FactInstallments[LoanID]
- DimDate[Date] 1 -> * FactApplications[ApplicationDate]; for origination-based loan charts create a role-playing DimOriginationDate copy related to DimLoan[OriginationDate]
- For installment date filtering, use separate DimDueDate copy related to FactInstallments[DueDate] to avoid ambiguous paths through DimLoan

Use one-to-many, single-direction cross filtering from dimension to fact unless otherwise indicated. Mark the daily date table as a date table using its Date field. Disable automatic date/time for a cleaner model. Date columns in secondary roles can use inactive relationships plus USERELATIONSHIP as required.
