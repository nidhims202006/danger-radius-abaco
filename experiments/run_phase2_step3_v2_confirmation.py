import json, os, multiprocessing as mp
from phase2_scenario_generator import generate_scenarios
from phase3_runner_v2 import run_scenario
PARAMS={
'HB':{'ants':8,'iterations':10,'label':'a8_i10'},
'HBP':{'ants':16,'iterations':20,'label':'a16_i20'},
'DR-T':{'R':4.5,'K':1,'ants':12,'iterations':20,'label':'R4.5_K1'},
'DR-SAFE':{'R':3.5,'K':0.5,'D_SAFE':0.75,'ants':12,'iterations':20,'label':'R3.5_K0.5_D0.75'},
'space_time_astar':{'horizon':30,'label':'h30'},
'dstar_dwa':{'progress_weight':1,'clearance_weight':0.1,'max_expansions':50,'label':'p1_c0.1'}}
METHODS=list(PARAMS)

def one(args):
 sid,m=args
 s=SCENARIOS[sid]
 return run_scenario(s,m,PARAMS[m],max_ticks=45)

if __name__=='__main__':
 SCENARIOS=generate_scenarios(240)
 tasks=[(i,m) for i in range(4,204) for m in METHODS]
 with mp.Pool(processes=min(12,mp.cpu_count())) as pool:
  rows=[]
  for i,r in enumerate(pool.imap_unordered(one,tasks,chunksize=1),1):
   rows.append(r)
   if i%50==0: print('completed',i,flush=True)
 rows.sort(key=lambda x:(x['scenario_id'],METHODS.index(x['method'])))
 os.makedirs('results/phase2_step3_v2',exist_ok=True)
 json.dump(rows,open('results/phase2_step3_v2/perrun.json','w'),indent=2)
 summary={}
 for m in METHODS:
  rr=[x for x in rows if x['method']==m]
  summary[m]={
   'n':len(rr),'success_rate':sum(x['success'] for x in rr)/len(rr),
   'collision_rate':sum(x['any_collision'] for x in rr)/len(rr),
   'zero_distance':sum(x['distance']==0 for x in rr),
   'mean_distance':sum(x['distance'] for x in rr)/len(rr),
   'mean_min_clearance':sum(x['min_clearance'] for x in rr)/len(rr),
   'mean_planning_time_s':sum(x['planning_time_s'] for x in rr)/len(rr),
   'mean_replans':sum(x['replans'] for x in rr)/len(rr),
   'floor_relaxation_runs':sum(x['floor_relaxations']>0 for x in rr),
   'total_floor_relaxations':sum(x['floor_relaxations'] for x in rr),
  }
 json.dump(summary,open('results/phase2_step3_v2/summary.json','w'),indent=2)
 print(json.dumps(summary,indent=2))
