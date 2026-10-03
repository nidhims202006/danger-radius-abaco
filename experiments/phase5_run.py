"""Usage: ADAPTER=[legacy] python phase5_run.py <tag> <method,method,...> [first last]"""
import json, os, sys
from phase2_scenario_generator import generate_scenarios
from phase5_runner import run_scenario
PARAMS = {
 'HB': {'ants':16,'iterations':20,'label':'a16_i20'},
 'HBP': {'ants':16,'iterations':20,'label':'a16_i20'},
 'DR-T': {'R':3.5,'K':0.5,'ants':12,'iterations':20,'label':'R3.5_K0.5'},
 'DR-SAFE': {'R':3.5,'K':0.5,'D_SAFE':0.75,'ants':12,'iterations':20,'label':'R3.5_K0.5_D0.75'},
 'aco_dwa': {'ants':8,'iterations':10,'clearance_weight':0.1,'goal_weight':1,'label':'a8_i10_c0.1_g1'},
 'aco_dwa_hb': {'ants':8,'iterations':10,'clearance_weight':0.1,'goal_weight':1,'label':'a8_i10_c0.1_g1'},
 'aco_dwa_hbp': {'ants':8,'iterations':10,'clearance_weight':0.1,'goal_weight':1,'label':'a8_i10_c0.1_g1+HBP'},
 'aco_dwa_drt': {'R':3.5,'K':0.5,'ants':8,'iterations':10,'clearance_weight':0.1,'goal_weight':1,'label':'a8_i10_c0.1_g1+R3.5_K0.5'},
}
if __name__ == '__main__':
    tag, methods = sys.argv[1], sys.argv[2].split(',')
    lo, hi = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (4, 203)
    S = generate_scenarios(240)
    out = f'../results/phase5/{tag}.jsonl'
    os.makedirs('../results/phase5', exist_ok=True)
    done = set()
    if os.path.exists(out):
        for l in open(out): d = json.loads(l); done.add((d['scenario_id'], d['method']))
    with open(out, 'a') as f:
        for i in range(lo, hi+1):
            for m in methods:
                if (i, m) in done: continue
                f.write(json.dumps(run_scenario(S[i], m, PARAMS[m], max_ticks=45))+'\n'); f.flush()
