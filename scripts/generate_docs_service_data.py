from pathlib import Path
from collections import defaultdict
from datetime import date,datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, ListFlowable, ListItem
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import csv,json,zipfile,shutil,math,textwrap
ROOT=Path(__file__).resolve().parents[1]
NAMES=['SaaS_Revenue_Churn_Intelligence','Banking_Credit_Risk_Intelligence','Healthcare_Operations_Intelligence','Supply_Chain_Inventory_Intelligence']

def load(n,t):
 with (ROOT/n/'data'/f'{t}.csv').open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def write(p,rs):
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,list(rs[0].keys()));w.writeheader();w.writerows(rs)
# Flat data for standalone CSV import in Power BI Service.
for n in NAMES:
 if n==NAMES[0]:
  cd={x['CustomerID']:x for x in load(n,'DimCustomer')};pd={x['PlanID']:x for x in load(n,'DimPlan')}; rows=[]
  for r in load(n,'FactSubscriptionMonthly'):
   c=cd[r['CustomerID']];p=pd[c['PlanID']]; rows.append({**r,'Segment':c['Segment'],'Industry':c['Industry'],'Region':c['Region'],'PlanName':p['PlanName'],'SignupMonth':c['SignupMonth']})
 elif n==NAMES[1]:
  customers={x['BorrowerID']:x for x in load(n,'DimBorrower')};pd={x['ProductID']:x for x in load(n,'DimProduct')}; rows=[]
  for r in load(n,'DimLoan'):
   b=customers[r['BorrowerID']];p=pd[r['ProductID']];rows.append({**r,'ProductName':p['ProductName'],'Region':b['Region'],'CreditScoreAtApplication':b['CreditScoreAtApplication'],'DebtToIncomeAtApplication':b['DebtToIncomeAtApplication'],'AgeBand':b['AgeBand']})
  wr=[{**x,'ProductName':pd[x['ProductID']]['ProductName'],'Region':customers[x['BorrowerID']]['Region']} for x in load(n,'FactApplications')]
  write(ROOT/n/'service_applications.csv',wr)
 elif n==NAMES[2]:
  p={x['PatientID']:x for x in load(n,'DimPatients')};d={x['DepartmentID']:x for x in load(n,'DimDepartments')};rows=[{**x,'DepartmentName':d[x['DepartmentID']]['DepartmentName'],'AgeBand':p[x['PatientID']]['AgeBand'],'PayerType':p[x['PatientID']]['PayerType']} for x in load(n,'FactEncounters')]
  write(ROOT/n/'service_capacity.csv',[{**x,'DepartmentName':d[x['DepartmentID']]['DepartmentName']} for x in load(n,'FactBedCapacityDaily')])
 else:
  products={x['ProductID']:x for x in load(n,'DimProducts')};warehouses={x['WarehouseID']:x for x in load(n,'DimWarehouses')};su={x['SupplierID']:x for x in load(n,'DimSuppliers')};rows=[]
  for x in load(n,'FactOrderLines'):
   p=products[x['ProductID']];rows.append({**x,'Category':p['Category'],'UnitCost':p['UnitCost'],'UnitPrice':p['UnitPrice'],'SupplierName':su[p['SupplierID']]['SupplierName'],'WarehouseName':warehouses[x['WarehouseID']]['WarehouseName']})
  write(ROOT/n/'service_inventory.csv',[{**x,'Category':products[x['ProductID']]['Category'],'WarehouseName':warehouses[x['WarehouseID']]['WarehouseName']} for x in load(n,'FactInventoryMonthly')])
 write(ROOT/n/'POWERBI_SERVICE_STARTER.csv',rows)
 # Replace misleading Excel references; native Power BI model still to author.
 p=ROOT/n/'README.md';s=p.read_text();s=s.replace('- `PowerBI_Import.xlsx`: same data arranged as named Excel tables for browser-based Power BI Service importing','- `POWERBI_SERVICE_STARTER.csv`: denormalized primary-fact CSV for a quick Power BI Service browser report (secondary flat CSVs provided when relevant)')
 s=s.replace('1. In Power BI Service go to **My workspace > New > Semantic model > Excel** and import `PowerBI_Import.xlsx`. Exact UI may vary by tenant/licence.','1. In Power BI Service go to **My workspace > New item > Semantic model > CSV** and import `POWERBI_SERVICE_STARTER.csv`. This creates a starter single-table model.')
 s=s.replace('2. In the semantic model, verify types, use `relationships.md` to set one-to-many model relationships and create measures from `measures.dax`. Some model-editor capabilities depend on access; Power BI Desktop on Windows is the most complete authoring workflow.','2. In the semantic model, verify dates/number types; build a basic one-table report using its fields. For the **advanced multi-table model** and all measures in `measures.dax`, import every file under `data/` using Power BI Desktop on Windows or a suitably provisioned Fabric data workflow, then create relationships from `relationships.md`. Web modelling features vary by license and workspace.')
 s=s.replace('3. Create a report and reproduce layouts in `dashboard_blueprint.md`.','3. Create a report and reproduce the applicable visuals in `dashboard_blueprint.md`. To replicate all 3 pages and multi-fact KPIs, use the advanced multi-table model.')
 s=s.replace('The import workbook contains actual Excel date values (not unparsed date strings), numeric measures, named tables and header formatting. In the model editor, verify Date, Whole Number, Decimal Number and currency/percentage measures after import.','The service starter is a CSV. In the model editor, explicitly change ISO date-text columns to Date, number columns to Whole/Decimal, and format DAX measures as currency or percentage as appropriate.')
 (ROOT/n/'README.md').write_text(s)
 # For single-table service starter, give corresponding DAX that works without other tables
 if n==NAMES[0]:dax='''-- All measures refer ONLY to POWERBI_SERVICE_STARTER (rename imported table to ServiceFact)\nMRR = VAR LastMonth = MAX(ServiceFact[MonthStart]) RETURN CALCULATE(SUM(ServiceFact[EndingMRR]),ServiceFact[MonthStart]=LastMonth)\nARR = [MRR] * 12\nActive Customers = VAR LastMonth = MAX(ServiceFact[MonthStart]) RETURN CALCULATE(SUM(ServiceFact[ActiveEOM]),ServiceFact[MonthStart]=LastMonth)\nLogo Churn % = DIVIDE(SUM(ServiceFact[ChurnedLogos]),SUM(ServiceFact[ActiveBOM]))\nNRR = DIVIDE(SUM(ServiceFact[StartingMRR])-SUM(ServiceFact[ChurnMRR])-SUM(ServiceFact[ContractionMRR])+SUM(ServiceFact[ExpansionMRR]),SUM(ServiceFact[StartingMRR]))\n'''
 elif n==NAMES[1]:dax='''Loan Count = COUNTROWS(ServiceFact)\nPrincipal Disbursed = SUM(ServiceFact[Principal])\nDefault Loan % = DIVIDE(CALCULATE(COUNTROWS(ServiceFact),ServiceFact[LoanStatusAsOf]="Default"),COUNTROWS(ServiceFact))\n30+ DPD Loans = CALCULATE(COUNTROWS(ServiceFact),ServiceFact[DaysPastDueAsOf]>=30)\n-- Approval rate requires service_applications.csv as a SEPARATE model, or the advanced multi-table model.\n'''
 elif n==NAMES[2]:dax='''Encounters = COUNTROWS(ServiceFact)\nAverage Stay Days = AVERAGE(ServiceFact[StayDays])\nAvg Wait Minutes = AVERAGE(ServiceFact[WaitingMinutes])\nReturn Visit % = DIVIDE(SUM(ServiceFact[ReturnWithin30Days]),COUNTROWS(ServiceFact))\nMargin = SUM(ServiceFact[CollectedRevenue])-SUM(ServiceFact[DirectCost])\n-- Occupancy requires service_capacity.csv as a separate model or the advanced multi-table model.\n'''
 else:dax='''Net Sales = SUM(ServiceFact[NetSales])\nOrder Lines = COUNTROWS(ServiceFact)\nOTIF % = DIVIDE(SUM(ServiceFact[OTIFFlag]),COUNTROWS(ServiceFact))\nFill Rate % = DIVIDE(SUM(ServiceFact[DeliveredQty]),SUM(ServiceFact[OrderedQty]))\nGross Margin = SUM(ServiceFact[NetSales])-SUM(ServiceFact[CostOfGoodsSold])\n-- Stockout snapshots require service_inventory.csv as a separate model or the advanced multi-table model.\n'''
 (ROOT/n/'service_starter_measures.dax').write_text(dax)
# fix notes where ambiguous schema directions
p=ROOT/NAMES[0]/'relationships.md';s=p.read_text().replace(' (filtering fact through customer; may need both-direction or denormalize PlanName into DimCustomer; recommended: merge DimPlan attributes into DimCustomer and remove separate DimPlan from final semantic model)',' (single-direction filters propagate plan -> customer -> subscription; do not enable bidirectional filtering)');p.write_text(s)
p=ROOT/NAMES[3]/'relationships.md';s=p.read_text().replace('DimSuppliers[SupplierID] 1 -> * FactPurchaseOrders[SupplierID] (avoid ambiguous supplier->product->purchase-order path; in production use supplier role-playing dim or drop direct active link)','DimSuppliers[SupplierID] -> FactPurchaseOrders[SupplierID] is NOT an active relationship because Supplier -> Product -> FactPurchaseOrders already provides a path. Do not create a second active route; use a role-playing supplier dimension only if direct PO supplier analysis needs it.');p.write_text(s)
p=ROOT/'README.md';s=p.read_text().replace('Import the named Excel tables in `PowerBI_Import.xlsx` into Power BI Service (Mac workflow) or `data/*.csv` into Desktop (Windows workflow).','Import each project\'s `POWERBI_SERVICE_STARTER.csv` in Power BI Service on Mac (single-table quick start); import all `data/*.csv` into Desktop on Windows for the full multi-table model.')
p.write_text(s)

# Audit-friendly validator, independent of this build script
validator='''#!/usr/bin/env python3\n"""Run: python validate_all.py. Uses only Python standard library."""\nfrom pathlib import Path\nfrom collections import defaultdict\nimport csv,json,sys,math\nROOT=Path(__file__).resolve().parent\nerrors=[]\ndef read(project,table):\n with (ROOT/project/'data'/f'{table}.csv').open(newline='',encoding='utf8') as fh:return list(csv.DictReader(fh))\ndef check_unique(p,t,key):\n rows=read(p,t);keys=[x[key] for x in rows]\n if len(keys)!=len(set(keys)):errors.append(f'{p} {t}: duplicate {key}')\n return set(keys)\ndef check_fk(p,ft,fk,dimkeys):\n miss=[v[fk] for v in read(p,ft) if v[fk] not in dimkeys]\n if miss:errors.append(f'{p} {ft}.{fk}: {len(miss)} missing keys')\ndef approx(p,title,actual,expected,tol=0.015):\n if abs(float(actual)-float(expected))>tol:errors.append(f'{p} {title} mismatch {actual} vs {expected}')\nP='SaaS_Revenue_Churn_Intelligence'; c=check_unique(P,'DimCustomer','CustomerID');check_fk(P,'FactSubscriptionMonthly','CustomerID',c);check_fk(P,'FactSupportTickets','CustomerID',c);check_unique(P,'FactSupportTickets','TicketID'); f=read(P,'FactSubscriptionMonthly'); months={(x['CustomerID'],x['MonthStart']) for x in f}\nif len(months)!=len(f):errors.append('SaaS duplicated customer-month grain')\nfor x in f:\n expected=float(x['StartingMRR'])+float(x['NewMRR'])+float(x['ExpansionMRR'])-float(x['ContractionMRR'])-float(x['ChurnMRR'])\n if abs(expected-float(x['EndingMRR']))>.02:errors.append('SaaS MRR bridge discrepancy');break\napprox(P,'Current MRR',sum(float(x['EndingMRR']) for x in f if x['MonthStart']=='2025-12-01'),json.loads((ROOT/P/'metrics.json').read_text())['kpis']['Current MRR'])\nP='Banking_Credit_Risk_Intelligence';b=check_unique(P,'DimBorrower','BorrowerID');a=check_unique(P,'FactApplications','ApplicationID');l=check_unique(P,'DimLoan','LoanID');check_fk(P,'DimLoan','ApplicationID',a);check_fk(P,'FactInstallments','LoanID',l);check_fk(P,'FactApplications','BorrowerID',b);check_unique(P,'FactInstallments','PaymentID')\nfor x in read(P,'FactInstallments'):\n if float(x['PaidAmount'])>float(x['DueAmount'])+.01 or float(x['PaidAmount'])<0:errors.append('Banking invalid installment paid');break\nP='Healthcare_Operations_Intelligence';pa=check_unique(P,'DimPatients','PatientID');doc=check_unique(P,'DimDoctors','DoctorID');dep=check_unique(P,'DimDepartments','DepartmentID');check_unique(P,'FactEncounters','EncounterID');check_fk(P,'FactEncounters','PatientID',pa);check_fk(P,'FactEncounters','DoctorID',doc);check_fk(P,'FactEncounters','DepartmentID',dep);check_fk(P,'FactBedCapacityDaily','DepartmentID',dep)\nfor x in read(P,'FactBedCapacityDaily'):\n if int(x['StaffedBeds'])!=int(x['OccupiedBeds'])+int(x['AvailableBeds']):errors.append('Healthcare beds do not reconcile');break\nP='Supply_Chain_Inventory_Intelligence'; sku=check_unique(P,'DimProducts','ProductID'); wh=check_unique(P,'DimWarehouses','WarehouseID');sup=check_unique(P,'DimSuppliers','SupplierID');check_unique(P,'FactOrderLines','OrderLineID');check_unique(P,'FactPurchaseOrders','PurchaseOrderID');check_fk(P,'FactOrderLines','ProductID',sku);check_fk(P,'FactInventoryMonthly','ProductID',sku);check_fk(P,'FactPurchaseOrders','SupplierID',sup);check_fk(P,'FactOrderLines','WarehouseID',wh)\nfor x in read(P,'FactOrderLines'):\n if int(x['DeliveredQty'])>int(x['OrderedQty']) or int(x['ReturnedQty'])>int(x['DeliveredQty']):errors.append('Supply qty invalid');break\n if int(x['OTIFFlag']) and (int(x['DeliveredQty'])!=int(x['OrderedQty']) or int(x['OnTimeFlag'])!=1):errors.append('Supply OTIF invalid');break\nprint('\\n'.join(errors) if errors else 'PASS: unique keys, foreign keys, reconciliation, grain and range tests')\nsys.exit(1 if errors else 0)\n'''
(ROOT/'validate_all.py').write_text(validator)

FONT_REG='Helvetica'
FONT_BOLD='Helvetica-Bold'
_font_dir=Path('/usr/share/fonts/truetype/dejavu')
if (_font_dir/'DejaVuSans.ttf').is_file() and (_font_dir/'DejaVuSans-Bold.ttf').is_file():
 pdfmetrics.registerFont(TTFont('DejaVu',str(_font_dir/'DejaVuSans.ttf')))
 pdfmetrics.registerFont(TTFont('DejaVu-Bold',str(_font_dir/'DejaVuSans-Bold.ttf')))
 FONT_REG='DejaVu'
 FONT_BOLD='DejaVu-Bold'
styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='BI_Title',fontName=FONT_BOLD,fontSize=22,leading=29,textColor=colors.HexColor('#0b2740'),spaceAfter=16));styles.add(ParagraphStyle(name='BI_Sub',fontName=FONT_BOLD,fontSize=12,leading=16,textColor=colors.HexColor('#086f94'),spaceBefore=14,spaceAfter=8));styles.add(ParagraphStyle(name='BI_Body',fontName=FONT_REG,fontSize=8.6,leading=14,spaceAfter=7,textColor=colors.HexColor('#23354a')));styles.add(ParagraphStyle(name='BI_Small',fontName=FONT_REG,fontSize=7.2,leading=11,textColor=colors.HexColor('#52677e')))
def p(txt,sty='BI_Body'):
 from xml.sax.saxutils import escape
 return Paragraph(escape(str(txt)),styles[sty])
def tbl(headers,rows,colwidths=None):
 vals=[[p(x,'BI_Small') for x in headers]]+[[p(x,'BI_Small') for x in row] for row in rows]
 table=Table(vals,colWidths=colwidths,repeatRows=1,hAlign='LEFT');table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dceefa')),('BACKGROUND',(0,1),(-1,-1),colors.HexColor('#f7fafc')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f3f8fd')]),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#d6e2eb')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]));return table

def decorate(can,doc):
 can.setStrokeColor(colors.HexColor('#d2e3ef'));can.line(42,42,552,42);can.setFont(FONT_REG,7);can.setFillColor(colors.HexColor('#638099'));can.drawString(43,29,'ORIGINAL POWER BI PORTFOLIO  |  SYNTHETIC DATA');can.drawRightString(552,29,f'{doc.page}')

def makepdf(out,blocks):
 doc=SimpleDocTemplate(str(out),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=47,bottomMargin=56);doc.build(blocks,onFirstPage=decorate,onLaterPages=decorate)

for i,n in enumerate(NAMES):
 m=json.loads((ROOT/n/'metrics.json').read_text());schema=json.loads((ROOT/n/'schema.json').read_text());title=m['title']
 story=[p('INDUSTRY INTELLIGENCE / 0'+str(i+1),'BI_Small'),p(title,'BI_Title'),p(m['problem'])]
 story+=[p('01  Business objectives & verified sample baseline','BI_Sub')]
 items=[]
 for k,v in m['kpis'].items():items.append([k,str(v)])
 story.append(tbl(['KPI','Sample synthetic baseline'],items,[253,255]));story.append(Spacer(1,12))
 story.append(p('02  Data sources and source grain','BI_Sub'))
 story.append(tbl(['Table','Rows','Example grain'],[[t,str(z['rows']),', '.join(f['name'] for f in z['fields'][:2])] for t,z in schema.items()],[200,55,253]))
 story.append(p('03  Recommended dashboard pages','BI_Sub'))
 for j,line in enumerate((ROOT/n/'dashboard_blueprint.md').read_text().split('### Page ')[1:],start=1):
  lines=line.splitlines();story.append(p('Page '+str(j)+': '+lines[0].replace(' - ',' / '),'BI_Body'))
  for l in lines[1:5]:
   if l.strip().startswith('-'):story.append(p('   '+l.strip()[2:],'BI_Small'))
 story.append(p('04  Build workflow on Mac and Windows','BI_Sub'))
 for s in ['Mac, fast starter: Power BI Service > New item > Semantic model > CSV > select POWERBI_SERVICE_STARTER.csv.','Use service_starter_measures.dax after renaming the imported table to ServiceFact; verify all inferred types.','Windows, advanced model: import every data/*.csv, apply relationships.md, then create measures individually from measures.dax.','Build the 3 report pages, validate against metrics.json, export PDF/screenshots and publish the actual Power BI report.']:
  story.append(p('• '+s,'BI_Body'))
 story.append(p('05  Data interpretation & interview notes','BI_Sub'))
 caveat={'SaaS_Revenue_Churn_Intelligence':'MRR is a point-in-time value. Summing monthly MRR is not the same as latest MRR. NRR/GRR use starting-MRR denominators.','Banking_Credit_Risk_Intelligence':'Deliquency/default status is an as-of snapshot, not a monthly historical status series; do not use it to claim validated prediction.','Healthcare_Operations_Intelligence':'30-day return flag is a descriptive proxy, not a risk-adjusted clinical readmission indicator; data are fully fictional.','Supply_Chain_Inventory_Intelligence':'OTIF denominator includes all order lines. Inventory turnover proxy is simplified and not a full accounting reconciliation.'}[n]
 for s in [caveat,'Explain grain, cardinality, numerator/denominator, filter context, edge cases, what actions stakeholders can take.','The HTML dashboard preview is a functional offline prototype; a .pbix or hosted Power BI report has not been authored or tested.']:
  story.append(p('• '+s,'BI_Body'))
 makepdf(ROOT/n/'project_brief.pdf',story)

manifest=json.loads((ROOT/'portfolio_manifest.json').read_text()); master=[p('COMPLETE PROJECT STARTER KIT','BI_Small'),p('Industry-Level Power BI Portfolio','BI_Title'),p('4 independently modelled industry case studies with synthetic data, DAX measure contracts, interactive offline prototypes and business documentation.')]
master.append(p('Reference-inspired, not copied','BI_Sub'));master.append(p('Inspiration: sachinkumar1609/PowerBI-Project GitHub repository. Its per-project organization contains screenshots, dataset files and in several cases .pbix and PDF assets. This kit follows that packaging spirit but uses new domains and entirely original generated data.'))
master.append(p('Project overview','BI_Sub'));master.append(tbl(['Project','Tables','Total rows'],[[x['title'],str(x['tables']),f"{x['rows']:,}"] for x in manifest],[340,70,98]));master.append(Spacer(1,16))
master.append(p('Fast build sequence','BI_Sub'))
for s in ['Open START_HERE.html and interact with the four offline design previews.','On Mac, import each project POWERBI_SERVICE_STARTER.csv into Power BI Service as a semantic model.','Create starter report cards, trend charts, top segment charts and filters.','To demonstrate advanced modelling, use Power BI Desktop on Windows and import full data/*.csv tables.','Add 3 pages and DAX measures, reconcile totals, capture report screenshots, export report PDF, then publish.', 'Push each project as an independent repository with original model screenshots, design decisions, data dictionary and an explicit synthetic-data disclaimer.']:
 master.append(p('• '+s))
master.append(p('Release readiness','BI_Sub'))
master.append(tbl(['Artifact','Status'],[['CSV star-schema tables','Included'],['CSV single-table Service starters','Included'],['DAX measures + dashboard pages','Included'],['HTML interactive offline dashboard previews','Included'],['PDF project briefs','Included'],['Native .pbix / .pbip reports','NOT INCLUDED; requires report authoring/QA in Power BI'],['Hosted Power BI URLs','NOT INCLUDED; requires publishing with suitable account/permissions']],[246,262]))
master.append(p('Power BI limitations','BI_Sub'));master.append(p('Power BI Desktop is Windows-only (Microsoft minimum requirements). The online Power BI Service can create reports from CSV semantic models; workspace licensing, model editing and sharing capabilities vary. For a multi-table data model, Desktop/Fabric authoring offers the clearest route.'))
master.append(p('Verification','BI_Sub'));master.append(p('Run python validate_all.py at the ZIP root. Follow per-project briefs and README files. Exact baseline numbers are in metrics.json. See official documentation: https://learn.microsoft.com/en-us/power-bi/create-reports/service-report-create-new and https://learn.microsoft.com/en-us/power-bi/connect-data/service-comma-separated-value-files.'))
makepdf(ROOT/'PORTFOLIO_MASTER_GUIDE.pdf',master)
print('Generated all starter CSVs, project PDFs, master PDF and validator.')
