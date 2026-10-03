"""Paired analysis of the post hoc phase-5 runs (scenario IDs 4-203) against the stored primary results.

Writes results/phase5/phase5_summary.json, hybrid_legacy_tests.json, legacy_drt_vs_other_planners.json
and single_factor_summary.json. All tests: paired, exact two-sided McNemar; Holm within the stated family;
95% CI by 4000-draw paired bootstrap (default_rng(0) per comparison). Run from the experiments/ directory.
"""
import json, glob, numpy as np
from scipy.stats import binomtest
R = '../results/'
IDS = list(range(4, 204))

def jl(p): return {(x['method'], x['scenario_id']): x for x in map(json.loads, open(R + 'phase5/' + p))}
primary = {(x['method'], x['scenario_id']): x for x in json.load(open(R + 'phase2_step3_v2/perrun.json'))}
for f in glob.glob(R + 'phase2_strong_chunks/*.json'):
    for x in json.load(open(f)):
        primary[(x['method'], x['scenario_id'])] = x          # aco_dwa, dstar_dwa, space_time_astar, sipp
legacy, hybrid, hybrid_legacy = jl('legacy.jsonl'), jl('hybrid.jsonl'), jl('hybrid_legacy.jsonl')
cap_only, ageq_only = jl('cap_only.jsonl'), jl('ageq_only.jsonl')

def pick(d, m): return {i: d[(m, i)] for i in IDS}
def rate(d, m, k): return 100 * float(np.mean([d[(m, i)][k] for i in IDS]))

def paired(a, b, k):
    x = np.array([a[i][k] for i in IDS], int); y = np.array([b[i][k] for i in IDS], int)
    n10, n01 = int(((x == 1) & (y == 0)).sum()), int(((x == 0) & (y == 1)).sum())
    p = 1.0 if n10 + n01 == 0 else float(binomtest(n10, n10 + n01, 0.5).pvalue)
    rng = np.random.default_rng(0); d = x - y
    bs = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(4000)]
    return dict(diff=100 * float(d.mean()), lo=100 * float(np.percentile(bs, 2.5)), hi=100 * float(np.percentile(bs, 97.5)), p=p)

def holm(rows):
    ps = np.array([r['p'] for r in rows]); order = np.argsort(ps); run = 0.0
    for rank, i in enumerate(order):
        run = max(run, (len(ps) - rank) * ps[i]); rows[i]['holm'] = float(min(1.0, run))
    return rows

# --- Item 3: legacy-pheromone adapter ---
legacy_rows = {m: dict(method=m, primary_success=rate(primary, m, 'success'), primary_coll=rate(primary, m, 'any_collision'),
                       legacy_success=rate(legacy, m, 'success'), legacy_coll=rate(legacy, m, 'any_collision'),
                       legacy_dist=float(np.mean([legacy[(m, i)]['distance'] for i in IDS])))
               for m in ('HB', 'HBP', 'DR-T', 'DR-SAFE')}
tests = []
for c in ('HB', 'HBP', 'DR-SAFE'):
    for k in ('success', 'any_collision'):
        tests.append(dict(name=f'legacy DR-T vs {c}', outcome=k, **paired(pick(legacy, 'DR-T'), pick(legacy, c), k)))
holm(tests)
# --- Item 2 (flat deposit): ACO+DWA with prediction-aware ACO stage ---
base = pick(primary, 'aco_dwa'); fam = []
for m in ('aco_dwa_hbp', 'aco_dwa_drt'):
    for k in ('success', 'any_collision'):
        fam.append(dict(name=f'{m} vs ACO+DWA', outcome=k, **paired(pick(hybrid, m), base, k)))
for k in ('success', 'any_collision'):
    fam.append(dict(name='aco_dwa_drt vs aco_dwa_hbp', outcome=k, **paired(pick(hybrid, 'aco_dwa_drt'), pick(hybrid, 'aco_dwa_hbp'), k)))
holm(fam); tests += fam
hyb_rows = {}
for m in ('aco_dwa', 'aco_dwa_hbp', 'aco_dwa_drt'):
    d = primary if m == 'aco_dwa' else hybrid
    hyb_rows[m] = dict(success=rate(d, m, 'success'), coll=rate(d, m, 'any_collision'),
                       dist=float(np.mean([d[(m, i)]['distance'] for i in IDS])), clr=float(np.mean([d[(m, i)]['min_clearance'] for i in IDS])))
json.dump(dict(legacy=legacy_rows, hybrid=hyb_rows, tests=tests), open(R + 'phase5/phase5_summary.json', 'w'), indent=1)

# --- Item 2 (age-based deposit), Holm over eight tests ---
g = lambda m: pick(hybrid_legacy, m); rows = []
for a, b, n in (('aco_dwa_drt', 'aco_dwa_hb', 'ACO(DR-T)+DWA vs ACO+DWA'), ('aco_dwa_hbp', 'aco_dwa_hb', 'ACO(HBP)+DWA vs ACO+DWA'),
                ('aco_dwa_drt', 'aco_dwa_hbp', 'ACO(DR-T)+DWA vs ACO(HBP)+DWA')):
    for k in ('success', 'any_collision'): rows.append(dict(name=n, outcome=k, **paired(g(a), g(b), k)))
for k in ('success', 'any_collision'):
    rows.append(dict(name='DR-T(ACO) vs ACO+DWA, both legacy', outcome=k, **paired(pick(legacy, 'DR-T'), g('aco_dwa_hb'), k)))
json.dump(holm(rows), open(R + 'phase5/hybrid_legacy_tests.json', 'w'), indent=1)

# --- legacy-deposit DR-T vs stored non-ACO planners (ORCA/MPC per-run outcomes of the cadence-matched rerun are not archived) ---
rows = []
for c, name in (('aco_dwa', 'ACO+DWA'), ('dstar_dwa', 'D* Lite + DWA'), ('space_time_astar', 'Space-time A*')):
    for k in ('success', 'any_collision'):
        rows.append(dict(comparator=name, outcome=k, **paired(pick(legacy, 'DR-T'), pick(primary, c), k)))
json.dump(holm(rows), open(R + 'phase5/legacy_drt_vs_other_planners.json', 'w'), indent=1)

# --- single-factor DR-T arms ---
sf = {tag: dict(success=rate(d, 'DR-T', 'success'), coll=rate(d, 'DR-T', 'any_collision'), dist=float(np.mean([d[('DR-T', i)]['distance'] for i in IDS])))
      for tag, d in (('primary', primary), ('cap500_only', cap_only), ('ageq_only', ageq_only), ('both', legacy))}
json.dump(sf, open(R + 'phase5/single_factor_summary.json', 'w'), indent=1)
print('wrote phase5_summary.json, hybrid_legacy_tests.json, legacy_drt_vs_other_planners.json, single_factor_summary.json')
