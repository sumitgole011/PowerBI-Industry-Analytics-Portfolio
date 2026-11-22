from pathlib import Path
from collections import defaultdict
from datetime import datetime
import csv,json,html,subprocess,shutil
ROOT=Path(__file__).resolve().parents[1]
NAMES=['SaaS_Revenue_Churn_Intelligence','Banking_Credit_Risk_Intelligence','Healthcare_Operations_Intelligence','Supply_Chain_Inventory_Intelligence']
COLORS=['#38bdf8','#a78bfa','#2dd4bf','#f59e0b']

def read(name,table):
 with (ROOT/name/'data'/f'{table}.csv').open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def add(G,month,cat,vals):
 g=G[(month,cat)];g['month']=month;g['cat']=cat
 for k,v in vals.items():g[k]=g.get(k,0)+float(v)
def grouped(name):
 G=defaultdict(dict); cats=[]
 if name==NAMES[0]:
  c={v['CustomerID']:v['Segment'] for v in read(name,'DimCustomer')};cats=['SMB','Mid-Market','Enterprise']
  for x in read(name,'FactSubscriptionMonthly'):
   add(G,x['MonthStart'][:7],c[x['CustomerID']],{k:x[k] for k in ['StartingMRR','EndingMRR','NewMRR','ExpansionMRR','ContractionMRR','ChurnMRR','NewLogos','ChurnedLogos','ActiveBOM','ActiveEOM']})
  spec={'label':'Customer segment','metric':'EndingMRR','trend':'Monthly recurring revenue','unit':'$','barMode':'latest','cards':[['Month-end MRR','latest','EndingMRR','$'],['Annualized run rate','latest12','EndingMRR','$'],['Logo churn rate','ratio','ChurnedLogos/ActiveBOM','%'],['Net revenue retention','nrr','','%']]}
 elif name==NAMES[1]:
  pd={x['ProductID']:x['ProductName'] for x in read(name,'DimProduct')};cats=list(pd.values());a={x['ApplicationID']:x for x in read(name,'FactApplications')};loans=read(name,'DimLoan'); loanapps=defaultdict(list)
  for loan in loans:loanapps[loan['ApplicationID']].append(loan)
  for x in a.values():
   loan=loanapps.get(x['ApplicationID'],[]);add(G,x['ApplicationDate'][:7],pd[x['ProductID']],{'Apps':1,'Approvals':x['ApprovedFlag'],'Loans':len(loan),'Principal':sum(float(v['Principal']) for v in loan),'Defaults':sum(v['LoanStatusAsOf']=='Default' for v in loan),'DPD30':sum(int(v['DaysPastDueAsOf'])>=30 for v in loan)})
  spec={'label':'Loan product','metric':'Principal','trend':'Originated principal by month','unit':'$','cards':[['Loan applications','sum','Apps',''],['Approval rate','ratio','Approvals/Apps','%'],['Originated principal','sum','Principal','$'],['Default rate as of Sep 2026','ratio','Defaults/Loans','%']]}
 elif name==NAMES[2]:
  dp={x['DepartmentID']:x['DepartmentName'] for x in read(name,'DimDepartments')};cats=list(dp.values())
  for x in read(name,'FactEncounters'):
   add(G,x['AdmitDate'][:7],dp[x['DepartmentID']],{'Encounters':1,'Stay':x['StayDays'],'Wait':x['WaitingMinutes'],'Revenue':x['CollectedRevenue'],'Cost':x['DirectCost'],'Returns':x['ReturnWithin30Days']})
  for x in read(name,'FactBedCapacityDaily'):
   add(G,x['Date'][:7],dp[x['DepartmentID']],{'Occupied':x['OccupiedBeds'],'Staffed':x['StaffedBeds']})
  spec={'label':'Department','metric':'Encounters','trend':'Encounters by month','unit':'','cards':[['Patient encounters','sum','Encounters',''],['Bed occupancy','ratio','Occupied/Staffed','%'],['Average length of stay','ratio','Stay/Encounters',' days'],['30-day return visits','ratio','Returns/Encounters','%']]}
 else:
  pd={x['ProductID']:x['Category'] for x in read(name,'DimProducts')};cats=['Electronics','Home','Industrial','Office','Apparel']
  for x in read(name,'FactOrderLines'):
   add(G,x['OrderDate'][:7],pd[x['ProductID']],{'OrderLines':1,'NetSales':x['NetSales'],'COGS':x['CostOfGoodsSold'],'OTIF':x['OTIFFlag'],'Ordered':x['OrderedQty'],'Delivered':x['DeliveredQty']})
  for x in read(name,'FactInventoryMonthly'):
   add(G,x['SnapshotMonth'][:7],pd[x['ProductID']],{'Stockouts':x['StockoutFlag'],'Snapshots':1,'InventoryValue':x['InventoryValue']})
  spec={'label':'Product category','metric':'NetSales','trend':'Net sales by month','unit':'$','cards':[['Net sales','sum','NetSales','$'],['Order-line OTIF','ratio','OTIF/OrderLines','%'],['Unit fill rate','ratio','Delivered/Ordered','%'],['Stockout snapshots','ratio','Stockouts/Snapshots','%']]}
 return list(G.values()),cats,spec

TEMPLATE=r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{{TITLE}} - BI dashboard preview</title><style>
:root{--bg:#07111e;--panel:#0e1c2c;--muted:#93a4b8;--line:#223349;--accent:{{ACCENT}};--txt:#eff6fc}*{box-sizing:border-box}body{background:radial-gradient(circle at 90% -15%,#133151,transparent 40%),var(--bg);color:var(--txt);font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:0} .app{max-width:1440px;margin:auto;padding:26px 30px 48px}header{display:flex;align-items:center;justify-content:space-between;margin-bottom:25px;gap:15px}.brand{letter-spacing:2px;color:var(--accent);font-size:12px;font-weight:700}.title{font-size:29px;font-weight:750;margin:8px 0 3px}.sub{color:var(--muted);font-size:13px} .pill{border:1px solid #295066;background:#10293b;border-radius:99px;font-size:11px;color:#abd4f2;padding:8px 12px}.filters{display:flex;flex-wrap:wrap;gap:13px;margin:17px 0 23px}.filter{border:1px solid var(--line);border-radius:10px;background:#102032;padding:11px 15px;min-width:230px}label{font-size:11px;color:var(--muted);display:block;letter-spacing:.6px;text-transform:uppercase;margin-bottom:5px}select{width:100%;background:transparent;border:0;outline:none;color:#fff;font-size:14px;cursor:pointer}option{background:#14283b} .kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}.kpi{background:linear-gradient(160deg,#14273b,#0b1a2b);border:1px solid #1c3548;padding:19px 22px;border-radius:13px;min-height:121px}.kpi .value{font-size:28px;font-weight:750;margin-top:13px;letter-spacing:-1px}.kpi .mini{font-size:11px;color:#99aec5;margin-top:8px}.layout{display:grid;grid-template-columns:1.65fr 1fr;gap:14px;margin-top:16px}.panel{border-radius:14px;background:linear-gradient(165deg,#102032,#0b1725);border:1px solid #1f3448;padding:19px;min-width:0}.panel h3{font-weight:650;margin:1px 0 4px;font-size:16px}.panel p{color:var(--muted);margin:0;font-size:12px}.chart{height:260px;margin-top:17px}.legend{font-size:11px;color:var(--muted);margin-top:8px}.second{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px}table{width:100%;border-collapse:collapse;font-size:12px;margin-top:18px}th{text-align:left;font-size:11px;text-transform:uppercase;color:#8da2b8;font-weight:550;padding-bottom:12px}td{padding:11px 0;border-top:1px solid #20354a}td:last-child,th:last-child{text-align:right}footer{margin-top:27px;color:#7891a9;font-size:11px;line-height:1.7} @media(max-width:900px){.kpis{grid-template-columns:repeat(2,1fr)}.layout,.second{grid-template-columns:1fr}} @media(max-width:500px){.app{padding:17px}.title{font-size:23px}.kpis{grid-template-columns:1fr}.pill{display:none}}
</style></head><body><div class="app"><header><div><div class="brand">NOVA / ANALYTICS LAB&nbsp; • &nbsp;POWER BI PORTFOLIO</div><div class="title">{{TITLE}}</div><div class="sub">Executive intelligence workspace / portfolio design prototype</div></div><span class="pill">● INTERACTIVE OFFLINE PREVIEW</span></header><div class="filters"><div class="filter"><label>Reporting period</label><select id="period"><option value="all">All available data</option><option value="2024">2024</option><option value="2025">2025</option><option value="2026">2026</option><option value="2025-Q1">2025 · Q1</option><option value="2025-Q2">2025 · Q2</option><option value="2025-Q3">2025 · Q3</option><option value="2025-Q4">2025 · Q4</option></select></div><div class="filter"><label>{{CATEGORY}}</label><select id="cat"></select></div></div><section class="kpis" id="kpis"></section><section class="layout"><div class="panel"><h3>{{TREND}}</h3><p>Actuals derived from synthetic transactions • filtered by selection</p><div class="chart" id="lineChart"></div><div class="legend">Monthly performance · hover each point for exact numbers</div></div><div class="panel"><h3>Performance by {{CATEGORY}}</h3><p>{{BAR_DESC}}</p><div class="chart" id="barChart"></div><div class="legend">Categories remain comparable under period filter</div></div></section><section class="second"><div class="panel"><h3>Monthly breakdown</h3><p>Most recent five available months</p><table><thead><tr><th>Month</th><th>{{METRIC}}</th></tr></thead><tbody id="monthly"></tbody></table></div><div class="panel"><h3>Business narrative</h3><p>Executive handoff / technical notes</p><div style="font-size:13px;line-height:1.85;color:#bed0df;margin-top:16px">{{NARRATIVE}}</div></div></section><footer>LOCAL DESIGN PROTOTYPE ONLY · Not authored or published in Microsoft Power BI · Synthetic data • See source CSVs, model relationships, DAX measures and project brief to implement the report in Power BI.</footer></div>
<script>const DATA={{DATA}}; const CATS={{CATS}}; const SPEC={{SPEC}};const ACCENT='{{ACCENT}}';
const el=id=>document.getElementById(id);const comma=n=>Math.round(n).toLocaleString('en-US');const money=n=>'$'+Math.round(n).toLocaleString('en-US');const percent=n=>(n*100).toFixed(1)+'%';const fmt=(n,unit)=>unit==='$'?money(n):unit==='%'?percent(n):unit===' days'?n.toFixed(1)+' days':comma(n);
function matchPeriod(m,period){if(period==='all')return true; if(period.includes('-Q')){const yr=period.slice(0,4),q=Number(period.at(-1)),mn=Number(m.slice(5,7));return m.startsWith(yr) && Math.ceil(mn/3)===q;}return m.startsWith(period)}
function subset(){let p=el('period').value,c=el('cat').value;return DATA.filter(r=>matchPeriod(r.month,p)&&(c==='all'||c===r.cat));}
function totals(rows){let o={}; for(let r of rows)for(let[k,v]of Object.entries(r)){if(k!=='month'&&k!=='cat')o[k]=(o[k]||0)+v;}return o;}
function value(rows,type,field){if(type==='latest'||type==='latest12'){let last=[...new Set(rows.map(r=>r.month))].sort().at(-1);let n=totals(rows.filter(r=>r.month===last))[field]||0;return type==='latest12'?n*12:n;}let s=totals(rows);if(type==='sum')return s[field]||0;if(type==='ratio'){let[a,b]=field.split('/');return(s[b]||0)?(s[a]||0)/s[b]:0;}if(type==='nrr')return(s.StartingMRR||0)?((s.StartingMRR||0)-(s.ChurnMRR||0)-(s.ContractionMRR||0)+(s.ExpansionMRR||0))/s.StartingMRR:0;return 0}
function monthSeries(rows){let m={}; for(let r of rows){if(!m[r.month])m[r.month]=0;m[r.month]+=r[SPEC.metric]||0;}return Object.entries(m).sort((a,b)=>a[0].localeCompare(b[0])).map(([x,y])=>({x,y}));}
function escapeHTML(x){return String(x).replace(/[&<>"]/g,k=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[k]));}
function lineChart(points){if(!points.length)return'<p>No data for this selection.</p>';const W=850,H=248,left=55,right=25,top=20,bottom=35,max=Math.max(1,...points.map(p=>p.y))*1.16;let coords=points.map((p,i)=>({...p,value:p.y,x:left+(W-left-right)*(points.length===1?.5:i/(points.length-1)),y:top+(H-top-bottom)*(1-p.y/max)}));let grid=[0,.25,.5,.75,1].map(q=>{let y=top+(H-top-bottom)*(1-q);return `<line x1="${left}" y1="${y}" x2="${W-right}" y2="${y}" stroke="#264159" stroke-dasharray="4 5"/><text x="${left-10}" y="${y+4}" fill="#88a1b9" text-anchor="end" font-size="12">${Math.round(max*q).toLocaleString('en-US')}</text>`}).join('');let xlabels=coords.filter((p,i)=>i%Math.max(1,Math.ceil(coords.length/6))===0||i===coords.length-1).map(p=>`<text x="${p.x}" y="${H-10}" font-size="12" text-anchor="middle" fill="#93a4b8">${p.x===undefined?'':p.xlbl||p.x}</text>`).join('');let area=`${left},${H-bottom} `+coords.map(p=>`${p.x},${p.y}`).join(' ')+` ${coords.at(-1).x},${H-bottom}`;let circles=coords.map(p=>`<circle cx="${p.x}" cy="${p.y}" r="4" fill="${ACCENT}" stroke="#0c2234" stroke-width="2"><title>${p.xlbl||p.x}: ${fmt(p.value,SPEC.unit)}</title></circle>`).join('');let months=coords.filter((p,i)=>i%Math.max(1,Math.ceil(coords.length/7))===0||i===coords.length-1).map(p=>`<text x="${p.x}" y="${H-8}" font-size="12" text-anchor="middle" fill="#93a4b8">${p.xdate.slice(2)}</text>`).join('');return `<svg viewBox="0 0 ${W} ${H}" style="width:100%;height:100%" role="img" aria-label="Monthly ${SPEC.trend}">${grid}<polygon points="${area}" fill="${ACCENT}" fill-opacity=".09"/><polyline points="${coords.map(p=>p.x+','+p.y).join(' ')}" fill="none" stroke="${ACCENT}" stroke-width="3"/>${circles}${months}</svg>`;}
function bars(rows){let c=el('cat').value;let p=el('period').value;let vals=CATS.map(cat=>{let cr=DATA.filter(r=>r.cat===cat&&matchPeriod(r.month,p));if(SPEC.barMode==='latest'){let lm=cr.map(r=>r.month).sort().at(-1);cr=cr.filter(r=>r.month===lm)}return {cat,value:totals(cr)[SPEC.metric]||0};});if(c!=='all')vals=vals.filter(x=>x.cat===c);let max=Math.max(1,...vals.map(x=>x.value));return `<div style="display:flex;flex-direction:column;justify-content:space-around;height:240px;gap:9px">${vals.map(x=>`<div><div style="display:flex;justify-content:space-between;gap:6px;margin-bottom:7px;font-size:12px"><span style="color:#d6e6f7">${escapeHTML(x.cat)}</span><b>${fmt(x.value,SPEC.unit)}</b></div><div style="background:#21374b;height:10px;border-radius:99px"><div style="height:100%;width:${(x.value/max*100).toFixed(2)}%;border-radius:99px;background:linear-gradient(90deg,${ACCENT},#e0eafa)"></div></div></div>`).join('')}</div>`}
function draw(){const rows=subset();el('kpis').innerHTML=SPEC.cards.map(([label,t,f,unit])=>{let n=value(rows,t,f);return `<article class="kpi"><label>${escapeHTML(label)}</label><div class="value">${fmt(n,unit)}</div><div class="mini">Calculated from current selection</div></article>`}).join('');let m=monthSeries(rows).map(x=>({...x,xdate:x.x}));el('lineChart').innerHTML=lineChart(m);el('barChart').innerHTML=bars(rows);el('monthly').innerHTML=m.slice(-5).reverse().map(x=>`<tr><td>${x.x}</td><td>${fmt(x.y,SPEC.unit)}</td></tr>`).join('')||'<tr><td colspan="2">No records</td></tr>'}
for(let cat of ['All categories',...CATS]){let opt=document.createElement('option');opt.value=cat==='All categories'?'all':cat;opt.textContent=cat;el('cat').append(opt)}for(let p of [...el('period').options]){if(p.value!=='all'&&!DATA.some(x=>matchPeriod(x.month,p.value)))p.remove()}el('cat').addEventListener('change',draw);el('period').addEventListener('change',draw);draw();
</script></body></html>'''

def refresh_preview_data(path, rows, cats, spec):
    """Refresh embedded values while preserving an authored dashboard layout."""
    if not path.exists():
        return None
    page = path.read_text(encoding='utf-8')
    payloads = (
        ('dashboard-data', {'rows': rows, 'categories': cats, 'spec': spec}),
        ('subscription-data', rows),
    )
    for script_id, data in payloads:
        marker = f'<script id="{script_id}" type="application/json">'
        before, opening, script = page.partition(marker)
        if not opening:
            continue
        _, closing, after = script.partition('</script>')
        if not closing:
            raise ValueError(f'Unclosed {script_id} script in {path}')
        json_data = json.dumps(data, separators=(',', ':')).replace('<', r'\u003c')
        return before + opening + '\n' + json_data + '\n  ' + closing + after
    return None


for i,name in enumerate(NAMES):
 rows,cats,spec=grouped(name); title=json.loads((ROOT/name/'metrics.json').read_text())['title'];
 narrative={0:'Monitor the latest selected month for MRR, then compare retention and the impact of downgrades. MRR is a <b>snapshot</b>, not a sum across months.',1:'The loan default status is a single September 2026 snapshot. Do not interpret its share as a historical default rate in each origination month.',2:'Occupancy is computed as occupied bed-days divided by staffed bed-days. Thirty-day return flags are illustrative and not risk-adjusted clinical outcomes.',3:'OTIF uses a line-based denominator including cancelled or partially delivered lines. Inventory stockout rate is the share of monthly SKU-location snapshots at zero stock.'}[i]
 mapping={'{{TITLE}}':html.escape(title),'{{ACCENT}}':COLORS[i],'{{CATEGORY}}':html.escape(spec['label']),'{{TREND}}':html.escape(spec['trend']),'{{METRIC}}':html.escape(spec['metric']),'{{DATA}}':json.dumps(rows,separators=(',',':')),'{{CATS}}':json.dumps(cats),'{{SPEC}}':json.dumps(spec),'{{NARRATIVE}}':narrative,'{{BAR_DESC}}':'Latest available month-end snapshot' if i==0 else 'Selected period · portfolio contribution'}
 code=refresh_preview_data(ROOT/name/'dashboard_preview.html', rows, cats, spec)
 if code is None:
  code=TEMPLATE
  for k,v in mapping.items():code=code.replace(k,v)
 (ROOT/name/'dashboard_preview.html').write_text(code,encoding='utf-8')
 print(name,'aggregates:',len(rows),'html kb',len(code)//1024)

cards=[]
for i,name in enumerate(NAMES):
 title=json.loads((ROOT/name/'metrics.json').read_text())['title']
 cards.append(f'<a href="{name}/dashboard_preview.html" class="item"><span class="no">0{i+1}</span><h2>{html.escape(title)}</h2><p>Explore interactive offline dashboard</p><span class="link">Open live preview ↗</span></a>')
index=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Industry BI Portfolio</title><style>body{{font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#07111e;color:#eff9ff;margin:0}}main{{max-width:1100px;margin:80px auto;padding:30px}}.over{{font-size:12px;font-weight:700;letter-spacing:2px;color:#38bdf8}}h1{{font-size:44px;max-width:770px;line-height:1.15}}.sub{{color:#9bb0c2;max-width:690px;line-height:1.75}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:45px}}.item{{display:block;background:linear-gradient(135deg,#14293e,#0b1828);border:1px solid #263c54;border-radius:16px;padding:30px;text-decoration:none;color:#f3f9ff;transition:.2s}}.item:hover{{transform:translateY(-4px);border-color:#38bdf8}}.no{{color:#38bdf8;letter-spacing:2px}}h2{{font-size:22px;margin:20px 0 8px}}p{{color:#95a9bc}}.link{{font-size:13px;color:#7bd5ff;display:inline-block;margin-top:18px}}footer{{margin-top:45px;color:#6d869d;font-size:12px}}@media(max-width:700px){{.grid{{grid-template-columns:1fr}}h1{{font-size:34px}}main{{margin:30px auto}}}}</style><main><div class="over">ANALYTICS LAB / POWER BI CASE STUDIES</div><h1>Four industries. Four decision-ready analytics solutions.</h1><div class="sub">Original synthetic datasets, validated KPI definitions, professional data models, DAX starters and four offline interactive preview dashboards. Native Power BI reports to be authored from the packaged import workbooks.</div><div class="grid">{''.join(cards)}</div><footer>Demonstration only · All data is fictional · HTML is a dashboard design prototype, not a native Power BI report</footer></main></html>'''
(ROOT/'START_HERE.html').write_text(index,encoding='utf-8')
