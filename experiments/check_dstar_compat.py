"""Verify the runner-compatible FastDStarLite replacement against stored D* Lite + DWA results.

Usage:
    python3 experiments/check_dstar_compat.py [START END]

The script is location-independent: it can be invoked from the repository root or
from experiments/. The default range is the 200 primary scenarios, 4-203.
"""
import json
import signal
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for p in (HERE, ROOT / "abaco", ROOT / "danger_radius", ROOT / "baselines"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from phase2_scenario_generator import generate_scenarios
import phase3_runner_v2 as R

START = int(sys.argv[1]) if len(sys.argv) > 1 else 4
END = int(sys.argv[2]) if len(sys.argv) > 2 else 203

S = generate_scenarios(240)
with (ROOT / "results/phase2_step3_v2/perrun.json").open() as f:
    stored = {(r["scenario_id"], r["method"]): r for r in json.load(f)}

P = {"progress_weight": 1, "clearance_weight": 0.1, "max_expansions": 50}

class Timeout(Exception):
    pass

def _timeout_handler(*_):
    raise Timeout()

signal.signal(signal.SIGALRM, _timeout_handler)
out = []
for sid in range(START, END + 1):
    expected = stored[(sid, "dstar_dwa")]
    signal.alarm(15)
    try:
        got = R.run_scenario(S[sid], "dstar_dwa", P, max_ticks=45)
        signal.alarm(0)
        same = (
            all(expected[k] == got[k] for k in ("success", "any_collision", "time_to_goal", "turns"))
            and abs(expected["distance"] - got["distance"]) < 1e-9
        )
        out.append({
            "scenario_id": sid,
            "status": "match" if same else "diff",
            "stored_any_collision": expected["any_collision"],
            "rerun_any_collision": got["any_collision"],
            "stored_success": expected["success"],
            "rerun_success": got["success"],
        })
    except Timeout:
        signal.alarm(0)
        out.append({
            "scenario_id": sid,
            "status": "timeout",
            "stored_any_collision": expected["any_collision"],
            "rerun_any_collision": None,
            "stored_success": expected["success"],
            "rerun_success": None,
        })

outpath = ROOT / "results/dstar_compat_check/dstar_compat_check.json"
outpath.parent.mkdir(parents=True, exist_ok=True)
outpath.write_text(json.dumps(out, indent=2))
print(f"DONE: {len(out)} scenarios; matches={sum(x['status']=='match' for x in out)}, "
      f"diffs={sum(x['status']=='diff' for x in out)}, timeouts={sum(x['status']=='timeout' for x in out)}")
