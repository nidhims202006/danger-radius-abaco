"""Generate the 40 additional held-out closed-loop audit scenarios (IDs 204-243).

The primary pool contains scenarios 0-239.  The fresh audit deliberately extends
that deterministic generator to IDs 204-243 as a separate held-out block; this
script records their scenario definitions and a SHA256 manifest without running
any planner.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from phase2_scenario_generator import generate_scenarios

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "fresh_audit_scenarios"
OUT.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    scenarios = generate_scenarios(244)
    selected = [s for s in scenarios if 204 <= s.scenario_id <= 243]
    payload = [s.to_dict() for s in selected]
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    (OUT / "scenarios_204_243.json").write_bytes(data)
    manifest = {
        "count": len(selected),
        "scenario_ids": [s.scenario_id for s in selected],
        "generator": "experiments/phase2_scenario_generator.py",
        "base_seed": 820000,
        "sha256": hashlib.sha256(data).hexdigest(),
        "status": "held-out audit scenario definitions; no planner results",
    }
    (OUT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
