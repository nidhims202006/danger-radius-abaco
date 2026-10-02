import os,sys,json,time,multiprocessing as mp
import numpy as np
ROOT=os.path.dirname(os.path.dirname(__file__))
for s in ('experiments','abaco','danger_radius','baselines'): sys.path.insert(0,os.path.join(ROOT,s))
import drsafe_lib as L
SEEDS=list(range(10300,10600)); OUT=os.path.join(ROOT,'results','drsafe_drsafe_r4p5_confirmation.json')

def one(s): return L.run_drs(s,R=4.5,K=2.0,d_safe=1.5)
def summ(rs):
 v=[r for r in rs.values() if r['ok']]
 return {'n':len(rs),'success_rate':100*len(v)/len(rs),'any_collision_rate':100*np.mean([r['coll']>0 for r in v]),'collisions_per_run':float(np.mean([r['coll'] for r in v])),'mean_path_length':float(np.mean([r['len'] for r in v])),'mean_sharp_turns':float(np.mean([r['turns'] for r in v])),'mean_min_clearance':float(np.mean([r['clear'] for r in v])),'mean_convergence':float(np.mean([r['conv'] for r in v])),'mean_fallbacks':float(np.mean([r['fb'] for r in v]))}
if __name__=='__main__':
 runs={}
 if os.path.exists(OUT): runs=json.load(open(OUT)).get('runs',{})
 todo=[s for s in SEEDS if str(s) not in runs]
 t=time.time(); w=min(12,mp.cpu_count())
 with mp.Pool(w) as p:
  for i,(s,r) in enumerate(zip(todo,p.imap(one,todo)),1):
   runs[str(s)]=r
   if i%25==0:
    with open(OUT,'w') as f: json.dump({'protocol':{'seeds':'10300-10599','R':5.5,'K':2.0,'D_SAFE':1.5,'n':300},'runs':runs,'summary':summ(runs)},f,indent=2)
    print(i,'/',len(todo),'elapsed',round(time.time()-t,1),flush=True)
 with open(OUT,'w') as f: json.dump({'protocol':{'seeds':'10300-10599','R':5.5,'K':2.0,'D_SAFE':1.5,'n':300},'runs':runs,'summary':summ(runs)},f,indent=2)
 print(json.dumps(summ(runs),indent=2))
