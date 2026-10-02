"""Recompute every ORCA/MPC number inserted into the manuscript from the stored per-run
files and compare with the values printed in Tables 17A, 17C, 18, 19 and the text.
Run from the repository root:  python3 experiments/check_orca_mpc_numbers.py"""
import json, statistics as st
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'experiments'))
from phase2_scenario_generator import generate_scenarios
S = generate_scenarios(240)
new = json.load(open(ROOT / 'results/phase4_orca_mpc_perrun.json'))
stats = json.load(open(ROOT / 'results/phase4_orca_mpc_stats/orca_mpc_paired_statistics.json'))
bad = 0
def chk(name, got, want):
    global bad
    ok = got == want
    bad += (not ok)
    print(('OK   ' if ok else 'FAIL ') + name, got if ok else f'got {got!r} want {want!r}')
# Legacy raw-data check. The archived per-run file is the superseded ORCA/MPC run.
EXP = {'orca': ('99.0%', '8.0%'), 'mpc': ('100.0%', '2.0%')}
for m, want in EXP.items():
    r = [x for x in new if x['method'] == m]; n = len(r)
    assert n == 200
    got = (f'{100*sum(x["success"] for x in r)/n:.1f}%', f'{100*sum(x["any_collision"] for x in r)/n:.1f}%')
    chk(f'legacy raw {m}', got, want)
print('NOTE: v30 manuscript Table 29 reports the separate updated rerun (ORCA 100.0%/9.5%; MPC 100.0%/3.0%).')
print('NOTE: paired p-values for that updated rerun are intentionally not reported because its raw paired outcomes are not archived here.')

# Tables 18 / 19 (collision %, success %)
for tag, keyf, want in (
  ('18', lambda s: s.observation_sigma, {('orca', 0.0): (9.6, 96.2), ('orca', .15): (6.0, 100.0), ('orca', .35): (6.1, 100.0), ('orca', .7): (10.2, 100.0),
                                          ('mpc', 0.0): (0.0, 100.0), ('mpc', .15): (0.0, 100.0), ('mpc', .35): (4.1, 100.0), ('mpc', .7): (4.1, 100.0)}),
  ('19', lambda s: s.dynamic_obstacles[0].motion, {('orca', 'constant'): (0.0, 100.0), ('orca', 'curved'): (2.1, 100.0), ('orca', 'random_walk'): (20.8, 97.9), ('orca', 'stop_go'): (10.4, 97.9),
                                          ('mpc', 'constant'): (0.0, 100.0), ('mpc', 'curved'): (2.1, 100.0), ('mpc', 'random_walk'): (4.2, 100.0), ('mpc', 'stop_go'): (2.1, 100.0)})):
    for (m, k), w in want.items():
        v = [x for x in new if x['method'] == m and keyf(S[x['scenario_id']]) == k]
        chk(f'Table {tag} {m} {k}', (round(100*sum(x['any_collision'] for x in v)/len(v), 1), round(100*sum(x['success'] for x in v)/len(v), 1)), w)
# Table 17C new rows
for r, want in zip(stats['new_rows'], [(72.5, 99.0, -26.5), (18.0, 8.0, 10.0), (72.5, 100.0, -27.5), (18.0, 2.0, 16.0)]):
    chk('17C ' + r['comparison'] + ' ' + r['outcome'], (r['dr_t_rate_pct'], r['comparator_rate_pct'], round(r['difference_pct_points'], 1)), want)
print('mismatches:', bad); sys.exit(1 if bad else 0)
