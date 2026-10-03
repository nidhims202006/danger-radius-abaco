"""analyze_continuous_cost.py -- analysis of the continuous-cost replication (protocol: results/continuous_cost/PROTOCOL.json).
Arms with the boundary-continuous cost: DR-T (SOFT), DR-SAFE-T 1.0 (TA), DR-SAFE-T 1.5 (TB), versus the unchanged HB and HBP and versus the same arms with the
truncated cost. Outcomes: start-excluded collisions per run (primary), sharp turns, path length, min. clearance. Wilcoxon signed-rank, Holm over 12 per outcome
(3 arms x 2 references x 2 blocks). Writes results/continuous_cost/summary.json."""
import json, os
import numpy as np
import drsafe_lib as L
from analyze_confirmatory import paired_stats, holm
R = L.RESULTS_DIR
J = lambda f: json.load(open(os.path.join(R, f)))['runs']
dn, do, ab, fr = J('main_new_arms.json'), J('confirmatory_perrun.json'), J('ablation_main.json'), J('fresh_main.json')
cc = {'dev': J('continuous_cost/dev.json'), 'conf': J('continuous_cost/conf.json')}
trunc = {'dev': {'HB': lambda s: do[s]['HB'], 'HBP': lambda s: dn[s]['HBP'], 'DRT': lambda s: ab[s]['SOFT'], 'TA': lambda s: dn[s]['TA'], 'TB': lambda s: dn[s]['TB']},
         'conf': {a: (lambda s, a=a: fr[s][a]) for a in ('HB', 'HBP', 'TA', 'TB')}}
trunc['conf']['DRT'] = lambda s: fr[s]['SOFT']
_c = {}
def n_start(conv):
    if conv not in _c:
        real = L.real_obstacles_at(conv)
        _c[conv] = sum(L.base.dist((0, 0), o.traj[min(conv, len(o.traj) - 1)]) < 0.5 for o in real)
    return _c[conv]
OUT = {}; rows = {k: [] for k in ('adj', 'turns', 'len', 'clear')}
data = {}
for b in ('dev', 'conf'):
    seeds = sorted(cc[b], key=int); assert len(seeds) == 300, (b, len(seeds)); data[b] = {}
    get = {'HB': trunc[b]['HB'], 'HBP': trunc[b]['HBP'], 'DRT_t': trunc[b]['DRT'], 'TA_t': trunc[b]['TA'], 'TB_t': trunc[b]['TB'],
           'DRT_c': lambda s, b=b: cc[b][s]['SOFT'], 'TA_c': lambda s, b=b: cc[b][s]['TA'], 'TB_c': lambda s, b=b: cc[b][s]['TB']}
    for a, f in get.items():
        rec = [f(s) for s in seeds]; assert all(r['ok'] for r in rec), (b, a)
        coll = np.array([r['coll'] for r in rec], float); st = np.array([n_start(int(r['conv'])) for r in rec])
        data[b][a] = dict(adj=coll - st, raw=coll, turns=np.array([r['turns'] for r in rec], float), len=np.array([r['len'] for r in rec], float),
                          clear=np.array([r['clear'] for r in rec], float), conv=np.array([r['conv'] for r in rec], float), fb=np.array([r['fb'] for r in rec], float))
    OUT[b] = {'means': {a: {k: float(v.mean()) for k, v in d.items()} for a, d in data[b].items()}}
for k in rows:
    for b in ('dev', 'conf'):
        for t in ('DRT_c', 'TA_c', 'TB_c'):
            for ref in ('HB', 'HBP'):
                rows[k].append((b, t, ref, paired_stats(data[b][ref][k], data[b][t][k])))
    h = holm([r[3]['p_wilcoxon'] for r in rows[k]])
    for r, hp in zip(rows[k], h): r[3]['p_holm'] = float(hp)
OUT['vs_reference'] = {k: {f'{b}|{t}-{ref}': s for b, t, ref, s in rows[k]} for k in rows}
OUT['continuous_vs_truncated'] = {}
for b in ('dev', 'conf'):
    for a in ('DRT', 'TA', 'TB'):
        OUT['continuous_vs_truncated'][f'{b}|{a}'] = {k: paired_stats(data[b][a + '_t'][k], data[b][a + '_c'][k]) for k in ('adj', 'turns', 'len')}
json.dump(OUT, open(os.path.join(R, 'continuous_cost', 'summary.json'), 'w'), indent=1, default=float)
nm = {'HB': 'HB', 'HBP': 'HBP', 'DRT_t': 'DR-T trunc', 'DRT_c': 'DR-T cont', 'TA_t': 'DS1.0 trunc', 'TA_c': 'DS1.0 cont', 'TB_t': 'DS1.5 trunc', 'TB_c': 'DS1.5 cont'}
for b in ('dev', 'conf'):
    print(f'\n[{b}] mean per run: start-excl coll | sharp turns | path len | min clear | fallback')
    for a in nm: m = OUT[b]['means'][a]; print(f"  {nm[a]:12s} {m['adj']:.3f} | {m['turns']:.2f} | {m['len']:.2f} | {m['clear']:.2f} | {m['fb']:.0f}")
for k in ('adj', 'turns', 'len'):
    print(f'\nvs reference, {k} (cont - ref), Holm over 12')
    for b, t, ref, s in rows[k]: print(f"  {b:4} {t}-{ref:3} {s['diff']:+.3f} [{s['diff_ci'][0]:+.3f},{s['diff_ci'][1]:+.3f}] p_W {s['p_wilcoxon']:.4f} Holm {s['p_holm']:.4f}")
print('\ncontinuous - truncated (same arm, same seeds)')
for key, v in OUT['continuous_vs_truncated'].items():
    print(' ', key, {k: f"{s['diff']:+.3f} (p {s['p_wilcoxon']:.3f})" for k, s in v.items()})
