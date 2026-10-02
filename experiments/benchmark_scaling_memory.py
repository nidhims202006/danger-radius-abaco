from __future__ import annotations
import json, math, os, random, statistics, subprocess, sys, tempfile, time, resource
from pathlib import Path

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from phase2_scenario_generator import DynamicSpec, Scenario
from phase3_runner import run_scenario

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
REPS=2

def make_scenario(rows, cols, n_dyn, seed):
    rng=random.Random(seed)
    start=(0,0); goal=(rows-1,cols-1)
    # deterministic lattice of sparse static obstacles at density ~0.08, avoid diagonal corridor
    static=set()
    target=max(1,int(round(rows*cols*0.08)))
    while len(static)<target:
        cell=(rng.randrange(rows),rng.randrange(cols))
        if cell in (start,goal): continue
        if abs(cell[0]-cell[1])<=1: continue
        static.add(cell)
    dyn=[]
    occ=set(static)|{start,goal}
    for j in range(n_dyn):
        for _ in range(1000):
            r=rng.uniform(1,rows-2); c=rng.uniform(1,cols-2)
            if all(math.dist((r,c),x)>=3 for x in occ): break
        occ.add((round(r),round(c)))
        dyn.append(DynamicSpec(r,c,0.45,(j*71+23)%360,'constant'))
    return Scenario(seed,seed,rows,cols,0.08,start,goal,tuple(sorted(static)),tuple(dyn),0.35)

def child_case(size,n_dyn,method,rep):
    s=make_scenario(size,size,n_dyn,900000+size*100+n_dyn*10+rep)
    p=METHODS[method]
    t0=time.perf_counter()
    out=run_scenario(s,method,p,max_ticks=40)
    wall=time.perf_counter()-t0
    rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
    out.update({'grid':f'{size}x{size}','grid_cells':size*size,'dynamic_obstacles':n_dyn,'repeat':rep,'wall_time_s':wall,'peak_rss_bytes':rss})
    return out

if __name__=='__main__':
    rows=[]
    for size in SIZES:
      for nd in DYN:
        for method in METHODS:
          for rep in range(REPS):
            rows.append(child_case(size,nd,method,rep))
            print(json.dumps(rows[-1]), flush=True)
    out=ROOT.parent/'results'/'scaling_memory_benchmark.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(rows,indent=2))
    print('saved',out)
