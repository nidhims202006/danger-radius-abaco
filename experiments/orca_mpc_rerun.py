"""Reproducible ORCA/MPC rerun for closed-loop scenarios 4-203.

Run from this directory with the repository modules on PYTHONPATH. Results
append to results/orca_mpc_rerun/perrun.jsonl and can be resumed by rerunning
the script. The existing runner replans on ticks 0, 5, 10, ... (and whenever
there is no planned action); this script intentionally uses that behavior.
"""
from __future__ import annotations

import json
from pathlib import Path

from phase2_scenario_generator import generate_scenarios
from phase4_runner_orca_mpc import run_scenario

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "orca_mpc_rerun" / "perrun.jsonl"
SCENARIO_IDS = range(4, 204)
MAX_TICKS = 45
SEED_OFFSET = 0
METHODS = {
    "orca": {"tau": 1.5, "buffer": 0.10},
    "mpc": {"horizon": 3, "r_safe": 1.5, "w_coll": 5.0},
}


def load_completed(path: Path) -> set[tuple[int, str]]:
    completed: set[tuple[int, str]] = set()
    if not path.exists():
        return completed
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            record = json.loads(line)
            key = (int(record["scenario_id"]), record["method"])
            if key in completed:
                raise ValueError(f"Duplicate completed record at line {line_number}: {key}")
            if key[0] not in SCENARIO_IDS or key[1] not in METHODS:
                raise ValueError(f"Unexpected record at line {line_number}: {key}")
            completed.add(key)
    return completed


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    completed = load_completed(OUT)
    scenarios = [s for s in generate_scenarios(240) if s.scenario_id in SCENARIO_IDS]
    if [s.scenario_id for s in scenarios] != list(SCENARIO_IDS):
        raise AssertionError("Generated scenario IDs do not equal 4..203")

    with OUT.open("a", encoding="utf-8", newline="\n") as stream:
        for scenario in scenarios:
            for method, params in METHODS.items():
                key = (scenario.scenario_id, method)
                if key in completed:
                    continue
                record = run_scenario(
                    scenario,
                    method,
                    params,
                    max_ticks=MAX_TICKS,
                    seed_offset=SEED_OFFSET,
                )
                stream.write(json.dumps(record, allow_nan=False) + "\n")
                stream.flush()
                completed.add(key)
                print(f"completed scenario={scenario.scenario_id} method={method}", flush=True)

    expected = {(scenario_id, method) for scenario_id in SCENARIO_IDS for method in METHODS}
    if completed != expected:
        raise AssertionError(f"Incomplete rerun: {len(completed)}/{len(expected)} records")
    print(f"Complete: {len(completed)} per-run records in {OUT}")


if __name__ == "__main__":
    main()