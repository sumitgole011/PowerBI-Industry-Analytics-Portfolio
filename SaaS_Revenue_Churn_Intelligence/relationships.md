# Star-schema relationships

- DimCustomer[CustomerID] 1 -> * FactSubscriptionMonthly[CustomerID]
- DimCustomer[CustomerID] 1 -> * FactSupportTickets[CustomerID]
- DimPlan[PlanID] 1 -> * DimCustomer[PlanID] (single-direction filters propagate plan -> customer -> subscription; do not enable bidirectional filtering)
- DimDate[Date] 1 -> * FactSubscriptionMonthly[MonthStart]
- DimDate[Date] 1 -> * FactSupportTickets[OpenedDate]

Use one-to-many, single-direction cross filtering from dimension to fact unless otherwise indicated. Mark the daily date table as a date table using its Date field. Disable automatic date/time for a cleaner model. Date columns in secondary roles can use inactive relationships plus USERELATIONSHIP as required.
