"""analyze_fallback.py -- summarise results/fallback_audit.json; check it reproduces the stored fallback counts; write results/fallback_summary.json."""
import json, os
import numpy as np
import drsafe_lib as L
R = L.RESULTS_DIR
au = json.load(open(os.path.join(R, "fallback_audit.json")))["runs"]; fr = json.load(open(os.path.join(R, "fresh_main.json")))["runs"]
seeds = [s for s in sorted(au, key=int) if "TA" in au[s] and "TB" in au[s]]
out = {"n_seeds": len(seeds)}
for arm in ("TA", "TB"):
    a = [au[s][arm] for s in seeds]
    match = all(au[s][arm]["fb"] == fr[s][arm]["fb"] for s in seeds)
    calls = np.array([x["calls"] for x in a], float); fb = np.array([x["fb"] for x in a], float)
    cons = np.array([x["constructs"] for x in a], float); consfb = np.array([x["constructs_fb"] for x in a], float)
    ok = [x for x in a if x["best_fb"] is not None]
    bfb = np.array([x["best_fb"] for x in ok], float); bst = np.array([x["best_steps"] for x in ok], float)
    coll = np.array([fr[s][arm]["coll"] for s in seeds if au[s][arm]["best_fb"] is not None], float)
    r = dict(reproduces_stored_fb=bool(match), selection_calls_per_run=calls.mean(), fallbacks_per_run=fb.mean(),
             fallback_share_of_selection_steps_pooled=fb.sum() / calls.sum(), fallback_share_per_run_mean=float((fb / calls).mean()),
             constructions_per_run=cons.mean(), share_constructions_with_fallback=consfb.sum() / cons.sum(),
             runs_best_path_has_fallback=int((bfb > 0).sum()), runs_total=len(ok), share_runs_best_path_has_fallback=float((bfb > 0).mean()),
             mean_fallback_steps_on_best_path=float(bfb.mean()), share_of_steps_on_best_path_fallback=float(bfb.sum() / bst.sum()),
             collision_runs=int((coll > 0).sum()), collision_runs_with_best_fb=int(((coll > 0) & (bfb > 0)).sum()),
             collision_rate_best_fb=float((coll[bfb > 0] > 0).mean()) if (bfb > 0).any() else None,
             collision_rate_best_nofb=float((coll[bfb == 0] > 0).mean()) if (bfb == 0).any() else None)
    out[arm] = r
    print(arm, json.dumps({k: (round(v, 5) if isinstance(v, float) else v) for k, v in r.items()}, indent=1))
json.dump(out, open(os.path.join(R, "fallback_summary.json"), "w"), indent=1)
