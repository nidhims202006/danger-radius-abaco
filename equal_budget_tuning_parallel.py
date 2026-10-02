import os, json, time, sys, multiprocessing as mp
import numpy as np
ROOT=os.path.dirname(__file__)
sys.path.insert(0,os.path.join(ROOT,'experiments')); sys.path.insert(0,os.path.join(ROOT,'abaco')); sys.path.insert(0,os.path.join(ROOT,'danger_radius')); sys.path.insert(0,os.path.join(ROOT,'baselines'))
C={
 'HB':[dict(ants=a,iterations=i,label=f'a{a}_i{i}') for a,i in [(20,50),(30,75),(40,100),(50,100),(40,125),(60,100)]],
 'HBP':[dict(ants=a,iterations=i,label=f'a{a}_i{i}') for a,i in [(20,50),(30,75),(40,100),(50,100),(40,125),(60,100)]],
 'DR-T':[dict(R=R,K=K,ants=40,iterations=100,label=f'R{R}_K{K}') for R,K in [(2.5,1.0),(3.5,1.0),(4.5,1.0),(3.5,2.0),(4.5,2.0),(5.5,2.0)]],
 'DR-SAFE':[dict(R=R,K=K,D_SAFE=D,ants=40,iterations=100,label=f'R{R}_K{K}_D{D}') for R,K,D in [(3.5,1.0,1.0),(4.5,1.0,1.0),(3.5,2.0,1.0),(4.5,2.0,1.5),(5.5,2.0,1.5),(4.5,3.0,1.5)]],
}
SEEDS=list(range(6000,6030))
def worker(task):
    m,p,s=task
    import drsafe_lib as L, ABACO_safety_pred as SP
    if m=='HB':
        old=(L.base.NUM_ANTS,L.base.NUM_ITERATIONS); L.base.NUM_ANTS,L.base.NUM_ITERATIONS=p['ants'],p['iterations']
        try:r=L.run_hb(s)
        finally:L.base.NUM_ANTS,L.base.NUM_ITERATIONS=old
    elif m=='HBP':
        old=(L.base.NUM_ANTS,L.base.NUM_ITERATIONS); L.base.NUM_ANTS,L.base.NUM_ITERATIONS=p['ants'],p['iterations']
        try:r=L._flat(SP.run_abaco_safety_pred(L.GRID,s,mode='hb'),L.base)
        finally:L.base.NUM_ANTS,L.base.NUM_ITERATIONS=old
    elif m=='DR-T':
        old=(L.base.NUM_ANTS,L.base.NUM_ITERATIONS); L.base.NUM_ANTS,L.base.NUM_ITERATIONS=p['ants'],p['iterations']
        try:r=L.run_dr(s,R=p['R'],K=p['K'])
        finally:L.base.NUM_ANTS,L.base.NUM_ITERATIONS=old
    else:
        old=(L.base.NUM_ANTS,L.base.NUM_ITERATIONS); L.base.NUM_ANTS,L.base.NUM_ITERATIONS=p['ants'],p['iterations']
        try:r=L.run_drs(s,R=p['R'],K=p['K'],d_safe=p['D_SAFE'])
        finally:L.base.NUM_ANTS,L.base.NUM_ITERATIONS=old
    return {'method':m,'params':p,'seed':s,'result':r}

def summarize(items):
    cand=[]
    for p in C[items[0]['method']]:
        rs=[x['result'] for x in items if x['params']==p]
        valid=[r for r in rs if r['ok'] and r['coll'] is not None]
        cand.append({'params':p,'n':len(rs),'valid_n':len(valid),'failure_rate':1-len(valid)/len(rs),
          'collision_rate':float(np.mean([r['coll'] for r in valid])) if valid else float('inf'),
          'sharp_turns':float(np.mean([r['turns'] for r in valid])) if valid else float('inf'),
          'mean_length':float(np.mean([r['len'] for r in valid])) if valid else float('inf')})
    T=np.array([x['sharp_turns'] for x in cand]); CC=np.array([x['collision_rate'] for x in cand]);
    z=lambda x:(x-x.mean())/(x.std() if x.std()>0 else 1)
    for x,sc in zip(cand,z(T)+z(CC)):x['tuning_score']=float(sc)
    best=sorted(cand,key=lambda x:(round(x['tuning_score'],12),x['mean_length']))[0]
    return {'candidates':cand,'selected':best}

if __name__=='__main__':
    allitems=[]; t0=time.time(); nworkers=min(12,mp.cpu_count())
    for m in C:
        path=os.path.join(ROOT,f'partial_{m}.json')
        if os.path.exists(path):
            done=json.load(open(path)); donekeys={(x['method'],json.dumps(x['params'],sort_keys=True),x['seed']) for x in done}; allitems.extend(done)
        else: done=[]; donekeys=set()
        tasks=[(m,p,s) for p in C[m] for s in SEEDS if (m,json.dumps(p,sort_keys=True),s) not in donekeys]
        print('RUN',m,'tasks',len(tasks),'workers',nworkers,flush=True)
        with mp.Pool(nworkers) as pool:
            for i,x in enumerate(pool.imap_unordered(worker,tasks),1):
                done.append(x)
                if i%20==0:
                    json.dump(done,open(path,'w')); print(m,i,'/',len(tasks),'elapsed',round(time.time()-t0),flush=True)
        json.dump(done,open(path,'w')); allitems=[x for x in allitems if x['method']!=m]+done
        print('DONE',m,summarize(done),flush=True)
    out={'protocol':{'seeds':SEEDS,'n_seeds':30,'candidates_per_method':6,'selection':'z(collision rate)+z(sharp turns), tie mean path length'},'methods':{}}
    for m in C: out['methods'][m]=summarize([x for x in allitems if x['method']==m])
    json.dump(out,open(os.path.join(ROOT,'equal_budget_tuning.json'),'w'),indent=2)
    print('COMPLETE',time.time()-t0)
