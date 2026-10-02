"""A1: post hoc prediction-index sensitivity run (HBP, DR-T, DR-SAFE; frozen tuned settings).
Usage: ADAPTER=phase3_abaco_v3 python run_a1_sensitivity.py START END OUT.json"""
import json, sys, time
from phase2_scenario_generator import generate_scenarios
from phase3_runner_sens import run_scenario
PARAMS={
'HBP':{'ants':16,'iterations':20},
'DR-T':{'R':3.5,'K':0.5,'ants':12,'iterations':20},
'DR-SAFE':{'R':3.5,'K':0.5,'D_SAFE':0.75,'ants':12,'iterations':20}}
S=generate_scenarios(240)
a,b,out=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
rows=[];t=time.time()
for i in range(a,b+1):
    for m in PARAMS: rows.append(run_scenario(S[i],m,PARAMS[m],max_ticks=45))
    if (i-a+1)%10==0: print('done',i,round(time.time()-t),'s',flush=True); json.dump(rows,open(out,'w'))
json.dump(rows,open(out,'w')); print('WROTE',out,len(rows))
