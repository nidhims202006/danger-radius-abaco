import os, json, math, statistics, time, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'experiments'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'abaco'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'danger_radius'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'baselines'))
import drsafe_lib as L
import ABACO_safety_pred as SP

# Equal-budget historical fixed-grid tuning: 30 disjoint seeds, 6 candidates per method.
SEEDS = list(range(6000,6030))
C = {
 'HB': [dict(ants=a,iterations=i,label=f'a{a}_i{i}') for a,i in [(20,50),(30,75),(40,100),(50,100),(40,125),(60,100)]],
 'HBP': [dict(ants=a,iterations=i,label=f'a{a}_i{i}') for a,i in [(20,50),(30,75),(40,100),(50,100),(40,125),(60,100)]],
 'DR-T': [dict(R=R,K=K,ants=40,iterations=100,label=f'R{R}_K{K}') for R,K in [(2.5,1.0),(3.5,1.0),(4.5,1.0),(3.5,2.0),(4.5,2.0),(5.5,2.0)]],
 'DR-SAFE': [dict(R=R,K=K,D_SAFE=D,ants=40,iterations=100,label=f'R{R}_K{K}_D{D}') for R,K,D in [(3.5,1.0,1.0),(4.5,1.0,1.0),(3.5,2.0,1.0),(4.5,2.0,1.5),(5.5,2.0,1.5),(4.5,3.0,1.5)]],
}

def run(method,p,seed):
    if method=='HB':
        old=(L.base.NUM_ANTS,L.base.NUM_ITERATIONS)
        L.base.NUM_ANTS,L.base.NUM_ITERATIONS=p['ants'],p['iterations']
        try: return L.run_hb(seed)
        finally: L.base.NUM_ANTS,L.base.NUM_ITERATIONS=old
    if method=='HBP':
        old=(L.base.NUM_ANTS,L.base.NUM_ITERATIONS,SP.MODE)
        L.base.NUM_ANTS,L.base.NUM_ITERATIONS=p['ants'],p['iterations']
        try: return L._flat(SP.run_abaco_safety_pred(L.GRID,seed,mode='hb'),L.base)
        finally: L.base.NUM_ANTS,L.base.NUM_ITERATIONS,SP.MODE=old
    if method=='DR-T':
        old=(L.base.NUM_ANTS,L.base.NUM_ITERATIONS)
        L.base.NUM_ANTS,L.base.NUM_ITERATIONS=p['ants'],p['iterations']
        try: return L.run_dr(seed,R=p['R'],K=p['K'])
        finally: L.base.NUM_ANTS,L.base.NUM_ITERATIONS=old
    if method=='DR-SAFE':
        old=(L.base.NUM_ANTS,L.base.NUM_ITERATIONS)
        L.base.NUM_ANTS,L.base.NUM_ITERATIONS=p['ants'],p['iterations']
        try: return L.run_drs(seed,R=p['R'],K=p['K'],d_safe=p['D_SAFE'])
        finally: L.base.NUM_ANTS,L.base.NUM_ITERATIONS=old

def score_rows(rows):
    valid=[r for r in rows if r['ok'] and r['coll'] is not None and r['turns'] is not None]
    fail=1-len(valid)/len(rows)
    if not valid: return None
    coll=np.mean([r['coll'] for r in valid]); turns=np.mean([r['turns'] for r in valid]);
    return {'collision_rate':float(coll),'sharp_turns':float(turns),'failure_rate':float(fail),
            'score_raw':float(coll+turns/20.0)}

out={'protocol':{'seed_ids':SEEDS,'n_seeds':30,'candidates_per_method':6,
                 'selection_rule':'within-method z(collision events/run) + z(sharp turns); ties by shorter mean path; failures retained as a separate audit metric',
                 'fixed_common_alpha':1.0,'fixed_common_beta':5.0,'fixed_common_rho':0.3,
                 'primary_methods':['HB','HBP','DR-T','DR-SAFE']},'methods':{}}
t0=time.time()
for m,cands in C.items():
    cand=[]
    print('METHOD',m,flush=True)
    for ci,p in enumerate(cands):
        rows=[]
        for j,s in enumerate(SEEDS):
            r=run(m,p,s); rows.append(r)
        valid=[r for r in rows if r['ok'] and r['coll'] is not None]
        coll=np.array([r['coll'] for r in valid],float); turns=np.array([r['turns'] for r in valid],float); lens=np.array([r['len'] for r in valid],float)
        cr=float(coll.mean()) if len(coll) else float('inf'); tr=float(turns.mean()) if len(turns) else float('inf'); ln=float(lens.mean()) if len(lens) else float('inf'); fail=1-len(valid)/len(rows)
        cand.append({'params':p,'n':len(rows),'valid_n':len(valid),'failure_rate':fail,'collision_rate':cr,'sharp_turns':tr,'mean_length':ln})
        print(' ',ci,p,'coll',cr,'turns',tr,'fail',fail,flush=True)
    T=np.array([x['sharp_turns'] for x in cand]); Cc=np.array([x['collision_rate'] for x in cand]);
    z=lambda x:(x-x.mean())/(x.std() if x.std()>0 else 1)
    scores=z(T)+z(Cc)
    for x,sc in zip(cand,scores): x['tuning_score']=float(sc)
    best=sorted(cand,key=lambda x:(round(x['tuning_score'],12),x['mean_length']))[0]
    out['methods'][m]={'candidates':cand,'selected':best}
    print(' SELECTED',best,flush=True)
json.dump(out,open('equal_budget_tuning.json','w'),indent=2)
print('WROTE',os.path.abspath('equal_budget_tuning.json'),'elapsed',time.time()-t0)
