"""Analyze the Priority-13 fresh 300-run multi-noise robustness study.

Produces descriptive summaries only. The closed-loop Holm family is unchanged;
this fresh fixed-grid robustness block does not add post-hoc multiplicity claims.
"""
import json, os, numpy as np
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R=os.path.join(ROOT,'results','priority13')
FILES={'HB_clean':'confirmation_HB_clean.json','HBP_n1':'confirmation_HBP_n1.json','APFP_n1':'confirmation_APFP_n1.json','HBP_n':'confirmation_HBP_n.json','APFP_n':'confirmation_APFP_n.json','HBP_n3':'confirmation_HBP_n3.json','APFP_n3':'confirmation_APFP_n3.json'}

def summary(rows):
    ok=[r for r in rows if r['ok']]
    return {
      'N':len(rows),
      'success_rate':float(np.mean([r['ok'] for r in rows])),
      'collision_run_rate':float(np.mean([(r['coll'] or 0)>0 for r in rows])),
      'collisions_per_run':float(np.mean([r['coll'] or 0 for r in rows])),
      'mean_sharp_turns_successful':float(np.mean([r['turns'] for r in ok])),
      'mean_path_length_successful':float(np.mean([r['len'] for r in ok])),
      'mean_min_clearance_successful':float(np.mean([r['clear'] for r in ok])),
    }

out={'study':'Priority 13 multi-noise robustness','tuning_seeds':'9000-9029','confirmation_seeds':'10300-10599','noise_levels':{'n1':[5.0,0.10],'n':[15.0,0.20],'n3':[30.0,0.40]},'methods':{}}
for name,f in FILES.items():
    d=json.load(open(os.path.join(R,f)))
    out['methods'][name]={'noise':d.get('noise'),'params':d.get('params'),'summary':summary([x['result'] for x in d['runs']])}
json.dump(out,open(os.path.join(R,'priority13_summary.json'),'w'),indent=2)
print(json.dumps(out,indent=2))
