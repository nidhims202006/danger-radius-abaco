import json,os,multiprocessing as mp,statistics
from phase2_scenario_generator import generate_scenarios
from phase3_runner_v3 import run_scenario
C={
'sipp':[{'horizon':h,'label':f'h{h}'} for h in (20,30,40,50,60,70)],
'aco_dwa':[{'ants':a,'iterations':i,'clearance_weight':c,'goal_weight':g,'label':f'a{a}_i{i}_c{c}_g{g}'} for a,i,c,g in ((8,10,.1,1),(12,10,.1,1),(16,10,.1,1),(8,20,.25,1),(12,20,.25,1),(16,20,.25,1))]}
SS=generate_scenarios(240)[:4]
def score(rows):
 cr=sum(r['any_collision'] for r in rows)/len(rows)
 tm=statistics.median([r['time_to_goal'] if r['time_to_goal'] is not None else 45 for r in rows])
 return .5*cr+.5*tm/45,cr,tm
def one(x):
 m,p=x; rows=[run_scenario(s,m,p,max_ticks=45) for s in SS]; a,b,c=score(rows)
 return {'method':m,'params':p,'score':a,'collision_rate':b,'median_time_to_goal':c,'n':4}
if __name__=='__main__':
 with mp.Pool(min(24,mp.cpu_count())) as pool: out=list(pool.imap_unordered(one,[(m,p) for m,ps in C.items() for p in ps]))
 summary={}
 for m in C:
  cs=sorted([x for x in out if x['method']==m],key=lambda x:x['score']); summary[m]={'best':cs[0],'candidates':cs}; print('BEST',m,cs[0],flush=True)
 os.makedirs('results/phase2_strong_tuning',exist_ok=True); json.dump(summary,open('results/phase2_strong_tuning/tuning_summary.json','w'),indent=2)
