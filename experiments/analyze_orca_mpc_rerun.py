"""Summarize the ORCA/MPC rerun and paired comparisons against primary DR-T."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from analyze_a3_paired_statistics import (
    PRIMARY,
    SCENARIOS,
    bootstrap_ci,
    holm,
    index,
    mcnemar_exact,
)

ROOT = Path(__file__).resolve().parents[1]
RUNS_PATH = ROOT / "results" / "orca_mpc_rerun" / "perrun.jsonl"
SUMMARY_PATH = ROOT / "results" / "orca_mpc_rerun" / "summary.json"
DR_T_SOURCE = "results/phase2_step3_v2/perrun.json"
METHODS = ("orca", "mpc")
OUTCOMES = ("success", "any_collision")


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def main() -> None:
    rerun_rows = load_jsonl(RUNS_PATH)
    rerun = index(rerun_rows)
    dr_t = index(json.loads(PRIMARY.read_text(encoding="utf-8")))
    expected = set(SCENARIOS)

    for method in METHODS:
        ids = {scenario_id for scenario_id, found_method in rerun if found_method == method}
        if ids != expected:
            raise AssertionError(f"{method} scenarios differ from 4..203: {sorted(ids ^ expected)}")
    if len(rerun) != len(rerun_rows):
        raise AssertionError("Duplicate (scenario_id, method) entries in rerun JSONL")
    dr_t_ids = {scenario_id for scenario_id, method in dr_t if method == "DR-T"}
    if dr_t_ids != expected:
        raise AssertionError(f"Primary DR-T source coverage differs from 4..203: {sorted(dr_t_ids ^ expected)}")

    method_summary = {}
    for method in METHODS:
        rows = [rerun[(scenario_id, method)] for scenario_id in SCENARIOS]
        method_summary[method] = {
            "n": len(rows),
            "success_pct": float(100 * np.mean([bool(row["success"]) for row in rows])),
            "any_collision_pct": float(100 * np.mean([bool(row["any_collision"]) for row in rows])),
            "mean_path_length": float(np.mean([row["distance"] for row in rows])),
            "mean_min_clearance": float(np.mean([row["min_clearance"] for row in rows])),
            "mean_planning_time_s": float(np.mean([row["planning_time_s"] for row in rows])),
        }

    paired_rows = []
    for method_index, method in enumerate(METHODS):
        for outcome_index, outcome in enumerate(OUTCOMES):
            a = np.array([bool(dr_t[(scenario_id, "DR-T")][outcome]) for scenario_id in SCENARIOS])
            b = np.array([bool(rerun[(scenario_id, method)][outcome]) for scenario_id in SCENARIOS])
            difference = a.astype(float) - b.astype(float)
            p_value, drt_0_method_1, drt_1_method_0 = mcnemar_exact(a, b)
            ci = bootstrap_ci(difference, 2000 + 2 * method_index + outcome_index)
            paired_rows.append({
                "comparison": f"DR-T vs {method.upper()}",
                "outcome": "success" if outcome == "success" else "any_collision",
                "n": len(SCENARIOS),
                "dr_t_rate_pct": float(100 * a.mean()),
                "comparator_rate_pct": float(100 * b.mean()),
                "difference_pct_points": float(100 * difference.mean()),
                "bootstrap_ci95_pct_points": [float(100 * ci[0]), float(100 * ci[1])],
                "mcnemar_exact_p": p_value,
                "discordant_dr_t_0_comparator_1": drt_0_method_1,
                "discordant_dr_t_1_comparator_0": drt_1_method_0,
            })

    for row, adjusted_p in zip(paired_rows, holm([row["mcnemar_exact_p"] for row in paired_rows])):
        row["holm_p_family_of_4"] = float(adjusted_p)

    summary = {
        "scenario_ids": [SCENARIOS[0], SCENARIOS[-1]],
        "n_scenarios": len(SCENARIOS),
        "methods": method_summary,
        "paired_dr_t_comparisons": paired_rows,
        "dr_t_source": DR_T_SOURCE,
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(f"DR-T paired source: {DR_T_SOURCE}")
    print("METHOD SUMMARY: success % | any-collision % | mean path | mean min-clearance | mean planning seconds")
    for method in METHODS:
        row = method_summary[method]
        print(f"{method.upper():4s} {row['success_pct']:5.1f} | {row['any_collision_pct']:5.1f} | "
              f"{row['mean_path_length']:.3f} | {row['mean_min_clearance']:.3f} | {row['mean_planning_time_s']:.6f}")
    print("PAIRED DR-T COMPARISONS (difference = DR-T minus comparator; Holm family of 4)")
    for row in paired_rows:
        lo, hi = row["bootstrap_ci95_pct_points"]
        print(f"{row['comparison']:14s} {row['outcome']:13s} DR-T {row['dr_t_rate_pct']:5.1f}% vs "
              f"{row['comparator_rate_pct']:5.1f}% diff {row['difference_pct_points']:+5.1f} pp "
              f"CI [{lo:+5.1f}, {hi:+5.1f}] p={row['mcnemar_exact_p']:.6g} "
              f"Holm4={row['holm_p_family_of_4']:.6g}")
    print(f"Summary written to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()