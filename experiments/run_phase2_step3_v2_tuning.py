import json, os, statistics
from phase2_scenario_generator import generate_scenarios
from phase3_runner_v2 import run_scenario
C={
'HB':[{'ants':a,'iterations':i,'label':f'a{a}_i{i}'} for a,i in ((8,10),(12,10),(16,10),(8,20),(12,20),(16,20))],
'HBP':[{'ants':a,'iterations':i,'label':f'a{a}_i{i}'} for a,i in ((8,10),(12,10),(16,10),(8,20),(12,20),(16,20))],
'DR-T':[{'R':R,'K':K,'ants':12,'iterations':20,'label':f'R{R}_K{K}'} for R,K in ((3.5,.5),(3.5,1),(4.5,.5),(4.5,1),(5.5,.5),(5.5,1))],
'DR-SAFE':[{'R':R,'K':K,'D_SAFE':D,'ants':12,'iterations':20,'label':f'R{R}_K{K}_D{D}'} for R,K,D in ((3.5,.5,.75),(3.5,1,1),(4.5,.5,1),(4.5,1,1.5),(5.5,.5,1),(5.5,1,1.5))],
'space_time_astar':[{'horizon':h,'label':f'h{h}'} for h in (20,30,40,50,60,70)],
'dstar_dwa':[{'progress_weight':p,'clearance_weight':c,'max_expansions':50,'label':f'p{p}_c{c}'} for p,c in ((1,.1),(1,.25),(1,.5),(1.5,.25),(2,.25),(2,.5))]}
ss=generate_scenarios(240); tuning=ss[:4]
def score(rows):
 cr=sum(x['any_collision'] for x in rows)/len(rows)
 tm=statistics.median([x['time_to_goal'] if x['time_to_goal'] is not None else 45 for x in rows])
 return .5*cr+.5*tm/45,cr,tm
os.makedirs('results/phase2_step3_v2_tuning',exist_ok=True)
summary={}
for m,cs in C.items():
 cand=[]
 for p in cs:
  rows=[run_scenario(s,m,p,max_ticks=45) for s in tuning]
  a,b,c=score(rows); cand.append({'method':m,'params':p,'score':a,'collision_rate':b,'median_time_to_goal':c,'n':4})
  print('candidate',m,p,'score',a,flush=True)
 best=min(cand,key=lambda x:x['score']); summary[m]={'best':best,'candidates':cand}; print('BEST',m,best,flush=True)
json.dump(summary,open('results/phase2_step3_v2_tuning/tuning_summary.json','w'),indent=2)
