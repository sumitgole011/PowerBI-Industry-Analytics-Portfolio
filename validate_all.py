#!/usr/bin/env python3
"""Run: python validate_all.py. Uses only Python standard library."""
from pathlib import Path
from collections import defaultdict
import csv,json,sys,math
ROOT=Path(__file__).resolve().parent
errors=[]
def read(project,table):
 with (ROOT/project/'data'/f'{table}.csv').open(newline='',encoding='utf8') as fh:return list(csv.DictReader(fh))
def check_unique(p,t,key):
 rows=read(p,t);keys=[x[key] for x in rows]
 if len(keys)!=len(set(keys)):errors.append(f'{p} {t}: duplicate {key}')
 return set(keys)
def check_fk(p,ft,fk,dimkeys):
 miss=[v[fk] for v in read(p,ft) if v[fk] not in dimkeys]
 if miss:errors.append(f'{p} {ft}.{fk}: {len(miss)} missing keys')
def approx(p,title,actual,expected,tol=0.015):
 if abs(float(actual)-float(expected))>tol:errors.append(f'{p} {title} mismatch {actual} vs {expected}')
P='SaaS_Revenue_Churn_Intelligence'; c=check_unique(P,'DimCustomer','CustomerID');check_fk(P,'FactSubscriptionMonthly','CustomerID',c);check_fk(P,'FactSupportTickets','CustomerID',c);check_unique(P,'FactSupportTickets','TicketID'); f=read(P,'FactSubscriptionMonthly'); months={(x['CustomerID'],x['MonthStart']) for x in f}
if len(months)!=len(f):errors.append('SaaS duplicated customer-month grain')
for x in f:
 expected=float(x['StartingMRR'])+float(x['NewMRR'])+float(x['ExpansionMRR'])-float(x['ContractionMRR'])-float(x['ChurnMRR'])
 if abs(expected-float(x['EndingMRR']))>.02:errors.append('SaaS MRR bridge discrepancy');break
approx(P,'Current MRR',sum(float(x['EndingMRR']) for x in f if x['MonthStart']=='2025-12-01'),json.loads((ROOT/P/'metrics.json').read_text())['kpis']['Current MRR'])
P='Banking_Credit_Risk_Intelligence';b=check_unique(P,'DimBorrower','BorrowerID');a=check_unique(P,'FactApplications','ApplicationID');l=check_unique(P,'DimLoan','LoanID');check_fk(P,'DimLoan','ApplicationID',a);check_fk(P,'FactInstallments','LoanID',l);check_fk(P,'FactApplications','BorrowerID',b);check_unique(P,'FactInstallments','PaymentID')
for x in read(P,'FactInstallments'):
 if float(x['PaidAmount'])>float(x['DueAmount'])+.01 or float(x['PaidAmount'])<0:errors.append('Banking invalid installment paid');break
P='Healthcare_Operations_Intelligence';pa=check_unique(P,'DimPatients','PatientID');doc=check_unique(P,'DimDoctors','DoctorID');dep=check_unique(P,'DimDepartments','DepartmentID');check_unique(P,'FactEncounters','EncounterID');check_fk(P,'FactEncounters','PatientID',pa);check_fk(P,'FactEncounters','DoctorID',doc);check_fk(P,'FactEncounters','DepartmentID',dep);check_fk(P,'FactBedCapacityDaily','DepartmentID',dep)
for x in read(P,'FactBedCapacityDaily'):
 if int(x['StaffedBeds'])!=int(x['OccupiedBeds'])+int(x['AvailableBeds']):errors.append('Healthcare beds do not reconcile');break
P='Supply_Chain_Inventory_Intelligence'; sku=check_unique(P,'DimProducts','ProductID'); wh=check_unique(P,'DimWarehouses','WarehouseID');sup=check_unique(P,'DimSuppliers','SupplierID');check_unique(P,'FactOrderLines','OrderLineID');check_unique(P,'FactPurchaseOrders','PurchaseOrderID');check_fk(P,'FactOrderLines','ProductID',sku);check_fk(P,'FactInventoryMonthly','ProductID',sku);check_fk(P,'FactPurchaseOrders','SupplierID',sup);check_fk(P,'FactOrderLines','WarehouseID',wh)
for x in read(P,'FactOrderLines'):
 if int(x['DeliveredQty'])>int(x['OrderedQty']) or int(x['ReturnedQty'])>int(x['DeliveredQty']):errors.append('Supply qty invalid');break
 if int(x['OTIFFlag']) and (int(x['DeliveredQty'])!=int(x['OrderedQty']) or int(x['OnTimeFlag'])!=1):errors.append('Supply OTIF invalid');break
print('\n'.join(errors) if errors else 'PASS: unique keys, foreign keys, reconciliation, grain and range tests')
sys.exit(1 if errors else 0)
