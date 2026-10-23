# Data dictionary and data contracts

**Healthcare Operations & Hospital Performance**

## Table grain
Encounters: one admission encounter. Capacity: one department per calendar day.

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

### DimPatients (650 records)

| Field | Inferred type | Example |
|---|---|---|
| `PatientID` | Text | `PT0001` |
| `AgeBand` | Text | `0-17` |
| `PayerType` | Text | `Public Insurance` |

### DimDoctors (30 records)

| Field | Inferred type | Example |
|---|---|---|
| `DoctorID` | Text | `DR001` |
| `DepartmentID` | Text | `D1` |
| `DoctorRole` | Text | `Senior Consultant` |

### DimDepartments (6 records)

| Field | Inferred type | Example |
|---|---|---|
| `DepartmentID` | Text | `D1` |
| `DepartmentName` | Text | `Cardiology` |
| `StaffedBedBase` | Number | `40` |

### FactEncounters (1,800 records)

| Field | Inferred type | Example |
|---|---|---|
| `EncounterID` | Text | `E00001` |
| `PatientID` | Text | `PT0161` |
| `DoctorID` | Text | `DR023` |
| `DepartmentID` | Text | `D5` |
| `AdmitDate` | Date (ISO) | `2025-01-11` |
| `DischargeDate` | Date (ISO) | `2025-01-14` |
| `StayDays` | Number | `4` |
| `VisitType` | Text | `Elective` |
| `WaitingMinutes` | Number | `47` |
| `DirectCost` | Number | `13079.86` |
| `CollectedRevenue` | Number | `19126.0` |
| `ReturnWithin30Days` | Number | `0` |

### FactBedCapacityDaily (2,190 records)

| Field | Inferred type | Example |
|---|---|---|
| `Date` | Date (ISO) | `2025-01-01` |
| `DepartmentID` | Text | `D1` |
| `StaffedBeds` | Number | `40` |
| `OccupiedBeds` | Number | `36` |
| `AvailableBeds` | Number | `4` |

## Data-quality policy
- Keys must be non-null and unique on each dimension/primary fact grain.
- Every foreign key in a fact must resolve to its dimension.
- Date-like CSV fields require explicit Date typing after import; do not leave as alphabetic text.
- Ratio measures must use DIVIDE and have meaningful blank/zero denominators.
- Validate baseline measures against metrics.json.
- Never report the values as real business data.

**Known interpretation risk:** 30-day return visit rate is a simple descriptive proxy, not a medically validated readmission rate.
