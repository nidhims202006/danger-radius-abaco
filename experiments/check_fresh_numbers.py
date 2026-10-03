"""Check Tables 27A-27D of a manuscript .docx against the stored per-run results of the fresh crossed confirmation.
Usage: python check_fresh_numbers.py manuscript.docx   (recomputes from results/fresh_confirmation/*.jsonl)"""
import sys, re, json, collections
import numpy as np, docx
from fresh_confirmation_generator import generate_fresh
R='../results/fresh_confirmation/'
S={s.scenario_id:s for s in generate_fresh()}; IDS=sorted(S)
def load(a): return {(r['method'],r['scenario_id']):r for r in map(json.loads,open(R+a+'.jsonl'))}
A={'age':load('legacy'),'flat':load('flat'),'oth':load('other')}
M={'DR-T (age-based deposit)':('age','DR-T'),'HB (age-based)':('age','HB'),'HBP (age-based)':('age','HBP'),'DR-SAFE (age-based)':('age','DR-SAFE'),
 'DR-T (flat deposit)':('flat','DR-T'),'HB (flat)':('flat','HB'),'HBP (flat)':('flat','HBP'),'DR-SAFE (flat)':('flat','DR-SAFE'),
 'Space-time A*':('oth','space_time_astar'),'SIPP-style':('oth','sipp'),'D* Lite + DWA':('oth','dstar_dwa'),'ACO+DWA':('oth','aco_dwa'),'ORCA':('oth','orca'),'MPC':('oth','mpc'),
 'DR-T (age-based)':('age','DR-T')}
def ids_where(fn): return [i for i in IDS if fn(S[i])]
def rate(label,k,ids=IDS):
    a,m=M[label]; return 100*np.mean([bool(A[a][(m,i)][k]) for i in ids])
d=docx.Document(sys.argv[1]); T={}
for t in d.tables:
    pass
caps={}
body=d.element.body; prev=None
for el in body:
    if el.tag.endswith('}tbl'): prev=docx.table.Table(el,d)
    elif el.tag.endswith('}p'):
        txt=''.join(x.text or '' for x in el.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
        m=re.match(r'Table (27[A-D])\.',txt)
        if m and prev is not None: caps[m.group(1)]=prev
bad=n=0
def chk(cell,val,tol=0.051):
    global bad,n; n+=1
    try: ok=abs(float(cell)-val)<=tol
    except: ok=False
    if not ok: bad+=1; print('MISMATCH',cell,val)
t=caps['27A']
for row in t.rows[1:]:
    lab=row.cells[0].text.strip(); a,m=M[lab]
    chk(row.cells[2].text,rate(lab,'success')); chk(row.cells[3].text,rate(lab,'any_collision'))
    chk(row.cells[4].text,np.mean([A[a][(m,i)]['distance'] for i in IDS])); chk(row.cells[5].text,np.mean([A[a][(m,i)]['planning_time_s'] for i in IDS]),0.0006)
for key,fn,levels in (('27C',lambda s:s.dynamic_obstacles[0].motion,['constant','curved','stop_go','random_walk']),('27D',lambda s:len(s.dynamic_obstacles),[1,3,5,8])):
    for row in caps[key].rows[1:]:
        lab=row.cells[0].text.strip()
        for j,l in enumerate(levels,1): chk(row.cells[j].text,rate(lab,'any_collision',ids_where(lambda s,l=l:fn(s)==l)))
        chk(row.cells[5].text,rate(lab,'any_collision'))
# 27B: recompute exact McNemar + Holm
from scipy import stats
def mc(a,b):
    n01=int(np.sum(~a&b)); n10=int(np.sum(a&~b)); k=n01+n10
    return n10,n01,(1.0 if k==0 else min(1.0,2*stats.binom.cdf(min(n01,n10),k,0.5)))
base='DR-T (age-based deposit)'; rows=[]
for row in caps['27B'].rows[1:]:
    lab=row.cells[0].text.strip(); k='success' if row.cells[1].text.strip()=='success' else 'any_collision'
    a,m=M[base]; b1=np.array([bool(A[a][(m,i)][k]) for i in IDS]); a2,m2=M[lab]; b2=np.array([bool(A[a2][(m2,i)][k]) for i in IDS])
    o,c,p=mc(b1,b2); rows.append((row,p,o,c,100*(b1.mean()-b2.mean())))
order=sorted(range(len(rows)),key=lambda i:rows[i][1]); run=0; holm={}
for rank,i in enumerate(order): run=max(run,min(1,(len(rows)-rank)*rows[i][1])); holm[i]=run
def fp(p): return '<0.0001' if p<1e-4 else f'{p:.4f}' if p<0.1 else f'{p:.3f}'
for i,(row,p,o,c,df) in enumerate(rows):
    chk(row.cells[2].text,df); n+=3
    for cell,val in ((row.cells[3].text,f'{o} / {c}'),(row.cells[4].text,fp(p)),(row.cells[5].text,fp(holm[i]))):
        if cell.strip()!=val: bad+=1; print('MISMATCH',cell,val)
print(f'{n} cells/values checked; {bad} disagree')
sys.exit(1 if bad else 0)
