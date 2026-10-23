from pathlib import Path
import csv, json, random, calendar, math, zipfile, textwrap, os
from collections import defaultdict, Counter
from datetime import date, timedelta

ROOT=Path(__file__).resolve().parents[1]
ROOT.mkdir(exist_ok=True)
random.seed(20261023)
NAMES=['SaaS_Revenue_Churn_Intelligence','Banking_Credit_Risk_Intelligence','Healthcare_Operations_Intelligence','Supply_Chain_Inventory_Intelligence']
COLORS=['#38bdf8','#a78bfa','#2dd4bf','#f59e0b']

def write_csv(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True)
 if not rows:return
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader();w.writerows(rows)
def dump(p,obj):p.write_text(json.dumps(obj,indent=2),encoding='utf-8')
def dstr(d):return d.isoformat()
def monthadd(d,k):
 y=d.year+(d.month-1+k)//12;m=(d.month-1+k)%12+1
 return date(y,m,min(d.day,calendar.monthrange(y,m)[1]))
def date_rows(start,end):
 rows=[]; d=start
 while d<=end:
  rows.append({'Date':dstr(d),'Year':d.year,'Quarter':f'Q{(d.month-1)//3+1}','MonthNumber':d.month,'MonthName':d.strftime('%B'),'YearMonth':d.strftime('%Y-%m'),'MonthStart':dstr(d.replace(day=1)),'DayOfWeek':d.strftime('%A')})
  d+=timedelta(days=1)
 return rows

def project(name,tables,meta,measures,relationships,insights,dashboard_pages):
 folder=ROOT/name; data=folder/'data'; data.mkdir(parents=True,exist_ok=True)
 for t,rs in tables.items():write_csv(data/(t+'.csv'),rs)
 schema={k:{'rows':len(rs),'fields':[{'name':c,'example':rs[0][c] if rs else ''} for c in rs[0]] if rs else []} for k,rs in tables.items()}
 dump(folder/'schema.json',schema)
 dump(folder/'metrics.json',meta)
 (folder/'measures.dax').write_text(measures,encoding='utf-8')
 (folder/'relationships.md').write_text('# Star-schema relationships\n\n'+'\n'.join('- '+r for r in relationships)+'\n\nUse one-to-many, single-direction cross filtering from dimension to fact unless otherwise indicated. Mark the daily date table as a date table using its Date field. Disable automatic date/time for a cleaner model. Date columns in secondary roles can use inactive relationships plus USERELATIONSHIP as required.\n',encoding='utf-8')
 details='\n'.join(f'### Page {i+1} - {p[0]}\n'+ '\n'.join('- '+v for v in p[1]) for i,p in enumerate(dashboard_pages))
 (folder/'dashboard_blueprint.md').write_text('# Power BI dashboard blueprint\n\n**Canvas:** 16:9, 1366 x 768; slate/navy backgrounds, accessible labels, consistent decimals and business units.\n\n'+details+'\n\n## Interactions\n- Page-level slicers: Year/Month, primary segment and one operational dimension.\n- Sync time slicers across pages and configure drill-through details.\n- Tooltip page: KPI definition, period, numerator and denominator.\n- Bookmark: Reset filters; navigation: Overview / Drivers / Details.\n- Test cross-filter direction, totals, no-data months, empty selections, and long segment names.\n',encoding='utf-8')
 readme=f'''# {meta['title']}\n\n> **Original synthetic-data Power BI case study**. All organizations, account IDs, financial outcomes and events are simulated. Not real customer/patient/credit data.\n\n## Business problem\n{meta['problem']}\n\n## Included artifacts\n- `data/*.csv`: source tables with explicit grains and stable surrogate IDs\n- `PowerBI_Import.xlsx`: same data arranged as named Excel tables for browser-based Power BI Service importing\n- `measures.dax`: analyst-reviewed starter measures (paste into Power BI as individual measures)\n- `relationships.md`: modelling and filter directions\n- `dashboard_blueprint.md`: wireframe-by-page, visuals and navigation\n- `dashboard_preview.html`: interactive standalone mock dashboard (NOT an actual .pbix or a published Power BI report)\n- `project_brief.pdf`: business questions, KPI contract, build steps and interview talking points\n- `metrics.json` and `schema.json`: reproducible QA inputs and metadata\n\n## Getting started on a Mac\n1. In Power BI Service go to **My workspace > New > Semantic model > Excel** and import `PowerBI_Import.xlsx`. Exact UI may vary by tenant/licence.\n2. In the semantic model, verify types, use `relationships.md` to set one-to-many model relationships and create measures from `measures.dax`. Some model-editor capabilities depend on access; Power BI Desktop on Windows is the most complete authoring workflow.\n3. Create a report and reproduce layouts in `dashboard_blueprint.md`.\n4. Export screenshots and PDF after validating totals; save a native `.pbix` / `.pbip` when using Power BI Desktop.\n\n## KPIs and sample baseline\n'''+ '\n'.join(f'- **{k}:** {v}' for k,v in meta['kpis'].items()) + '''\n\n## Decisions this project supports\n'''+ '\n'.join('- '+v for v in insights) + '''\n\n## Portfolio caution\nThe data has engineered patterns to support demonstration, so it is unsuitable for production forecasts, clinical decisions, lending decisions or real-world inferential claims. Native Power BI report files and Power BI-hosted links must be completed in Microsoft Power BI; the self-contained HTML is a functional design preview.\n'''
 (folder/'README.md').write_text(readme,encoding='utf-8')
 return folder

# 1 SaaS
r=random.Random(202601)
customers=[];plans=[{'PlanID':'PL1','PlanName':'Starter','BaseMRR':99},{'PlanID':'PL2','PlanName':'Growth','BaseMRR':299},{'PlanID':'PL3','PlanName':'Enterprise','BaseMRR':899}]
months=[date(2024+(i//12),i%12+1,1) for i in range(24)]
for i in range(180):
 start=r.randrange(0,22);pl=r.choices(plans,weights=[.48,.37,.15])[0];seg=r.choice(['SMB','Mid-Market','Enterprise']);ind=r.choice(['Technology','Professional Services','Education','Retail'])
 customers.append({'CustomerID':f'C{i+1:04d}','Company':f'Synthetic Account {i+1:04d}','Industry':ind,'Segment':seg,'Region':r.choice(['North America','Europe','APAC','India']),'PlanID':pl['PlanID'],'SignupMonth':dstr(months[start]),'_start':start,'_base':pl['BaseMRR']})
saas_fact=[];tickets=[];tid=0
for c in customers:
 base=c['_base'];start=c['_start'];active=False;mrr=0
 for i,m in enumerate(months):
  was=active;prev=mrr;new=exp=con=churn=0;nl=cl=0
  if i==start:
   active=True;mrr=base;new=mrr;nl=1
  elif was:
   hazard={'SMB':.024,'Mid-Market':.012,'Enterprise':.007}[c['Segment']]
   if r.random()<hazard:
    active=False;churn=prev;mrr=0;cl=1
   else:
    if r.random()<.095:exp=round(mrr*.15,2);mrr+=exp
    elif r.random()<.04:con=round(mrr*.08,2);mrr-=con
  saas_fact.append({'CustomerID':c['CustomerID'],'MonthStart':dstr(m),'StartingMRR':round(prev,2),'EndingMRR':round(mrr,2),'NewMRR':round(new,2),'ExpansionMRR':round(exp,2),'ContractionMRR':round(con,2),'ChurnMRR':round(churn,2),'NewLogos':nl,'ChurnedLogos':cl,'ActiveBOM':int(was),'ActiveEOM':int(active)})
  if active and r.random()<.22:
   for _ in range(r.choices([1,2,3],[.77,.2,.03])[0]):
    tid+=1; tdate=m+timedelta(days=r.randrange(0,calendar.monthrange(m.year,m.month)[1]));severity=r.choice(['Low','Medium','High'])
    tickets.append({'TicketID':f'T{tid:05d}','CustomerID':c['CustomerID'],'OpenedDate':dstr(tdate),'Priority':severity,'ResolutionHours':round(max(1,r.gauss(18 if severity!='High' else 8,8)),1),'CSAT':r.choice([3,4,4,5,5])})
for c in customers:del c['_start'];del c['_base']
saas={ 'DimDate':date_rows(date(2024,1,1),date(2025,12,31)),'DimCustomer':customers,'DimPlan':plans,'FactSubscriptionMonthly':saas_fact,'FactSupportTickets':tickets}
saas_kpi={'Current MRR':round(sum(x['EndingMRR'] for x in saas_fact if x['MonthStart']=='2025-12-01'),2),'Current Active Customers':sum(x['ActiveEOM'] for x in saas_fact if x['MonthStart']=='2025-12-01'),'Period Logo Churns':sum(x['ChurnedLogos'] for x in saas_fact),'Support Tickets':len(tickets)}
saas_dax='''-- Create ONE measure at a time in Power BI. MonthStart is the first day of a month.\nMRR =\nVAR _LastMonth = MAX ( FactSubscriptionMonthly[MonthStart] )\nRETURN CALCULATE ( SUM ( FactSubscriptionMonthly[EndingMRR] ), FactSubscriptionMonthly[MonthStart] = _LastMonth )\n\nARR = [MRR] * 12\n\nActive Customers =\nVAR _LastMonth = MAX ( FactSubscriptionMonthly[MonthStart] )\nRETURN CALCULATE ( SUM ( FactSubscriptionMonthly[ActiveEOM] ), FactSubscriptionMonthly[MonthStart] = _LastMonth )\n\nNew MRR = SUM ( FactSubscriptionMonthly[NewMRR] )\nExpansion MRR = SUM ( FactSubscriptionMonthly[ExpansionMRR] )\nContraction MRR = SUM ( FactSubscriptionMonthly[ContractionMRR] )\nChurned MRR = SUM ( FactSubscriptionMonthly[ChurnMRR] )\nNew Customers = SUM ( FactSubscriptionMonthly[NewLogos] )\nChurned Customers = SUM ( FactSubscriptionMonthly[ChurnedLogos] )\nLogo Churn Rate = DIVIDE ( [Churned Customers], SUM ( FactSubscriptionMonthly[ActiveBOM] ) )\nNet Revenue Retention =\nVAR _Base = SUM ( FactSubscriptionMonthly[StartingMRR] )\nRETURN DIVIDE ( _Base - [Churned MRR] - [Contraction MRR] + [Expansion MRR], _Base )\nGross Revenue Retention =\nVAR _Base = SUM ( FactSubscriptionMonthly[StartingMRR] )\nRETURN DIVIDE ( _Base - [Churned MRR] - [Contraction MRR], _Base )\nSupport Ticket Count = COUNTROWS ( FactSupportTickets )\nAvg Resolution Hours = AVERAGE ( FactSupportTickets[ResolutionHours] )\n'''
saas_rels=['DimCustomer[CustomerID] 1 -> * FactSubscriptionMonthly[CustomerID]','DimCustomer[CustomerID] 1 -> * FactSupportTickets[CustomerID]','DimPlan[PlanID] 1 -> * DimCustomer[PlanID] (filtering fact through customer; may need both-direction or denormalize PlanName into DimCustomer; recommended: merge DimPlan attributes into DimCustomer and remove separate DimPlan from final semantic model)','DimDate[Date] 1 -> * FactSubscriptionMonthly[MonthStart]','DimDate[Date] 1 -> * FactSupportTickets[OpenedDate]']
saas_pages=[('Executive overview',['Cards: MRR, ARR, Active Customers, Logo Churn Rate, NRR','Line chart: monthly MRR and customers','Waterfall: MRR bridge (start + new + expansion - contraction - churn)','Slicers: month, segment, industry, region']),('Retention and cohorts',['Cohort retention matrix by SignupMonth and reporting month (requires cohort calculation)','Trend: NRR vs GRR','Segment-level churn bars','Customer drill-through: account timeline']),('Customer support',['Tickets by priority and CSAT','Resolution SLA trend','Tickets vs churn correlation (descriptive only)'])]
folder=project(NAMES[0],saas,{'title':'SaaS Revenue & Customer Churn Intelligence','problem':'A B2B SaaS leadership team wants to understand recurring revenue expansion and customer retention. Avoid double-counting end-of-month MRR across selected months.','kpis':saas_kpi},saas_dax,saas_rels,['Investigate whether churn clusters in SMB accounts','Compare expansion MRR contribution against churned MRR','Prioritize support capacity where resolution times trend upward'],saas_pages)

# 2 Banking
r=random.Random(202602); applicants=[];apps=[];loans=[];payments=[]
products=[{'ProductID':'P1','ProductName':'Personal Loan'},{'ProductID':'P2','ProductName':'Auto Loan'},{'ProductID':'P3','ProductName':'Education Loan'},{'ProductID':'P4','ProductName':'SME Loan'}]
asof=date(2026,9,30)
for i in range(650):
 b=f'B{i+1:04d}';score=max(490,min(837,int(r.gauss(680,84))));dti=round(max(.06,min(.77,r.gauss(.36,.16))),3); income=round(r.uniform(33000,220000),0)
 applicants.append({'BorrowerID':b,'AgeBand':r.choice(['21-30','31-40','41-50','51-65']),'Region':r.choice(['North','South','East','West']),'AnnualIncome':income,'CreditScoreAtApplication':score,'DebtToIncomeAtApplication':dti})
 app_date=date(2025,1,1)+timedelta(days=r.randrange(0,365));pid=r.choice(products)['ProductID'];amount=round(r.uniform(3500,45000),2)
 approved=(r.random()<min(.96,max(.05,.82+(score-680)/460-(dti-.35)*.36)));aid=f'A{i+1:04d}'
 apps.append({'ApplicationID':aid,'BorrowerID':b,'ProductID':pid,'ApplicationDate':dstr(app_date),'RequestedAmount':amount,'ApprovedFlag':int(approved),'Decision':'Approved' if approved else 'Declined'})
 if not approved:continue
 lid=f'L{len(loans)+1:04d}';principal=round(amount*r.uniform(.82,1),2);term=r.choice([12,18,24,36]);apr=round(r.uniform(.08,.26),4);installment=round((principal*(1+apr*term/12))/term,2)
 first=monthadd(app_date.replace(day=1),1);rows=[];cur=first
 risk=max(.015,min(.26,.085+(640-score)/850+(dti-.35)*.28))
 will_default=r.random()<risk
 will_delinquent=(not will_default) and (r.random()<.075)
 due_dates=[]
 for j in range(term):
  due=monthadd(first,j)
  if due>asof:break
  due_dates.append(due)
 for j,due in enumerate(due_dates):
  # Recent unpaid installments produce the as-of DPD status; historical misses are
  # assumed cured on time for this simplified, deterministic synthetic case study.
  recent_idx=len(due_dates)-1-j
  if will_default and recent_idx<=3:
   paid=0.0
  elif will_delinquent and recent_idx<=1:
   paid=0.0
  else:
   paid=installment
  rows.append({'PaymentID':f'{lid}-{j+1:02d}','LoanID':lid,'DueDate':dstr(due),'DueAmount':installment,'PaidAmount':round(paid,2),'UnpaidAmount':round(installment-paid,2),'InstallmentNumber':j+1})
 unpaid=[x for x in rows if x['UnpaidAmount']>.01]
 dpd=max([ (asof-date.fromisoformat(x['DueDate'])).days for x in unpaid] or [0])
 status='Default' if dpd>=90 else ('Delinquent' if dpd>=30 else 'Current')
 loans.append({'LoanID':lid,'ApplicationID':aid,'BorrowerID':b,'ProductID':pid,'OriginationDate':dstr(app_date),'Principal':principal,'TermMonths':term,'APR':apr,'InstallmentAmount':installment,'DaysPastDueAsOf':dpd,'LoanStatusAsOf':status,'AsOfDate':dstr(asof)})
 payments.extend(rows)
bank={'DimDate':date_rows(date(2025,1,1),asof),'DimBorrower':applicants,'DimProduct':products,'FactApplications':apps,'DimLoan':loans,'FactInstallments':payments}
bank_kpi={'Applications':len(apps),'Approval Rate':round(sum(x['ApprovedFlag'] for x in apps)/len(apps)*100,2),'Disbursed Principal':round(sum(x['Principal'] for x in loans),2),'Defaulted Loans As Of 2026-09-30':sum(x['LoanStatusAsOf']=='Default' for x in loans)}
bank_dax='''-- DPD is a fixed AS-OF snapshot; do not treat the as-of status as historical at each application month.\nApplications = COUNTROWS ( FactApplications )\nApproved Applications = SUM ( FactApplications[ApprovedFlag] )\nApproval Rate = DIVIDE ( [Approved Applications], [Applications] )\nLoan Count = COUNTROWS ( DimLoan )\nDisbursed Principal = SUM ( DimLoan[Principal] )\nDefaulted Loans = CALCULATE ( [Loan Count], DimLoan[LoanStatusAsOf] = "Default" )\nDefault Rate by Count = DIVIDE ( [Defaulted Loans], [Loan Count] )\nDefaulted Original Principal = CALCULATE ( [Disbursed Principal], DimLoan[LoanStatusAsOf] = "Default" )\nAt Risk Loans 30+ DPD = CALCULATE ( [Loan Count], DimLoan[DaysPastDueAsOf] >= 30 )\nAt Risk Loan Share = DIVIDE ( [At Risk Loans 30+ DPD], [Loan Count] )\nInstallments Due = SUM ( FactInstallments[DueAmount] )\nInstallments Paid = SUM ( FactInstallments[PaidAmount] )\nCollection Rate = DIVIDE ( [Installments Paid], [Installments Due] )\n-- Do not label Defaulted Original Principal as expected credit loss.\n'''
bank_rels=['DimBorrower[BorrowerID] 1 -> * FactApplications[BorrowerID]','DimBorrower[BorrowerID] 1 -> * DimLoan[BorrowerID]','DimProduct[ProductID] 1 -> * FactApplications[ProductID]','DimProduct[ProductID] 1 -> * DimLoan[ProductID]','DimLoan[LoanID] 1 -> * FactInstallments[LoanID]','DimDate[Date] 1 -> * FactApplications[ApplicationDate]; for origination-based loan charts create a role-playing DimOriginationDate copy related to DimLoan[OriginationDate]','For installment date filtering, use separate DimDueDate copy related to FactInstallments[DueDate] to avoid ambiguous paths through DimLoan']
bank_pages=[('Credit portfolio overview',['Cards: Applications, Approval Rate, Disbursed Principal, Default Rate','Monthly originations and applications','Origination mix by product and region','Approval rate by credit score bands']),('Risk quality',['30+ DPD loan rate and 90+ DPD count','Risk matrix: DTI band x credit score band','Default status by original loan size','Important disclosure: status measured only at 2026-09-30']),('Collections',['Installments due vs paid by due month','Collection rate trend by product','Loan-level delinquency drill-through'])]
folder=project(NAMES[1],bank,{'title':'Banking Credit Risk & Loan Portfolio Intelligence','problem':'Credit portfolio managers need to track approval decisions, origination mix, delinquency and repayments without leaking future default outcomes into historical approval analysis.','kpis':bank_kpi},bank_dax,bank_rels,['Review 30+ day arrears and monitor collections','Locate product cohorts with deteriorating loan performance','Separate application approval metrics from as-of delinquency status'],bank_pages)

# 3 Healthcare
r=random.Random(202603)
depts=[{'DepartmentID':f'D{i+1}','DepartmentName':n,'StaffedBedBase':c} for i,(n,c) in enumerate([('Cardiology',40),('Orthopedics',32),('Neurology',30),('General Medicine',55),('Surgery',45),('Emergency',22)])]
patients=[{'PatientID':f'PT{i+1:04d}','AgeBand':r.choice(['0-17','18-34','35-49','50-64','65+']),'PayerType':r.choice(['Self Pay','Private Insurance','Public Insurance'])} for i in range(650)]
doctors=[{'DoctorID':f'DR{i+1:03d}','DepartmentID':depts[i%len(depts)]['DepartmentID'],'DoctorRole':'Consultant' if i%3 else 'Senior Consultant'} for i in range(30)]
encounters=[];by_patient=defaultdict(list)
for i in range(1800):
 patient=r.choice(patients);doc=r.choice(doctors);dep=next(d for d in depts if d['DepartmentID']==doc['DepartmentID']);start=date(2025,1,1)+timedelta(days=r.randrange(0,363));stay=r.randrange(1,10); end=min(date(2025,12,31),start+timedelta(days=stay-1))
 wait=max(0,int(r.gauss(54 if dep['DepartmentName']=='Emergency' else 29,21)));cost=round(r.uniform(800,4400)*stay,2);revenue=round(cost*r.uniform(.84,1.64),2)
 encounters.append({'EncounterID':f'E{i+1:05d}','PatientID':patient['PatientID'],'DoctorID':doc['DoctorID'],'DepartmentID':dep['DepartmentID'],'AdmitDate':dstr(start),'DischargeDate':dstr(end),'StayDays':(end-start).days+1,'VisitType':r.choice(['Elective','Urgent','Emergency']),'WaitingMinutes':wait,'DirectCost':cost,'CollectedRevenue':revenue,'ReturnWithin30Days':0})
for x in sorted(encounters,key=lambda z:z['AdmitDate']):
 p=x['PatientID']; a=date.fromisoformat(x['AdmitDate']);
 if by_patient[p]:
  prev=max(by_patient[p]);gap=(a-prev).days
  if 0<=gap<=30:x['ReturnWithin30Days']=1
 by_patient[p].append(date.fromisoformat(x['DischargeDate']))
capacity=[]
for d in date_rows(date(2025,1,1),date(2025,12,31)):
 for dep in depts:
  beds=dep['StaffedBedBase'] + r.randint(-3,3)
  cap=round(beds*r.uniform(.48,.97));capacity.append({'Date':d['Date'],'DepartmentID':dep['DepartmentID'],'StaffedBeds':beds,'OccupiedBeds':cap,'AvailableBeds':beds-cap})
hc={'DimDate':date_rows(date(2025,1,1),date(2025,12,31)),'DimPatients':patients,'DimDoctors':doctors,'DimDepartments':depts,'FactEncounters':encounters,'FactBedCapacityDaily':capacity}
hc_kpi={'Encounters':len(encounters),'Avg Length of Stay Days':round(sum(x['StayDays'] for x in encounters)/len(encounters),2),'Overall Occupancy %':round(sum(x['OccupiedBeds'] for x in capacity)/sum(x['StaffedBeds'] for x in capacity)*100,2),'30-day Return Visits':sum(x['ReturnWithin30Days'] for x in encounters)}
hc_dax='''-- All patient identifiers are synthetic. Return rate is NOT a clinical risk-adjusted readmission measure.\nEncounters = DISTINCTCOUNT ( FactEncounters[EncounterID] )\nPatients Seen = DISTINCTCOUNT ( FactEncounters[PatientID] )\nTotal Stay Days = SUM ( FactEncounters[StayDays] )\nAverage Length of Stay = DIVIDE ( [Total Stay Days], [Encounters] )\nAvg Wait Minutes = AVERAGE ( FactEncounters[WaitingMinutes] )\n30-Day Return Encounters = SUM ( FactEncounters[ReturnWithin30Days] )\n30-Day Return Visit Rate = DIVIDE ( [30-Day Return Encounters], [Encounters] )\nCollected Revenue = SUM ( FactEncounters[CollectedRevenue] )\nDirect Cost = SUM ( FactEncounters[DirectCost] )\nContribution Margin = [Collected Revenue] - [Direct Cost]\nContribution Margin % = DIVIDE ( [Contribution Margin], [Collected Revenue] )\nBed Occupancy Rate = DIVIDE ( SUM ( FactBedCapacityDaily[OccupiedBeds] ), SUM ( FactBedCapacityDaily[StaffedBeds] ) )\nAvailable Beds = SUM ( FactBedCapacityDaily[AvailableBeds] )\n'''
hc_rels=['DimPatients[PatientID] 1 -> * FactEncounters[PatientID]','DimDoctors[DoctorID] 1 -> * FactEncounters[DoctorID]','DimDepartments[DepartmentID] 1 -> * FactEncounters[DepartmentID]','DimDepartments[DepartmentID] 1 -> * FactBedCapacityDaily[DepartmentID]','DimDate[Date] 1 -> * FactEncounters[AdmitDate]','DimDate[Date] 1 -> * FactBedCapacityDaily[Date]','DimDoctors[DepartmentID] points to DimDepartments but do NOT add this as an active bidirectional filtering path; department is already stored on encounters']
hc_pages=[('Operations command center',['Cards: Encounters, ALOS, Occupancy, Avg Wait','Line chart: weekly encounters','Bed occupancy trend by department','Department heatmap of wait time']),('Patient experience',['Visit types and waiting times','30-day return visit rate by department','Patient counts by age band/payer (synthetic)']),('Unit economics',['Collected revenue vs direct cost','Contribution margin by department','Outlier drill-through: stay-days and cost'])]
folder=project(NAMES[2],hc,{'title':'Healthcare Operations & Hospital Performance','problem':'Hospital operations leaders need to improve patient throughput, staffed bed utilization and departmental contribution while protecting privacy and avoiding risk-adjusted medical claims.','kpis':hc_kpi},hc_dax,hc_rels,['Identify departments with higher wait times or utilization','Compare staffing capacity and activity by month','Explore department contribution and unusually long stays'],hc_pages)

# 4 Supply chain
r=random.Random(202604)
suppliers=[{'SupplierID':f'S{i+1:03d}','SupplierName':f'Synthetic Supplier {i+1:03d}','SupplierRegion':r.choice(['North','South','East','West']),'Tier':r.choice(['Strategic','Preferred','Standard'])} for i in range(32)]
products=[{'ProductID':f'SKU{i+1:04d}','Category':r.choice(['Electronics','Home','Industrial','Office','Apparel']),'SupplierID':r.choice(suppliers)['SupplierID'],'UnitCost':round(r.uniform(12,280),2),'UnitPrice':0} for i in range(90)]
for p in products:p['UnitPrice']=round(p['UnitCost']*r.uniform(1.25,1.85),2)
warehouses=[{'WarehouseID':f'W{i+1}','WarehouseName':v,'City':c} for i,(v,c) in enumerate([('North DC','Delhi'),('South DC','Bengaluru'),('West DC','Mumbai'),('East DC','Kolkata')])]
lines=[]
for i in range(2500):
 p=r.choice(products);w=r.choice(warehouses);orddate=date(2025,1,1)+timedelta(days=r.randrange(0,340)); qty=r.randint(1,17); promised=orddate+timedelta(days=r.randint(2,9));delay=r.randint(-2,4); delivered=promised+timedelta(days=delay);cancel=r.random()<.035
 actual=0 if cancel else (qty if r.random()<.89 else max(0,qty-r.randint(1,4)))
 ret=(r.randint(1,min(2,actual)) if actual and r.random()<.045 else 0)
 rev=round((actual-ret)*p['UnitPrice'],2);cogs=round((actual-ret)*p['UnitCost'],2)
 lines.append({'OrderLineID':f'OL{i+1:05d}','OrderDate':dstr(orddate),'ProductID':p['ProductID'],'WarehouseID':w['WarehouseID'],'OrderedQty':qty,'DeliveredQty':actual,'ReturnedQty':ret,'PromisedDate':dstr(promised),'DeliveredDate':dstr(delivered) if not cancel else '','OnTimeFlag':int(actual>0 and delivered<=promised),'OTIFFlag':int(not cancel and actual==qty and delivered<=promised),'NetSales':rev,'CostOfGoodsSold':cogs,'OrderStatus':'Cancelled' if cancel else 'Delivered'})
stock=[]
for m in [date(2025,i,1) for i in range(1,13)]:
 for p in products:
  for w in warehouses:
   qty= max(0,int(r.gauss(32 if p['Category']!='Industrial' else 19,22)))
   stock.append({'SnapshotMonth':dstr(m),'ProductID':p['ProductID'],'WarehouseID':w['WarehouseID'],'OnHandQty':qty,'InventoryValue':round(qty*p['UnitCost'],2),'StockoutFlag':int(qty==0)})
pos=[]
for i in range(430):
 p=r.choice(products);w=r.choice(warehouses);od=date(2025,1,1)+timedelta(days=r.randrange(0,332));due=od+timedelta(days=r.randint(5,16));received=due+timedelta(days=r.randint(-2,8)); qty=r.randint(15,125)
 pos.append({'PurchaseOrderID':f'PO{i+1:05d}','OrderDate':dstr(od),'SupplierID':p['SupplierID'],'ProductID':p['ProductID'],'WarehouseID':w['WarehouseID'],'OrderedQty':qty,'ReceivedQty':max(0,qty-r.choice([0,0,0,0,1,2,4])),'PromisedReceiptDate':dstr(due),'ActualReceiptDate':dstr(received),'LeadTimeDays':(received-od).days,'OnTimeReceiptFlag':int(received<=due)})
sc={'DimDate':date_rows(date(2025,1,1),date(2025,12,31)),'DimSuppliers':suppliers,'DimProducts':products,'DimWarehouses':warehouses,'FactOrderLines':lines,'FactInventoryMonthly':stock,'FactPurchaseOrders':pos}
sc_kpi={'Order Lines':len(lines),'Order-line OTIF %':round(sum(x['OTIFFlag'] for x in lines)/len(lines)*100,2),'Fulfillment Fill Rate %':round(sum(x['DeliveredQty'] for x in lines)/sum(x['OrderedQty'] for x in lines)*100,2),'Stockout Snapshot %':round(sum(x['StockoutFlag'] for x in stock)/len(stock)*100,2)}
sc_dax='''-- Revenue reflects units delivered less returns (simplified, excludes tax and shipping).\nOrder Lines = DISTINCTCOUNT ( FactOrderLines[OrderLineID] )\nOrdered Units = SUM ( FactOrderLines[OrderedQty] )\nDelivered Units = SUM ( FactOrderLines[DeliveredQty] )\nNet Sales = SUM ( FactOrderLines[NetSales] )\nCOGS = SUM ( FactOrderLines[CostOfGoodsSold] )\nGross Margin = [Net Sales] - [COGS]\nGross Margin % = DIVIDE ( [Gross Margin], [Net Sales] )\nOTIF Lines = SUM ( FactOrderLines[OTIFFlag] )\nOTIF Rate = DIVIDE ( [OTIF Lines], [Order Lines] )\nFill Rate = DIVIDE ( [Delivered Units], [Ordered Units] )\nStockout Snapshots = SUM ( FactInventoryMonthly[StockoutFlag] )\nStockout Rate = DIVIDE ( [Stockout Snapshots], COUNTROWS ( FactInventoryMonthly ) )\nAverage Monthly Inventory Value =\nAVERAGEX ( VALUES ( FactInventoryMonthly[SnapshotMonth] ), CALCULATE ( SUM ( FactInventoryMonthly[InventoryValue] ) ) )\nInventory Turnover Proxy = DIVIDE ( [COGS], [Average Monthly Inventory Value] )\nAvg Inbound Lead Time Days = AVERAGE ( FactPurchaseOrders[LeadTimeDays] )\nOn Time Supplier Receipt Rate = AVERAGE ( FactPurchaseOrders[OnTimeReceiptFlag] )\n-- Turnover is a simplified synthetic demonstration measure, not a full inventory accounting reconciliation.\n'''
sc_rels=['DimProducts[ProductID] 1 -> * FactOrderLines[ProductID]','DimProducts[ProductID] 1 -> * FactInventoryMonthly[ProductID]','DimProducts[ProductID] 1 -> * FactPurchaseOrders[ProductID]','DimSuppliers[SupplierID] 1 -> * DimProducts[SupplierID]','DimSuppliers[SupplierID] 1 -> * FactPurchaseOrders[SupplierID] (avoid ambiguous supplier->product->purchase-order path; in production use supplier role-playing dim or drop direct active link)','DimWarehouses[WarehouseID] 1 -> * each Fact* WarehouseID','DimDate[Date] 1 -> * FactOrderLines[OrderDate]','DimDate[Date] 1 -> * FactInventoryMonthly[SnapshotMonth]','DimDate[Date] 1 -> * FactPurchaseOrders[OrderDate]']
sc_pages=[('Fulfillment overview',['Cards: Net Sales, OTIF, Fill Rate, Gross Margin','Monthly shipped order lines and on-time rate','Warehouse ranking for OTIF and fill rate']),('Inventory health',['Monthly inventory value and turnover proxy','Stockout snapshot rate by warehouse/category','SKU drill-through with current snapshot inventory']),('Supplier scorecard',['Lead time and receipt reliability by supplier','Top late suppliers and regional distribution','Purchase order trend and detail table'])]
folder=project(NAMES[3],sc,{'title':'Supply Chain & Inventory Optimization','problem':'A multi-site distributor needs to increase on-time in-full delivery and eliminate stockouts without over-investing in stock.','kpis':sc_kpi},sc_dax,sc_rels,['Find warehouse/category combinations where order-level OTIF deteriorates','Review SKUs with repeated zero-stock snapshots','Investigate suppliers with longer purchase-order lead times'],sc_pages)

# summary, description, model and QA checks
summary=[]
for name in NAMES:
 path=ROOT/name;schema=json.loads((path/'schema.json').read_text());meta=json.loads((path/'metrics.json').read_text());summary.append({'project':name,'title':meta['title'],'tables':len(schema),'rows':sum(v['rows'] for v in schema.values()),'metrics':meta['kpis']})
dump(ROOT/'portfolio_manifest.json',summary)
(ROOT/'README.md').write_text('''# Industry-level Power BI Portfolio | 4 Original Case Studies\n\n**Inspired by:** https://github.com/sachinkumar1609/PowerBI-Project (presentation structure only). **No source files or dashboards were copied.**\n\nFour independent, original Power BI case studies, covering SaaS, Banking, Healthcare and Supply Chain. All source data are synthetically generated. The repository layout is GitHub-ready and designed to demonstrate data modelling, measure definitions, data quality, report UX and executive storytelling.\n\n## Four projects\n'''+ '\n'.join(f"{i+1}. **{x['title']}** - `{x['project']}/` ({x['tables']} tables; {x['rows']:,} total rows)" for i,x in enumerate(summary)) + '''\n\n## How to use this pack\n- Open each project's `dashboard_preview.html` locally in a web browser to interact with the **offline design prototype**. This is NOT a Power BI report.\n- Import the named Excel tables in `PowerBI_Import.xlsx` into Power BI Service (Mac workflow) or `data/*.csv` into Desktop (Windows workflow).\n- Create the relationships and add the measures according to the project documents.\n- Build the 3-page report for each project from `dashboard_blueprint.md`, then export screenshots and publish the actual `.pbix`/`.pbip` + PDF after acceptance testing.\n- Use `validate_all.py` to validate row counts, key uniqueness, foreign-key integrity, numeric reconciliations and high-level KPI contracts.\n\n## Scope & honesty\nThere are no authored or tested native `.pbix` files in this ZIP because Power BI Desktop requires Windows. The Excel/CSV data, local interactive HTML previews, project plans, DAX and PDFs are included and runnable/readable. The native Power BI report remains a manual authoring step in a supported environment.\n\n## Portfolio QA checklist\n- [ ] Raw files import without type errors\n- [ ] Relationship diagram has expected one-to-many cardinalities\n- [ ] DAX returns KPIs reconciled against `metrics.json` under default filters\n- [ ] Report slicers, drill-through, bookmarks and visual accessibility work\n- [ ] Screenshot/README/PDF/Power BI hosted report link added before public launch\n- [ ] Synthetic-data disclaimer retained\n\n## Power BI official references\n- https://learn.microsoft.com/en-us/power-bi/create-reports/service-report-create-new\n- https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop\n- https://learn.microsoft.com/power-bi/developer/projects/projects-overview\n''',encoding='utf-8')
print('Generated',len(summary),'projects',[(x['project'],x['rows']) for x in summary]);
