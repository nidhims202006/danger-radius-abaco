import json, sys, math, random, time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from phase3_abaco import abaco_plan, FastDStarLite
from phase2_planners import space_time_astar
METHODS={
 'HB': {'ants':8,'iterations':10}, 'HBP': {'ants':16,'iterations':20},
 'DR-T': {'R':4.5,'K':1.0,'ants':12,'iterations':20},
 'DR-SAFE': {'R':4.5,'K':1.0,'D_SAFE':1.5,'ants':12,'iterations':20},
 'space_time_astar': {'horizon':30}, 'dstar_dwa': {'max_expansions':50}}
def make(size,nd,seed):
 rng=random.Random(seed); start=(0,0); goal=(size-1,size-1); static=set(); target=max(1,int(round(size*size*.08)))
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
 pred=[[(r,min(max(c+.45*t,0),size-1)) for r,c in dyn] for t in range(31)]
 return start,goal,static,pred
size=int(sys.argv[1]); nd=int(sys.argv[2]); m=sys.argv[3]
start,goal,static,pred=make(size,nd,700000+size*100+nd)
t0=time.perf_counter();
if m in ('HB','HBP','DR-T','DR-SAFE'):
 path,pt,_=abaco_plan(size,size,start,goal,static,pred,mode=m,**METHODS[m],seed=1234)
elif m=='space_time_astar': path,pt=space_time_astar(size,size,start,goal,static,[set(x) for x in pred],max_time=30)
else:
 blocked=static|{(round(r),round(c)) for r,c in pred[0]}; d=FastDStarLite(size,size,start,goal,blocked,max_expansions=50); d.compute(); path=d.path(); pt=time.perf_counter()-t0
print(json.dumps({'grid':size,'dynamic_obstacles':nd,'method':m,'path_found':bool(path),'planning_time_s':pt,'wall_time_s':time.perf_counter()-t0}))
