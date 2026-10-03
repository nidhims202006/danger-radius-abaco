"""Analysis of the fresh crossed closed-loop confirmation (protocol: results/fresh_confirmation/PROTOCOL.json).
Writes results/fresh_confirmation/summary.json. Primary family: DR-T(legacy) vs 8 comparators x 2 outcomes,
exact McNemar on paired scenarios, Holm over 16. Everything else is descriptive."""
import json, math, collections
import numpy as np
from scipy import stats
from fresh_confirmation_generator import generate_fresh
R = '../results/fresh_confirmation/'
S = {s.scenario_id: s for s in generate_fresh()}
def load(arm):
    d = {}
    for l in open(R + arm + '.jsonl'):
        r = json.loads(l); d[(r['method'], r['scenario_id'])] = r
    return d
leg, flat, oth = load('legacy'), load('flat'), load('other')
IDS = sorted(S)
for nm, d, ms in (('legacy', leg, ['HB','HBP','DR-T','DR-SAFE']), ('flat', flat, ['HB','HBP','DR-T','DR-SAFE']),
                  ('other', oth, ['space_time_astar','sipp','dstar_dwa','aco_dwa','orca','mpc'])):
    assert all((m, i) in d for m in ms for i in IDS), f'{nm} incomplete'
ARMS = {'HB': leg, 'HBP': leg, 'DR-T': leg, 'DR-SAFE': leg}
NAMES = [('DR-T (age-based deposit)', 'DR-T', leg), ('HB (age-based)', 'HB', leg), ('HBP (age-based)', 'HBP', leg), ('DR-SAFE (age-based)', 'DR-SAFE', leg),
         ('DR-T (flat deposit)', 'DR-T', flat), ('HB (flat)', 'HB', flat), ('HBP (flat)', 'HBP', flat), ('DR-SAFE (flat)', 'DR-SAFE', flat),
         ('Space-time A*', 'space_time_astar', oth), ('SIPP-style', 'sipp', oth), ('D* Lite + DWA', 'dstar_dwa', oth),
         ('ACO+DWA', 'aco_dwa', oth), ('ORCA', 'orca', oth), ('MPC', 'mpc', oth)]
def vec(d, m, k): return np.array([bool(d[(m, i)][k]) for i in IDS])
def mcnemar(a, b):
    n01 = int(np.sum(~a & b)); n10 = int(np.sum(a & ~b)); n = n01 + n10
    p = 1.0 if n == 0 else min(1.0, 2 * stats.binom.cdf(min(n01, n10), n, 0.5))
    return n10, n01, p
def holm(rows):
    order = sorted(range(len(rows)), key=lambda i: rows[i]['p']); m = len(rows); run = 0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (m - rank) * rows[i]['p'])); rows[i]['holm_p'] = run
    return rows
out = {'n': len(IDS)}
summ = []
for label, m, d in NAMES:
    s = vec(d, m, 'success'); c = vec(d, m, 'any_collision')
    dist = float(np.mean([d[(m, i)]['distance'] for i in IDS]))
    pt = float(np.mean([d[(m, i)]['planning_time_s'] for i in IDS]))
    summ.append(dict(label=label, success=100*s.mean(), any_collision=100*c.mean(), mean_path=dist, mean_plan_s=pt))
out['summary'] = summ
prim = []
base = vec(leg, 'DR-T', 'success'), vec(leg, 'DR-T', 'any_collision')
for label, m, d in NAMES:
    if label in ('DR-T (age-based deposit)',) or 'flat' in label or label in ('DR-SAFE (age-based)',): continue
    for k, bv in zip(('success', 'any_collision'), base):
        o = vec(d, m, k); a_only, b_only, p = mcnemar(bv, o)
        prim.append(dict(comparator=label, outcome=k, drt_only=a_only, comp_only=b_only, diff_pp=100*(bv.mean()-o.mean()), p=p))
out['primary_family'] = holm(prim)
sec = []
for label, m, d in (('DR-SAFE (age-based)','DR-SAFE',leg),):
    for k in ('success','any_collision'):
        a_only,b_only,p = mcnemar(vec(leg,'DR-T',k), vec(d,m,k)); sec.append(dict(comparator=label, outcome=k, drt_only=a_only, comp_only=b_only, diff_pp=100*(vec(leg,'DR-T',k).mean()-vec(d,m,k).mean()), p=p))
for k in ('success','any_collision'):
    a_only,b_only,p = mcnemar(vec(flat,'DR-T',k), vec(flat,'HB',k)); sec.append(dict(comparator='flat-deposit: DR-T vs HB', outcome=k, drt_only=a_only, comp_only=b_only, diff_pp=100*(vec(flat,'DR-T',k).mean()-vec(flat,'HB',k).mean()), p=p))
out['secondary'] = holm(sec)
# subgroup tables (descriptive); crossed design allows separate marginals
def grp(fn):
    g = collections.defaultdict(list)
    for i in IDS: g[fn(S[i])].append(i)
    return g
factors = {'motion': lambda s: s.dynamic_obstacles[0].motion, 'dyn_count': lambda s: len(s.dynamic_obstacles),
           'noise': lambda s: s.observation_sigma, 'workspace': lambda s: f'{s.rows}x{s.cols}', 'density': lambda s: s.static_density}
sub = {}
for fname, fn in factors.items():
    g = grp(fn); sub[fname] = {}
    for lvl, ids in sorted(g.items(), key=lambda x: str(x[0])):
        sub[fname][str(lvl)] = {'n': len(ids)}
        for label, m, d in NAMES:
            if label in ('DR-T (age-based deposit)','HB (age-based)','HBP (age-based)','ACO+DWA','Space-time A*','ORCA','MPC','D* Lite + DWA'):
                sub[fname][str(lvl)][label] = dict(any_collision=100*np.mean([bool(d[(m,i)]['any_collision']) for i in ids]),
                                                     success=100*np.mean([bool(d[(m,i)]['success']) for i in ids]))
out['subgroups'] = sub
# motion x count cross-tab for DR-T collision
cross = collections.defaultdict(list)
for i in IDS: cross[(S[i].dynamic_obstacles[0].motion, len(S[i].dynamic_obstacles))].append(bool(leg[('DR-T', i)]['any_collision']))
out['drt_collision_motion_x_count'] = {f'{k[0]}|{k[1]}': [len(v), 100*float(np.mean(v))] for k, v in sorted(cross.items())}
json.dump(out, open(R + 'summary.json', 'w'), indent=1, default=float)
for r in summ: print(f"{r['label']:28s} succ {r['success']:5.1f}  coll {r['any_collision']:5.1f}  path {r['mean_path']:.1f}  plan {r['mean_plan_s']:.3f}s")
print()
for r in out['primary_family']: print(f"{r['comparator']:26s} {r['outcome']:14s} diff {r['diff_pp']:+6.1f}pp  {r['drt_only']}/{r['comp_only']}  p={r['p']:.4f} holm={r['holm_p']:.4f}")
print(); 
for r in out['secondary']: print(r)
