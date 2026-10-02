"""
fallback_audit.py -- how often is the DR-SAFE hard floor actually relaxed, per selection step and on the winning path?
Instruments (counts only; no change to any random draw or decision) the planner's transition function and construction routine
for DR-SAFE at D_SAFE 1.0 (TA) and 1.5 (TB), R=4.5, K=2.0, on the confirmation seeds 20000-20299. Reproduces results/fresh_main.json
fallbacks exactly (checked in analyze_fallback.py). Output: results/fallback_audit.json (resumable, per seed).
Per run: selection calls, fallback count, constructions, constructions with >=1 fallback, and for the winning path: the fallback count and
number of selection steps in the construction that first produced it.
"""
import json, os, sys
import drsafe_lib as L
import ABACO_safety_pred as P

OUT = os.path.join(L.RESULTS_DIR, "fallback_audit.json")
ck = L.load_ckpt(OUT, {"meta": dict(seeds="20000-20299", arms={"TA": 1.0, "TB": 1.5}, R=4.5, K=2.0), "runs": {}})
cnt = {"calls": 0}
rec = []
_orig_tp, _orig_construct = P._trans_prob_pred, P._construct

def counted_tp(*a, **k):
    cnt["calls"] += 1
    return _orig_tp(*a, **k)

def counted_construct(*a, **k):
    f0, c0 = P.FALLBACK, cnt["calls"]
    res = _orig_construct(*a, **k)
    rec.append((tuple(res[0]) if res[0] else None, P.FALLBACK - f0, cnt["calls"] - c0))
    return res

P._trans_prob_pred, P._construct = counted_tp, counted_construct
for i, s in enumerate(range(20000, 20300)):
    row = ck["runs"].setdefault(str(s), {})
    for arm, d in (("TA", 1.0), ("TB", 1.5)):
        if arm in row:
            continue
        cnt["calls"] = 0; rec.clear()
        r = P.run_abaco_safety_pred(L.GRID, s, d_safe=d, R=4.5, K=2.0)
        best = tuple(r["best_path"]) if r["best_path"] else None
        first = next((x for x in rec if x[0] == best), None) if best else None
        row[arm] = dict(fb=int(r["safety_fallback_count"]), calls=cnt["calls"], constructs=len(rec),
                        constructs_fb=sum(1 for x in rec if x[1] > 0), constructs_ok=sum(1 for x in rec if x[0] is not None),
                        best_len_steps=(len(best) - 1 if best else None), best_fb=(first[1] if first else None),
                        best_steps=(first[2] if first else None), best_matches=(sum(1 for x in rec if x[0] == best) if best else 0),
                        best_any_fb=(any(x[1] > 0 for x in rec if x[0] == best) if best else None))
    L.save_ckpt(OUT, ck)
    if (i + 1) % 10 == 0:
        print(s, f"{i+1}/300", flush=True)
print("complete")
