# Data dictionary and data contracts

**Supply Chain & Inventory Optimization**

## Table grain
Customer orders: one order line. Inventory: one SKU x warehouse x month. Procurement: one purchase order.

## Tables and columns

### DimDate (365 records)

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

### DimSuppliers (32 records)

| Field | Inferred type | Example |
|---|---|---|
| `SupplierID` | Text | `S001` |
| `SupplierName` | Text | `Synthetic Supplier 001` |
| `SupplierRegion` | Text | `South` |
| `Tier` | Text | `Preferred` |

### DimProducts (90 records)

| Field | Inferred type | Example |
|---|---|---|
| `ProductID` | Text | `SKU0001` |
| `Category` | Text | `Office` |
| `SupplierID` | Text | `S005` |
| `UnitCost` | Number | `161.48` |
| `UnitPrice` | Number | `266.04` |

### DimWarehouses (4 records)

| Field | Inferred type | Example |
|---|---|---|
| `WarehouseID` | Text | `W1` |
| `WarehouseName` | Text | `North DC` |
| `City` | Text | `Delhi` |

### FactOrderLines (2,500 records)

| Field | Inferred type | Example |
|---|---|---|
| `OrderLineID` | Text | `OL00001` |
| `OrderDate` | Date (ISO) | `2025-05-18` |
| `ProductID` | Text | `SKU0017` |
| `WarehouseID` | Text | `W2` |
| `OrderedQty` | Number | `10` |
| `DeliveredQty` | Number | `10` |
| `ReturnedQty` | Number | `0` |
| `PromisedDate` | Date (ISO) | `2025-05-21` |
| `DeliveredDate` | Date (ISO) | `2025-05-20` |
| `OnTimeFlag` | Number | `1` |
| `OTIFFlag` | Number | `1` |
| `NetSales` | Number | `4674.9` |
| `CostOfGoodsSold` | Number | `2641.2` |
| `OrderStatus` | Text | `Delivered` |

### FactInventoryMonthly (4,320 records)

| Field | Inferred type | Example |
|---|---|---|
| `SnapshotMonth` | Date (ISO) | `2025-01-01` |
| `ProductID` | Text | `SKU0001` |
| `WarehouseID` | Text | `W1` |
| `OnHandQty` | Number | `64` |
| `InventoryValue` | Number | `10334.72` |
| `StockoutFlag` | Number | `0` |

### FactPurchaseOrders (430 records)

| Field | Inferred type | Example |
|---|---|---|
| `PurchaseOrderID` | Text | `PO00001` |
| `OrderDate` | Date (ISO) | `2025-05-12` |
| `SupplierID` | Text | `S005` |
| `ProductID` | Text | `SKU0001` |
| `WarehouseID` | Text | `W2` |
| `OrderedQty` | Number | `105` |
| `ReceivedQty` | Number | `105` |
| `PromisedReceiptDate` | Date (ISO) | `2025-05-19` |
| `ActualReceiptDate` | Date (ISO) | `2025-05-23` |
| `LeadTimeDays` | Number | `11` |
| `OnTimeReceiptFlag` | Number | `0` |

## Data-quality policy
- Keys must be non-null and unique on each dimension/primary fact grain.
- Every foreign key in a fact must resolve to its dimension.
- Date-like CSV fields require explicit Date typing after import; do not leave as alphabetic text.
- Ratio measures must use DIVIDE and have meaningful blank/zero denominators.
- Validate baseline measures against metrics.json.
- Never report the values as real business data.

**Known interpretation risk:** OTIF is measured per original order line; cancelled orders count as failures. Inventory turnover is a simplified proxy.
