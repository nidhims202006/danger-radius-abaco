"""Equal-budget tuning for the post hoc ORCA and MPC baselines.

Same protocol as run_phase2_strong_tuning.py: six candidate configurations per
method, evaluated on the same four reserved tuning scenarios (IDs 0-3), same
selection rule: minimise 0.5*any_collision_rate + 0.5*median_time_to_goal/45,
failures scored as 45 ticks.  Ties are broken by listing order.  The candidate
grids below were fixed before any of the 200 evaluation scenarios was run.
"""
import json, os, statistics
from pathlib import Path
from phase2_scenario_generator import generate_scenarios
from phase4_runner_orca_mpc import run_scenario

C = {
 'orca': [{'tau': t, 'buffer': b, 'label': f'tau{t}_b{b}'}
          for t, b in ((2.0, .15), (3.0, .15), (4.0, .15), (2.0, .4), (3.0, .4), (4.0, .4))],
 'mpc':  [{'horizon': h, 'r_safe': r, 'w_coll': w, 'label': f'H{h}_r{r}_w{w}'}
          for h, r, w in ((4, 1.5, 5.0), (6, 1.5, 5.0), (8, 1.5, 5.0),
                          (4, 2.0, 10.0), (6, 2.0, 10.0), (8, 2.0, 10.0))],
}
SS = generate_scenarios(240)[:4]

def score(rows):
    cr = sum(r['any_collision'] for r in rows) / len(rows)
    tm = statistics.median([r['time_to_goal'] if r['time_to_goal'] is not None else 45 for r in rows])
    return .5 * cr + .5 * tm / 45, cr, tm

if __name__ == '__main__':
    summary = {}
    for m, ps in C.items():
        cand = []
        for p in ps:
            rows = [run_scenario(s, m, p, max_ticks=45) for s in SS]
            a, b, c = score(rows)
            cand.append({'method': m, 'params': p, 'score': a, 'collision_rate': b,
                         'median_time_to_goal': c, 'n': 4})
            print('candidate', m, p['label'], 'score', round(a, 4), 'coll', b, 'median_t', c, flush=True)
        cs = sorted(cand, key=lambda x: x['score'])  # stable: ties -> listing order
        summary[m] = {'best': cs[0], 'candidates': cand}
        print('BEST', m, cs[0]['params']['label'], flush=True)
    out = Path(__file__).resolve().parents[1] / 'results' / 'phase4_orca_mpc_tuning'
    os.makedirs(out, exist_ok=True)
    json.dump(summary, open(out / 'tuning_summary.json', 'w'), indent=2)
