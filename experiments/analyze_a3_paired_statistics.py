"""A3: paired closed-loop statistics for the 200-scenario confirmation set.

Post hoc family: 5 DR-T comparisons x 2 binary outcomes = 10 tests.
Unit: scenario (IDs 4--203), paired across methods.
Outcomes: success and any-collision indicator.
Inference: exact two-sided McNemar tests; Holm correction across all 10 tests.
Uncertainty: 95% percentile bootstrap CI for the paired mean difference,
reported in percentage points, with 4,000 resamples.

The A1 shifted-index DR-T vs HBP analysis is reported separately and is not
included in the 10-test Holm family.

Run from repository root:
    python experiments/analyze_a3_paired_statistics.py
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT = RESULTS / "a3_paired_statistics"
OUT.mkdir(parents=True, exist_ok=True)

PRIMARY = RESULTS / "phase2_step3_v2" / "perrun.json"
STRONG = RESULTS / "phase2_strong_baselines_perrun.json"
SHIFTED = RESULTS / "a1_sensitivity" / "perrun_v3.json"
BOOTSTRAP_REPS = 4000
SCENARIOS = list(range(4, 204))

COMPARISONS = [
    ("DR-T", "HBP"),
    ("DR-T", "HB"),
    ("DR-T", "DR-SAFE"),
    ("DR-T", "aco_dwa"),
    ("DR-T", "dstar_dwa"),
]
DISPLAY = {"aco_dwa": "ACO+DWA", "dstar_dwa": "D* Lite+DWA"}


def load(path: Path):
    with path.open() as f:
        return json.load(f)


def index(rows):
    return {(r["scenario_id"], r["method"]): r for r in rows}


def bootstrap_ci(diff, seed):
    diff = np.asarray(diff, dtype=float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(diff), size=(BOOTSTRAP_REPS, len(diff)))
    means = diff[idx].mean(axis=1)
    return np.percentile(means, [2.5, 97.5]).tolist()


def mcnemar_exact(a, b):
    a = np.asarray(a, dtype=bool)
    b = np.asarray(b, dtype=bool)
    a0_b1 = int(((~a) & b).sum())
    a1_b0 = int((a & (~b)).sum())
    n = a0_b1 + a1_b0
    p = float(binomtest(a0_b1, n, 0.5).pvalue) if n else 1.0
    return p, a0_b1, a1_b0


def holm(p_values):
    p_values = np.asarray(p_values, dtype=float)
    order = np.argsort(p_values)
    adjusted = np.empty(len(p_values), dtype=float)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (len(p_values) - rank) * p_values[i])
        adjusted[i] = min(1.0, running)
    return adjusted.tolist()


def row(primary, comparator, source, outcome, seed):
    a = np.array([bool(primary[(s, "DR-T")][outcome]) for s in SCENARIOS])
    b = np.array([bool(source[(s, comparator)][outcome]) for s in SCENARIOS])
    diff = a.astype(float) - b.astype(float)
    p, a0_b1, a1_b0 = mcnemar_exact(a, b)
    ci = bootstrap_ci(diff, seed)
    return {
        "comparison": f"DR-T vs {DISPLAY.get(comparator, comparator)}",
        "outcome": "success" if outcome == "success" else "collision",
        "n": len(SCENARIOS),
        "dr_t_rate_pct": float(100 * a.mean()),
        "comparator_rate_pct": float(100 * b.mean()),
        "difference_pct_points": float(100 * diff.mean()),
        "bootstrap_ci95_pct_points": [float(100 * ci[0]), float(100 * ci[1])],
        "mcnemar_exact_p": p,
        "discordant_dr_t_0_comparator_1": a0_b1,
        "discordant_dr_t_1_comparator_0": a1_b0,
    }


def main():
    primary_rows = load(PRIMARY)
    strong_rows = load(STRONG)
    shifted_rows = load(SHIFTED)
    primary = index(primary_rows)
    strong = index(strong_rows)
    shifted = index(shifted_rows)

    assert sorted({r["scenario_id"] for r in primary_rows}) == SCENARIOS
    for method in ("HB", "HBP", "DR-T", "DR-SAFE", "dstar_dwa"):
        assert all((s, method) in primary for s in SCENARIOS), method
    assert all((s, "aco_dwa") in strong for s in SCENARIOS)
    assert all((s, "HBP") in shifted and (s, "DR-T") in shifted for s in SCENARIOS)

    rows = []
    for i, (a, b) in enumerate(COMPARISONS):
        source = strong if b == "aco_dwa" else primary
        rows.append(row(primary, b, source, "success", 1000 + 2 * i))
        rows.append(row(primary, b, source, "any_collision", 1001 + 2 * i))

    adjusted = holm([r["mcnemar_exact_p"] for r in rows])
    for r, p in zip(rows, adjusted):
        r["holm_adjusted_p"] = float(p)

    shifted_rows_out = []
    for i, outcome in enumerate(("success", "any_collision")):
        r = row(shifted, "HBP", shifted, outcome, 9001 + i)
        r["indexing"] = "A1 shifted: prediction index = step + 1"
        shifted_rows_out.append(r)

    protocol = {
        "analysis": "A3 paired closed-loop statistics",
        "family": "10 post hoc tests: 5 comparisons x 2 binary outcomes",
        "family_status": "post hoc; the family was never frozen",
        "unit": "scenario",
        "scenario_ids": [4, 203],
        "n_scenarios": 200,
        "tests": "exact two-sided McNemar",
        "multiplicity": "Holm correction across all 10 tests",
        "bootstrap": "95% percentile CI for paired scenario-level difference in percentage points",
        "bootstrap_replicates": BOOTSTRAP_REPS,
        "primary_source": str(PRIMARY.relative_to(ROOT)),
        "strong_baseline_source": str(STRONG.relative_to(ROOT)),
        "shifted_index_source": str(SHIFTED.relative_to(ROOT)),
    }

    output = {"protocol": protocol, "rows": rows, "shifted_index_extra_rows": shifted_rows_out}
    (OUT / "a3_paired_statistics.json").write_text(json.dumps(output, indent=2))

    with (OUT / "table_17C.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Comparison", "Outcome", "N", "DR-T (%)", "Comparator (%)",
                    "Difference (pp)", "95% bootstrap CI (pp)", "Exact McNemar p", "Holm p"])
        for r in rows:
            lo, hi = r["bootstrap_ci95_pct_points"]
            w.writerow([r["comparison"], r["outcome"], r["n"],
                        f'{r["dr_t_rate_pct"]:.1f}', f'{r["comparator_rate_pct"]:.1f}',
                        f'{r["difference_pct_points"]:+.1f}', f'[{lo:+.1f}, {hi:+.1f}]',
                        f'{r["mcnemar_exact_p"]:.6g}', f'{r["holm_adjusted_p"]:.6g}'])

    md = [
        "**Table 17C. Post hoc paired comparisons on the 200-scenario closed-loop set.** "
        "Differences are DR-T minus comparator. CIs are 95% percentile bootstrap intervals "
        "for paired scenario-level differences; p values are exact two-sided McNemar tests; "
        "Holm correction is across the 10-test family. A positive collision difference means "
        "a higher collision rate for DR-T.\n",
        "| Comparison | Outcome | N | DR-T | Comparator | Difference (pp) | 95% CI (pp) | Exact p | Holm p |",
        "|---|---:|---:|---:|---:|---:|---|---:|---:|",
    ]
    for r in rows:
        lo, hi = r["bootstrap_ci95_pct_points"]
        md.append(f'| {r["comparison"]} | {r["outcome"]} | {r["n"]} | '
                  f'{r["dr_t_rate_pct"]:.1f}% | {r["comparator_rate_pct"]:.1f}% | '
                  f'{r["difference_pct_points"]:+.1f} | [{lo:+.1f}, {hi:+.1f}] | '
                  f'{r["mcnemar_exact_p"]:.4g} | {r["holm_adjusted_p"]:.4g} |')
    md += [
        "",
        "**A1 shifted-index extra row (not part of the 10-test family):** DR-T vs HBP under prediction index step + 1.",
    ]
    for r in shifted_rows_out:
        lo, hi = r["bootstrap_ci95_pct_points"]
        md.append(f'- {r["outcome"]}: DR-T {r["dr_t_rate_pct"]:.1f}% vs HBP '
                  f'{r["comparator_rate_pct"]:.1f}%; difference {r["difference_pct_points"]:+.1f} pp; '
                  f'95% CI [{lo:+.1f}, {hi:+.1f}]; exact McNemar p={r["mcnemar_exact_p"]:.4g}.')
    (OUT / "table_17C.md").write_text("\n".join(md) + "\n")

    hashes = {}
    for path in (PRIMARY, STRONG, SHIFTED):
        h = hashlib.sha256(path.read_bytes()).hexdigest()
        hashes[str(path.relative_to(ROOT))] = h
    (OUT / "INPUT_SHA256.json").write_text(json.dumps(hashes, indent=2) + "\n")

    print("A3 complete: Table 17C generated from stored per-run JSON files.")
    for r in rows:
        lo, hi = r["bootstrap_ci95_pct_points"]
        print(f'{r["comparison"]:20s} {r["outcome"]:9s} '
              f'DR-T {r["dr_t_rate_pct"]:5.1f}% vs {r["comparator_rate_pct"]:5.1f}% '
              f'diff {r["difference_pct_points"]:+5.1f} pp '
              f'CI [{lo:+5.1f},{hi:+5.1f}] p={r["mcnemar_exact_p"]:.6g} '
              f'Holm={r["holm_adjusted_p"]:.6g}')
    print("Shifted-index DR-T vs HBP:")
    for r in shifted_rows_out:
        lo, hi = r["bootstrap_ci95_pct_points"]
        print(f'  {r["outcome"]:9s} diff {r["difference_pct_points"]:+5.1f} pp '
              f'CI [{lo:+5.1f},{hi:+5.1f}] p={r["mcnemar_exact_p"]:.6g}')


if __name__ == "__main__":
    main()
