import json, os, multiprocessing as mp, sys
from phase2_scenario_generator import generate_scenarios
from phase3_runner_v2 import run_scenario
PARAMS={
'HB':{'ants':16,'iterations':20,'label':'a16_i20'},
'HBP':{'ants':16,'iterations':20,'label':'a16_i20'},
'DR-T':{'R':3.5,'K':0.5,'ants':12,'iterations':20,'label':'R3.5_K0.5'},
'DR-SAFE':{'R':3.5,'K':0.5,'D_SAFE':0.75,'ants':12,'iterations':20,'label':'R3.5_K0.5_D0.75'},
'space_time_astar':{'horizon':30,'label':'h30'},
'dstar_dwa':{'progress_weight':1,'clearance_weight':0.1,'max_expansions':50,'label':'p1_c0.1'}}
METHODS=list(PARAMS)
SCENARIOS=generate_scenarios(240)

def one(args):
 sid,m=args
 return run_scenario(SCENARIOS[sid],m,PARAMS[m],max_ticks=45)
if __name__=='__main__':
 start=int(sys.argv[1]); end=int(sys.argv[2])
 tasks=[(i,m) for i in range(start,end+1) for m in METHODS]
 with mp.Pool(min(24,mp.cpu_count())) as pool:
  rows=[]
  for i,r in enumerate(pool.imap_unordered(one,tasks,chunksize=2),1):
   rows.append(r)
   if i%50==0: print('completed',i,flush=True)
 rows.sort(key=lambda x:(x['scenario_id'],METHODS.index(x['method'])))
 outdir='results/phase2_step3_v2_chunks'; os.makedirs(outdir,exist_ok=True)
 path=f'{outdir}/perrun_{start:03d}_{end:03d}.json'; json.dump(rows,open(path,'w'),indent=2)
 print('WROTE',path,'N',len(rows),flush=True)
