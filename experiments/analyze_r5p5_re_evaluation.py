"""Analyze the R=5.5 DR-SAFE-T re-evaluation against the R=4.5 reference.

Both blocks use the same 300 seeds (10300-10599), K=2, D_SAFE=1.5.
R=5.5 was selected by the previously completed 30-seed extended-grid tuning.
No parameter search is performed here.
"""
import os, json
import numpy as np
from scipy.stats import wilcoxon
ROOT=os.path.dirname(os.path.dirname(__file__))
P4=os.path.join(ROOT,'results','drsafe_drsafe_r4p5_confirmation.json')
P5=os.path.join(ROOT,'results','drsafe_r5p5_confirmation.json')
OUT=os.path.join(ROOT,'results','r5p5_re_evaluation_analysis.json')

a=json.load(open(P4))['runs']; b=json.load(open(P5))['runs']
seeds=sorted(set(a)&set(b), key=int)
metrics={'len':'Mean path length','turns':'Mean sharp turns','clear':'Mean minimum clearance','coll':'Collisions per run'}
summary={}
for key,label in metrics.items():
    x=np.array([a[s][key] for s in seeds],float); y=np.array([b[s][key] for s in seeds],float); d=y-x
    bs=np.random.default_rng(12345).choice(d,(10000,len(d))).mean(axis=1)
    summary[key]={
      'label':label,'R4.5_mean':float(x.mean()),'R5.5_mean':float(y.mean()),
      'difference_R5.5_minus_R4.5':float(d.mean()),
      'bootstrap_95ci_difference':[float(np.quantile(bs,.025)),float(np.quantile(bs,.975))],
      'wilcoxon_p':float(wilcoxon(d,zero_method='wilcox',alternative='two-sided').pvalue)
    }

def agg(r):
 v=[r[s] for s in seeds if r[s]['ok']]
 return {'n':len(v),'success_rate_pct':100*len(v)/len(seeds),'any_collision_rate_pct':100*np.mean([q['coll']>0 for q in v]),'collisions_per_run':float(np.mean([q['coll'] for q in v])),'mean_path_length':float(np.mean([q['len'] for q in v])),'mean_sharp_turns':float(np.mean([q['turns'] for q in v])),'mean_min_clearance':float(np.mean([q['clear'] for q in v]))}

out={'protocol':{'seeds':'10300-10599','n':300,'K':2.0,'D_SAFE':1.5,'R_reference':4.5,'R_re_evaluated':5.5,'R5.5_selection_source':'30-seed extended-grid tuning on seeds 6000-6029','selection_rule':'z(sharp turns)+z(collisions/run), tie by shorter length'},'aggregate_R4.5':agg(a),'aggregate_R5.5':agg(b),'paired_comparison':summary}
json.dump(out,open(OUT,'w'),indent=2)
print(json.dumps(out,indent=2))
