import json,os,multiprocessing as mp,sys
from phase2_scenario_generator import generate_scenarios
from phase3_runner_v3 import run_scenario
P={'sipp':{'horizon':30,'label':'h30'},'aco_dwa':{'ants':8,'iterations':10,'clearance_weight':.1,'goal_weight':1,'label':'a8_i10_c0.1_g1'}}
M=list(P); S=generate_scenarios(240)
def one(x):
 i,m=x; return run_scenario(S[i],m,P[m],max_ticks=45)
if __name__=='__main__':
 a,b=map(int,sys.argv[1:3]); tasks=[(i,m) for i in range(a,b+1) for m in M]
 with mp.Pool(min(24,mp.cpu_count())) as pool: rows=list(pool.imap_unordered(one,tasks,chunksize=1))
 rows.sort(key=lambda x:(x['scenario_id'],M.index(x['method'])))
 d='results/phase2_strong_chunks';os.makedirs(d,exist_ok=True); f=f'{d}/perrun_{a:03d}_{b:03d}.json';json.dump(rows,open(f,'w'),indent=2);print(f,len(rows))
