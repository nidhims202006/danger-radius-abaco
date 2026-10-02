"""Post hoc paired statistics for the ORCA and MPC baselines (scenarios 4-203).

Family A (new, 4 tests): DR-T vs {ORCA, MPC} x {success, any-collision}.
Family B (extended, 14 tests): the 10 tests of analyze_a3_paired_statistics.py
plus the 4 above, Holm-corrected together.  Exact two-sided McNemar tests and
4,000-resample percentile bootstrap CIs on the paired scenario-level difference,
identical to A3.  All of this is post hoc.
"""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
import numpy as np
from scipy.stats import binomtest
import analyze_a3_paired_statistics as A3

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "phase4_orca_mpc_stats"
OUT.mkdir(parents=True, exist_ok=True)
NEW = ROOT / "results" / "phase4_orca_mpc_perrun.json"
DISPLAY = {"orca": "ORCA", "mpc": "MPC", **A3.DISPLAY}

def main():
    primary = A3.index(A3.load(A3.PRIMARY)); strong = A3.index(A3.load(A3.STRONG)); new = A3.index(json.load(open(NEW)))
    sc = A3.SCENARIOS
    assert all((s, m) in new for s in sc for m in ("orca", "mpc"))
    def row(comp, source, outcome, seed):
        a = np.array([bool(primary[(s, "DR-T")][outcome]) for s in sc])
        b = np.array([bool(source[(s, comp)][outcome]) for s in sc])
        diff = a.astype(float) - b.astype(float)
        p, a0b1, a1b0 = A3.mcnemar_exact(a, b)
        ci = A3.bootstrap_ci(diff, seed)
        return {"comparison": f"DR-T vs {DISPLAY.get(comp, comp)}", "outcome": "success" if outcome == "success" else "collision",
                "n": len(sc), "dr_t_rate_pct": float(100*a.mean()), "comparator_rate_pct": float(100*b.mean()),
                "difference_pct_points": float(100*diff.mean()),
                "bootstrap_ci95_pct_points": [float(100*ci[0]), float(100*ci[1])],
                "mcnemar_exact_p": p, "discordant_dr_t_0_comparator_1": a0b1, "discordant_dr_t_1_comparator_0": a1b0}
    new_rows = []
    for i, comp in enumerate(("orca", "mpc")):
        new_rows.append(row(comp, new, "success", 2000 + 2*i))
        new_rows.append(row(comp, new, "any_collision", 2001 + 2*i))
    old_rows = json.load(open(A3.OUT / "a3_paired_statistics.json"))["rows"]
    for r, h in zip(new_rows, A3.holm([r["mcnemar_exact_p"] for r in new_rows])): r["holm_p_family_of_4"] = h
    allp = [r["mcnemar_exact_p"] for r in old_rows + new_rows]
    for r, h in zip(old_rows + new_rows, A3.holm(allp)): r["holm_p_family_of_14"] = h
    json.dump({"new_rows": new_rows, "old_rows_with_14_test_holm": old_rows,
               "note": "post hoc; ORCA/MPC added after the frozen protocol"}, open(OUT / "orca_mpc_paired_statistics.json", "w"), indent=2)
    with open(OUT / "table_17C_extension.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["Comparison","Outcome","N","DR-T (%)","Comparator (%)","Difference (pp)","95% bootstrap CI (pp)","Exact McNemar p","Holm p (4)","Holm p (14)"])
        for r in new_rows:
            lo, hi = r["bootstrap_ci95_pct_points"]
            w.writerow([r["comparison"], r["outcome"], r["n"], f'{r["dr_t_rate_pct"]:.1f}', f'{r["comparator_rate_pct"]:.1f}', f'{r["difference_pct_points"]:+.1f}', f'[{lo:+.1f}, {hi:+.1f}]', f'{r["mcnemar_exact_p"]:.4g}', f'{r["holm_p_family_of_4"]:.4g}', f'{r["holm_p_family_of_14"]:.4g}'])
    (OUT / "INPUT_SHA256.json").write_text(json.dumps({str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (A3.PRIMARY, A3.STRONG, NEW)}, indent=2) + "\n")
    print("NEW ROWS")
    for r in new_rows:
        lo, hi = r["bootstrap_ci95_pct_points"]
        print(f'{r["comparison"]:16s}{r["outcome"]:10s} DR-T {r["dr_t_rate_pct"]:5.1f}% vs {r["comparator_rate_pct"]:5.1f}%  diff {r["difference_pct_points"]:+6.1f} CI[{lo:+6.1f},{hi:+6.1f}] p={r["mcnemar_exact_p"]:.3g} Holm4={r["holm_p_family_of_4"]:.3g} Holm14={r["holm_p_family_of_14"]:.3g}')
    print("ORIGINAL 10 UNDER 14-TEST HOLM")
    for r in old_rows:
        print(f'{r["comparison"]:22s}{r["outcome"]:10s} p={r["mcnemar_exact_p"]:.3g} Holm10={r["holm_adjusted_p"]:.3g} Holm14={r["holm_p_family_of_14"]:.3g}')

if __name__ == "__main__":
    main()
