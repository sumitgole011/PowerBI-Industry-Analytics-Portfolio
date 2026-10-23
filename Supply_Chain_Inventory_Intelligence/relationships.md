# Star-schema relationships

- DimProducts[ProductID] 1 -> * FactOrderLines[ProductID]
- DimProducts[ProductID] 1 -> * FactInventoryMonthly[ProductID]
- DimProducts[ProductID] 1 -> * FactPurchaseOrders[ProductID]
- DimSuppliers[SupplierID] 1 -> * DimProducts[SupplierID]
- DimSuppliers[SupplierID] -> FactPurchaseOrders[SupplierID] is NOT an active relationship because Supplier -> Product -> FactPurchaseOrders already provides a path. Do not create a second active route; use a role-playing supplier dimension only if direct PO supplier analysis needs it.
- DimWarehouses[WarehouseID] 1 -> * each Fact* WarehouseID
- DimDate[Date] 1 -> * FactOrderLines[OrderDate]
- DimDate[Date] 1 -> * FactInventoryMonthly[SnapshotMonth]
- DimDate[Date] 1 -> * FactPurchaseOrders[OrderDate]

Use one-to-many, single-direction cross filtering from dimension to fact unless otherwise indicated. Mark the daily date table as a date table using its Date field. Disable automatic date/time for a cleaner model. Date columns in secondary roles can use inactive relationships plus USERELATIONSHIP as required.
