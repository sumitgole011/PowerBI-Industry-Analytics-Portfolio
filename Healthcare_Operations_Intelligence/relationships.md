# Star-schema relationships

- DimPatients[PatientID] 1 -> * FactEncounters[PatientID]
- DimDoctors[DoctorID] 1 -> * FactEncounters[DoctorID]
- DimDepartments[DepartmentID] 1 -> * FactEncounters[DepartmentID]
- DimDepartments[DepartmentID] 1 -> * FactBedCapacityDaily[DepartmentID]
- DimDate[Date] 1 -> * FactEncounters[AdmitDate]
- DimDate[Date] 1 -> * FactBedCapacityDaily[Date]
- DimDoctors[DepartmentID] points to DimDepartments but do NOT add this as an active bidirectional filtering path; department is already stored on encounters

Use one-to-many, single-direction cross filtering from dimension to fact unless otherwise indicated. Mark the daily date table as a date table using its Date field. Disable automatic date/time for a cleaner model. Date columns in secondary roles can use inactive relationships plus USERELATIONSHIP as required.
