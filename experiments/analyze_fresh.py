"""
analyze_fresh.py -- analysis of the fresh-seed confirmation (results/fresh_main.json, seeds 20000-20299),
exactly as declared in docs/FRESH_SEED_PROTOCOL.md. Writes results/fresh_summary.json.
Primary family (Holm over 8): {collisions/run, sharp turns} x {DR-SAFE 1.0 (TA), 1.5 (TB)} x {HB, HBP}.
Secondary families (Holm over 8 each): TA/TB vs SOFT and vs floor-only (F10/F15); TA/TB vs APFP and APFS.
Also: runs with >=1 collision (exact McNemar), collisions excluding the start waypoint.
"""
import json, os
import numpy as np
import drsafe_lib as L
from analyze_confirmatory import paired_stats, holm, mcnemar_exact

ck = json.load(open(os.path.join(L.RESULTS_DIR, "fresh_main.json")))["runs"]
seeds_all = sorted(ck, key=int)
have = lambda a: all(a in ck[s] for s in seeds_all)
ARMS = [a for a in ("HB", "HBP", "DR", "TA", "TB", "SOFT", "F10", "F15", "DRS", "APFS", "APFP") if have(a)]
seeds = [s for s in seeds_all if all(ck[s][a]["ok"] for a in ARMS)]
print(f"seeds present: {len(seeds_all)}; all-arms-successful: {len(seeds)}; arms: {ARMS}")
g = lambda a, m: np.array([ck[s][a][m] for s in seeds], float)

_cache = {}
def n_start(conv):
    if conv not in _cache:
        real = L.real_obstacles_at(conv)
        _cache[conv] = sum(L.base.dist((0, 0), o.traj[min(conv, len(o.traj) - 1)]) < 0.5 for o in real)
    return _cache[conv]
adj = {a: np.array([ck[s][a]["coll"] - n_start(ck[s][a]["conv"]) for s in seeds], float) for a in ARMS}

out = {"n": len(seeds), "arms": {}, "primary": {}, "secondary": {}}
print(f"\n{'arm':5} {'len':>6} {'turns':>6} {'clear':>6} {'coll/run':>8} {'events':>6} {'runs>=1':>7} {'adj coll':>8} {'adj runs':>8} {'fb/run':>8}")
for a in ARMS:
    c = g(a, "coll")
    out["arms"][a] = dict(len=g(a, "len").mean(), turns=g(a, "turns").mean(), clear=g(a, "clear").mean(), coll=c.mean(),
                          events=int(c.sum()), runs_ge1=int((c > 0).sum()), adj_coll=adj[a].mean(), adj_runs_ge1=int((adj[a] > 0).sum()),
                          fb=g(a, "fb").mean())
    o = out["arms"][a]
    print(f"{a:5} {o['len']:6.2f} {o['turns']:6.2f} {o['clear']:6.3f} {o['coll']:8.3f} {o['events']:6d} {o['runs_ge1']:7d} {o['adj_coll']:8.3f} {o['adj_runs_ge1']:8d} {o['fb']:8.1f}")

def family(title, pairs, metrics=("coll", "turns")):
    """pairs: list of (ref, target). Holm over len(pairs)*len(metrics)."""
    rows = []
    for ref, t in pairs:
        if ref not in ARMS or t not in ARMS:
            continue
        for m in metrics:
            s = paired_stats(g(ref, m), g(t, m)); rows.append((m, t, ref, s))
    if not rows:
        return
    h = holm([r[3]["p_wilcoxon"] for r in rows])
    print(f"\n{title} (Holm over {len(rows)}); difference = target - reference")
    for (m, t, ref, s), hp in zip(rows, h):
        s["p_holm"] = float(hp)
        print(f"  {m:5} {t:5}-{ref:5}: {s['diff']:+8.3f} [{s['diff_ci'][0]:+.3f},{s['diff_ci'][1]:+.3f}] d_z {s['dz']:+.2f} p_W {s['p_wilcoxon']:.4f} Holm {hp:.4f}")
        out["primary" if title.startswith("PRIMARY") else "secondary"][f"{title.split(':')[0]}|{m}|{t}-{ref}"] = s

family("PRIMARY: DR-SAFE vs HB / HBP", [(r, t) for t in ("TA", "TB") for r in ("HB", "HBP")])
family("ABLATION: DR-SAFE vs soft-only / floor-only", [("SOFT", "TA"), ("SOFT", "TB"), ("F10", "TA"), ("F15", "TB")])
family("APF: DR-SAFE vs APF", [(r, t) for t in ("TA", "TB") for r in ("APFS", "APFP")])

print("\nSecondary (unadjusted): length, clearance; any-collision McNemar; start-excluded collisions")
for ref in ("HB", "HBP"):
    for t in ("TA", "TB"):
        s_len = paired_stats(g(ref, "len"), g(t, "len")); s_cl = paired_stats(g(ref, "clear"), g(t, "clear"))
        n10, n01, pm = mcnemar_exact(g(ref, "coll"), g(t, "coll"))
        s_adj = paired_stats(adj[ref], adj[t])
        out["secondary"][f"sec|{t}-{ref}"] = dict(len=s_len, clear=s_cl, mcnemar=dict(only_ref=n10, only_target=n01, p=pm), adj_coll=s_adj)
        print(f"  {t}-{ref}: len {s_len['diff']:+.2f} (p {s_len['p_wilcoxon']:.4f}) | clear {s_cl['diff']:+.2f} (p {s_cl['p_wilcoxon']:.4f}) | "
              f"McNemar ref-only {n10} target-only {n01} p {pm:.4f} | start-excluded coll {s_adj['diff']:+.3f} [{s_adj['diff_ci'][0]:+.3f},{s_adj['diff_ci'][1]:+.3f}] p_W {s_adj['p_wilcoxon']:.4f}")
json.dump(out, open(os.path.join(L.RESULTS_DIR, "fresh_summary.json"), "w"), indent=1, default=float)
