"""A1 analysis: prediction-index sensitivity (v3: predicted[step+1]) vs frozen primary (v2: predicted[step]).
Post hoc; paired by scenario. Run from repo root."""
import json, numpy as np
from scipy.stats import binomtest
d='results/a1_sensitivity/'
v3=json.load(open(d+'part1_004_013.json'))+json.load(open(d+'part2_014_203.json'))
json.dump(v3,open(d+'perrun_v3.json','w'))
v2=[r for r in json.load(open('results/phase2_step3_v2/perrun.json')) if 4<=r['scenario_id']<=203]
rng=np.random.default_rng(0)
def idx(rows,m): return {r['scenario_id']:r for r in rows if r['method']==m}
def boot(x):
    x=np.asarray(x,float); b=[rng.choice(x,len(x)).mean() for _ in range(5000)]
    return np.percentile(b,[2.5,97.5])
out={}
for m in ('HBP','DR-T','DR-SAFE'):
    a,b=idx(v2,m),idx(v3,m); ids=sorted(a); assert ids==sorted(b) and len(ids)==200
    res={}
    for k,name in (('success','success'),('any_collision','collision')):
        x=np.array([a[i][k] for i in ids],int); y=np.array([b[i][k] for i in ids],int)
        n01=int(((x==0)&(y==1)).sum()); n10=int(((x==1)&(y==0)).sum())
        p=binomtest(n01,n01+n10,0.5).pvalue if n01+n10 else 1.0
        dif=y-x; lo,hi=boot(dif)
        res[name]=dict(v2=x.mean(),v3=y.mean(),diff_pp=100*dif.mean(),ci_pp=[100*lo,100*hi],gained=n01,lost=n10,mcnemar_exact_p=p)
    # path metrics on scenarios successful in both
    both=[i for i in ids if a[i]['success'] and b[i]['success']]
    for k in ('distance','turns','min_clearance','time_to_goal'):
        res[k+'_both_success']=dict(n=len(both),v2=float(np.mean([a[i][k] for i in both])),v3=float(np.mean([b[i][k] for i in both])))
    res['mean_distance_all']=dict(v2=float(np.mean([a[i]['distance'] for i in ids])),v3=float(np.mean([b[i]['distance'] for i in ids])))
    res['floor_relax_runs']=dict(v2=sum(a[i]['floor_relaxations']>0 for i in ids),v3=sum(b[i]['floor_relaxations']>0 for i in ids))
    res['identical_outcome_scenarios']=sum(a[i]['success']==b[i]['success'] and a[i]['any_collision']==b[i]['any_collision'] for i in ids)
    out[m]=res
json.dump(out,open(d+'a1_summary.json','w'),indent=2,default=float)
for m,r in out.items():
    print('\n==',m)
    for k in ('success','collision'):
        q=r[k]; print(f"{k:9s} v2 {100*q['v2']:.1f}%  v3 {100*q['v3']:.1f}%  diff {q['diff_pp']:+.1f}pp CI[{q['ci_pp'][0]:+.1f},{q['ci_pp'][1]:+.1f}]  gained {q['gained']} lost {q['lost']}  p={q['mcnemar_exact_p']:.3f}")
    for k in ('mean_distance_all','distance_both_success','turns_both_success','min_clearance_both_success'):
        print(k,{a:round(b,2) if isinstance(b,float) else b for a,b in r[k].items()})
    print('floor relax runs',r['floor_relax_runs'],'| identical-outcome scenarios',r['identical_outcome_scenarios'],'/200')
# ranking
print('\nRanking v3: ',{m:(round(100*out[m]['success']['v3'],1),round(100*out[m]['collision']['v3'],1)) for m in out})
