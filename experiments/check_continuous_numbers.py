"""Check Tables 27E and 27F of a manuscript .docx against results/continuous_cost/summary.json (written by analyze_continuous_cost.py from the raw per-run files).
Usage: python check_continuous_numbers.py manuscript.docx"""
import sys, re, json, docx
D=json.load(open('../results/continuous_cost/summary.json')); d=docx.Document(sys.argv[1]); caps={}; prev=None
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'
for el in d.element.body:
    if el.tag.endswith('}tbl'): prev=docx.table.Table(el,d)
    elif el.tag.endswith('}p'):
        m=re.match(r'Table (27[EF])\.',''.join(x.text or '' for x in el.iter(W)))
        if m and prev is not None: caps[m.group(1)]=prev
num=lambda s: float(s.replace('−','-'))
n=bad=0
def chk(a,b,tol):
    global n,bad; n+=1
    if abs(a-b)>tol: bad+=1; print('MISMATCH',a,b)
keys={'HB':'HB','HBP':'HBP','DR-T, truncated':'DRT_t','DR-T, continuous':'DRT_c','DR-SAFE 1.0, truncated':'TA_t','DR-SAFE 1.0, continuous':'TA_c','DR-SAFE 1.5, truncated':'TB_t','DR-SAFE 1.5, continuous':'TB_c'}
for row in caps['27E'].rows[1:]:
    c=[x.text.strip() for x in row.cells]; b={'development':'dev','confirmation':'conf'}[c[1]]; m=D[b]['means'][keys[c[0]]]
    chk(num(c[2]),m['adj'],5e-4); chk(num(c[3]),m['turns'],5e-3); chk(num(c[4]),m['len'],5e-3); chk(num(c[5]),m['clear'],5e-3)
at={'DR-T (continuous)':'DRT_c','DR-SAFE 1.0 (continuous)':'TA_c','DR-SAFE 1.5 (continuous)':'TB_c'}
for row in caps['27F'].rows[1:]:
    c=[x.text.strip() for x in row.cells]; b={'development':'dev','confirmation':'conf'}[c[2]]; k=f'{b}|{at[c[0]]}-{c[1]}'
    for cell,o,dg in ((c[3],'adj',3),(c[4],'turns',2),(c[5],'len',2)):
        s=D['vs_reference'][o][k]; mm=re.match(r'([+−\-0-9.]+) \[([+−\-0-9.]+), ([+−\-0-9.]+)\] \(([^)]+)\)',cell)
        t=10**-dg/2+1e-9
        chk(num(mm.group(1)),s['diff'],t); chk(num(mm.group(2)),s['diff_ci'][0],t); chk(num(mm.group(3)),s['diff_ci'][1],t)
        hp=mm.group(4); chk(1e-4 if hp=='<0.0001' else num(hp), 1e-4 if s['p_holm']<1e-4 else s['p_holm'], 5e-4); 
print(f'{n} values checked; {bad} disagree'); sys.exit(1 if bad else 0)
