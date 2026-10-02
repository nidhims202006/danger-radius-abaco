"""Regression check: phase4 runner reproduces stored per-run results for
existing methods (all fields except wall-clock planning time)."""
import json, sys
from pathlib import Path
from phase2_scenario_generator import generate_scenarios
from phase4_runner_orca_mpc import run_scenario
R = Path(__file__).resolve().parents[1] / "results"
S = generate_scenarios(240)
strong = {(r['scenario_id'], r['method']): r for r in json.load(open(R/'phase2_strong_baselines_perrun.json'))}
n = bad = 0
FIELDS = ['any_collision','time_to_goal','success','distance','min_clearance','turns','replans']
for sid in range(4, 4 + int(sys.argv[1]) if len(sys.argv) > 1 else 40):
    for m in ('sipp', 'aco_dwa'):
        ref = strong[(sid, m)]
        new = run_scenario(S[sid], m, ref['params'], max_ticks=45)
        n += 1
        for f in FIELDS:
            a, b = new[f], ref[f]
            same = abs(a-b) < 1e-9 if isinstance(a, float) and b is not None else a == b
            if not same:
                bad += 1; print('MISMATCH', sid, m, f, a, b); break
print(f'checked {n} runs, mismatching runs: {bad}')
