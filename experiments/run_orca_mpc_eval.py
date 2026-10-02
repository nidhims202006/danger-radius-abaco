"""Post hoc evaluation of ORCA and MPC on the 200 closed-loop scenarios (IDs 4-203),
using the configurations frozen by run_orca_mpc_tuning.py."""
import json, os
from pathlib import Path
from phase2_scenario_generator import generate_scenarios
from phase4_runner_orca_mpc import run_scenario

ROOT = Path(__file__).resolve().parents[1]
TUNE = json.load(open(ROOT / 'results/phase4_orca_mpc_tuning/tuning_summary.json'))
S = generate_scenarios(240)
if __name__ == '__main__':
    rows = []
    for m in ('orca', 'mpc'):
        p = TUNE[m]['best']['params']
        for sid in range(4, 204):
            rows.append(run_scenario(S[sid], m, p, max_ticks=45))
    out = ROOT / 'results'
    json.dump(rows, open(out / 'phase4_orca_mpc_perrun.json', 'w'), indent=2)
    print('wrote', len(rows))
    for m in ('orca', 'mpc'):
        r = [x for x in rows if x['method'] == m]
        n = len(r)
        print(m, 'success %.1f%%' % (100*sum(x['success'] for x in r)/n),
              'any-collision %.1f%%' % (100*sum(x['any_collision'] for x in r)/n),
              'mean plan time/scn %.4fs' % (sum(x['planning_time_s'] for x in r)/n))
