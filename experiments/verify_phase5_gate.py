"""Reproducibility gate for the phase-5 runner (about 1-2 minutes). Run from experiments/ with
PYTHONPATH=../abaco:../danger_radius:../baselines:. (as in run_all.sh) and WITHOUT ADAPTER=legacy.

With the unmodified primary adapter, phase5_runner must reproduce the stored outcomes exactly:
 - HB, HBP, DR-T, DR-SAFE, ACO+DWA on scenarios 4-8 vs results/phase2_step3_v2/perrun.json and phase2_strong_chunks/;
 - the phase-5 'aco_dwa_hb' reimplementation vs the stored ACO+DWA on scenarios 4-8.
Exit code 0 only if every compared run matches.
"""
import glob, json, os, sys
os.environ.pop('ADAPTER', None)
from phase2_scenario_generator import generate_scenarios
from phase5_runner import run_scenario
from phase5_run import PARAMS
R = '../results/'
stored = {(x['method'], x['scenario_id']): x for x in json.load(open(R + 'phase2_step3_v2/perrun.json'))}
for f in glob.glob(R + 'phase2_strong_chunks/*.json'):
    for x in json.load(open(f)):
        if x['method'] == 'aco_dwa': stored[('aco_dwa', x['scenario_id'])] = x
S = generate_scenarios(240)
KEYS = ('success', 'any_collision', 'time_to_goal', 'turns', 'replans')
bad = n = 0
for i in range(4, 9):
    for m in ('HB', 'HBP', 'DR-T', 'DR-SAFE', 'aco_dwa', 'aco_dwa_hb'):
        row = run_scenario(S[i], m, PARAMS[m], max_ticks=45)
        ref = stored[('aco_dwa' if m == 'aco_dwa_hb' else m, i)]
        ok = all(row[k] == ref[k] for k in KEYS) and abs(row['distance'] - ref['distance']) < 1e-9
        n += 1; bad += (not ok)
        if not ok: print('MISMATCH', i, m)
print(f'{n} runs compared; mismatches: {bad}')
sys.exit(1 if bad else 0)
