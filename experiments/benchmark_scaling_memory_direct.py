from __future__ import annotations
import json, math, os, random, resource, sys, time, tracemalloc
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from phase3_abaco import abaco_plan, FastDStarLite
from phase2_planners import space_time_astar, neighbors

METHODS={
 'HB': {'ants':8,'iterations':10},
 'HBP': {'ants':16,'iterations':20},
 'DR-T': {'R':4.5,'K':1.0,'ants':12,'iterations':20},
 'DR-SAFE': {'R':4.5,'K':1.0,'D_SAFE':1.5,'ants':12,'iterations':20},
 'space_time_astar': {'horizon':30},
 'dstar_dwa': {'progress_weight':1.0,'clearance_weight':0.1,'max_expansions':50},
}
SIZES=[12,18,25,30,40]
DYN=[1,3,5]

def make(size, nd, seed):
    rng=random.Random(seed); start=(0,0); goal=(size-1,size-1)
    static=set(); target=max(1,int(round(size*size*.08)))
    while len(static)<target:
        x=(rng.randrange(size),rng.randrange(size))
        if x in (start,goal) or abs(x[0]-x[1])<=1: continue
        static.add(x)
    dyn=[]; occ=static|{start,goal}
    for j in range(nd):
        for _ in range(1000):
            r=rng.uniform(1,size-2); c=rng.uniform(1,size-2)
            if all(math.dist((r,c),x)>=3 for x in occ): break
        occ.add((round(r),round(c))); dyn.append((r,c))
    pred=[]
    for t in range(31):
        pred.append([(min(max(r,0),size-1),min(max(c+.45*t,0),size-1)) for r,c in dyn])
    return start,goal,static,pred

def one(size,nd,method):
    start,goal,static,pred=make(size,nd,700000+size*100+nd)
    p=METHODS[method]
    tracemalloc.start(); rss0=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024; t0=time.perf_counter()
    if method in ('HB','HBP','DR-T','DR-SAFE'):
        path,pt,_=abaco_plan(size,size,start,goal,static,pred,mode=method,**p,seed=1234)
    elif method=='space_time_astar':
        path,pt=space_time_astar(size,size,start,goal,static,[set(x) for x in pred],max_time=p['horizon'])
    else:
        blocked=static|{(round(r),round(c)) for r,c in pred[0]}
        d=FastDStarLite(size,size,start,goal,blocked,max_expansions=p['max_expansions']); d.compute(); path=d.path(); pt=time.perf_counter()-t0
    wall=time.perf_counter()-t0
    cur,peak=tracemalloc.get_traced_memory(); tracemalloc.stop()
    rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
    return {'grid':size,'cells':size*size,'dynamic_obstacles':nd,'method':method,'path_found':bool(path),'planning_time_s':pt,'wall_time_s':wall,'peak_tracemalloc_MB':peak/1e6,'peak_rss_MB':rss/1e6,'rss_delta_MB':max(0,(rss-rss0)/1e6)}

if __name__=='__main__':
    rows=[]
    for size in SIZES:
      for nd in DYN:
        for m in METHODS:
          r=one(size,nd,m); rows.append(r); print(json.dumps(r),flush=True)
    out=Path(__file__).resolve().parent.parent/'results'/'scaling_memory_direct.json'; out.write_text(json.dumps(rows,indent=2)); print('saved',out)
