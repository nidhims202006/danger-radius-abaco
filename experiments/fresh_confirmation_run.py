"""Usage: python fresh_confirmation_run.py <arm> [first last]
arm = legacy : HB,HBP,DR-T,DR-SAFE with the age-based deposit + 500-step limit (phase5_runner, ADAPTER=legacy)  [PRIMARY]
arm = flat   : HB,HBP,DR-T,DR-SAFE with the primary flat-deposit adapter (phase5_runner)                        [secondary]
arm = other  : space-time A*, SIPP-style, D* Lite+DWA, ACO+DWA, ORCA, MPC (phase4_runner_orca_mpc)
All settings are frozen in PARAMS below (taken from earlier, already-archived tuning; nothing is tuned on the fresh set).
Resumable; one planner seed per scenario (seed_offset 0), 45 ticks, five-tick scheduled replanning."""
import json, os, sys
arm = sys.argv[1]
if arm == 'legacy': os.environ['ADAPTER'] = 'legacy'
from fresh_confirmation_generator import generate_fresh
if arm in ('legacy', 'flat'):
    from phase5_runner import run_scenario
    METHODS = ['HB', 'HBP', 'DR-T', 'DR-SAFE']
else:
    from phase4_runner_orca_mpc import run_scenario
    METHODS = ['space_time_astar', 'sipp', 'dstar_dwa', 'aco_dwa', 'orca', 'mpc']
PARAMS = {
 'HB': {'ants':16,'iterations':20,'label':'a16_i20'},
 'HBP': {'ants':16,'iterations':20,'label':'a16_i20'},
 'DR-T': {'R':3.5,'K':0.5,'ants':12,'iterations':20,'label':'R3.5_K0.5'},
 'DR-SAFE': {'R':3.5,'K':0.5,'D_SAFE':0.75,'ants':12,'iterations':20,'label':'R3.5_K0.5_D0.75'},
 'space_time_astar': {'horizon':30,'label':'h30'},
 'sipp': {'horizon':30,'label':'h30'},
 'dstar_dwa': {'progress_weight':1,'clearance_weight':0.1,'max_expansions':50,'label':'p1_c0.1'},
 'aco_dwa': {'ants':8,'iterations':10,'clearance_weight':0.1,'goal_weight':1,'label':'a8_i10_c0.1_g1'},
 'orca': {'tau':2.0,'buffer':0.15,'label':'tau2.0_b0.15'},
 'mpc': {'horizon':4,'r_safe':1.5,'w_coll':5.0,'label':'H4_r1.5_w5.0'},
}
if __name__ == '__main__':
    S = generate_fresh()
    lo = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    hi = int(sys.argv[3]) if len(sys.argv) > 3 else len(S) - 1
    out = f'../results/fresh_confirmation/{arm}.jsonl'
    done = set()
    if os.path.exists(out):
        for l in open(out): d = json.loads(l); done.add((d['scenario_id'], d['method']))
    with open(out, 'a') as f:
        for i in range(lo, hi + 1):
            for m in METHODS:
                if (S[i].scenario_id, m) in done: continue
                f.write(json.dumps(run_scenario(S[i], m, PARAMS[m], max_ticks=45)) + '\n'); f.flush()
