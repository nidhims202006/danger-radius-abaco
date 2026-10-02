import json, multiprocessing as mp
from phase2_scenario_generator import generate_scenarios
from phase3_runner_v2 import run_scenario
P={'HB':{'ants':8,'iterations':10},'HBP':{'ants':16,'iterations':20},'DR-T':{'R':4.5,'K':1,'ants':12,'iterations':20},'DR-SAFE':{'R':3.5,'K':.5,'D_SAFE':.75,'ants':12,'iterations':20},'space_time_astar':{'horizon':30},'dstar_dwa':{'progress_weight':1,'clearance_weight':.1,'max_expansions':50}}
SS=generate_scenarios(240)

def f(x):
 i,m=x; return run_scenario(SS[i],m,P[m],max_ticks=45)
if __name__=='__main__':
 tasks=[(i,m) for i in range(4,24) for m in P]
 with mp.Pool(5) as pool: rows=list(pool.imap_unordered(f,tasks,1))
 rows.sort(key=lambda r:(r['scenario_id'],r['method']))
 json.dump(rows,open('results/phase2_step3_v2_smoke/perrun.json','w'),indent=2)
 for m in P:
  rr=[r for r in rows if r['method']==m]
  print(m,'n',len(rr),'zero',sum(r['distance']==0 for r in rr),'success',sum(r['success'] for r in rr),'collisions',sum(r['any_collision'] for r in rr),'floorrelax_runs',sum(r['floor_relaxations']>0 for r in rr))
