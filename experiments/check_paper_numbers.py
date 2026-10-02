"""check_paper_numbers.py -- independent check of paper tables against the stored per-run results (v29).

Usage: python experiments/check_paper_numbers.py paper.docx -> prints mismatches; exit code 1 if any.
A manuscript path is required because the public code repository intentionally does not contain the paper.

Recomputes with numpy/scipy directly (not via the analysis scripts) and compares with the cells of the .docx:
  Tables 18, 20  means, start-excluded collision rates, run counts, fallbacks (development / confirmation blocks)
  Tables 19, 21  paired mean difference, Wilcoxon p, Holm p over the 8 rows
  Table 10        randomized suite means. Exact-estimate rows: SUITE_SEEDS (10) seeds per scenario; noisy rows: NOISY_SEEDS (5)
  Table 11        randomized suite paired differences (10 seeds per scenario), Wilcoxon p, Holm p over 8
  Table 12        noisy-estimate suite (5 seeds per scenario): means, paired diff vs noisy HBP, Holm p over 8
  Table 13        noisy-estimate main environment (seeds 20000-20099): means, paired diff vs noisy HBP, Holm p over 8
  Table 22        fresh 300-run fixed-grid multi-noise robustness block (Priority-13 stored summaries)
Compared with the stored analysis outputs (results/*.json written by the analysis scripts; run_all.sh --analysis-only refreshes them):
  Tables B.1, B.2   start-waypoint sensitivity (start_cell_coprimary.json)
  Table C.1         time-aligned soft cost vs HB / HBP, post hoc (soft_primary_summary.json)
Not covered: bootstrap CIs (Tables 10-13, 18-22), d_z, Tables 1-9, 14-17, A.1 (they come from the analysis scripts in docs/MANIFEST.md).
Tables are found by their caption number ("Table 10.", "Table B.2."), so caption text can change without breaking the check.
"""
import glob, json, os, re, sys
import numpy as np
from scipy import stats
import docx
from docx.oxml.ns import qn

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); R = os.path.join(ROOT, "results")
SUITE_SEEDS, NOISY_SEEDS = 10, 5      # exact-estimate suite arms / protocol-fixed noisy-estimate sub-study
if len(sys.argv) < 2:
    print("Usage: python experiments/check_paper_numbers.py /path/to/manuscript.docx", file=sys.stderr)
    sys.exit(2)
paper = sys.argv[1]
J = lambda f: json.load(open(os.path.join(R, f)))["runs"]
old, new, fr, su = J("confirmatory_perrun.json"), J("main_new_arms.json"), J("fresh_main.json"), J("suite_results.json")
sadd, fnoise = J("suite_added.json"), J("fresh_noise.json")
dev_seeds, fr_seeds = sorted(new, key=int), sorted(fr, key=int)
DEV = {"HB": lambda s: old[s]["HB"], "HBP": lambda s: new[s]["HBP"], "DR": lambda s: old[s]["DR"], "DRS": lambda s: old[s]["DRS"], "TA": lambda s: new[s]["TA"], "TB": lambda s: new[s]["TB"]}
FRE = {a: (lambda s, a=a: fr[s][a]) for a in ("HB", "HBP", "DR", "SOFT", "APFP", "TA", "TB")}

# ---- read the docx: tables keyed by caption number (caption = next non-empty paragraph after the table)
d = docx.Document(paper); tables = {}
def ptxt(e): return "".join(x.text or "" for x in e.iter(qn("w:t")))
kids = list(d.element.body.iterchildren())
for i, k in enumerate(kids):
    if k.tag != qn("w:tbl"): continue
    for nxt in kids[i + 1:]:
        t = ptxt(nxt).strip()
        if nxt.tag == qn("w:p") and not t: continue
        m = re.match(r"Table ([A-C]\.\d+|\d+)\.\s", t) if nxt.tag == qn("w:p") else None
        if m: tables[m.group(1)] = docx.table.Table(k, d)
        break
def TB(num):
    assert num in tables, f"Table {num} not found in {os.path.basename(paper)} (found: {sorted(tables)})"
    return tables[num]
bad = []; n_ok = 0
def chk(label, got, want):
    global n_ok
    if got == want: n_ok += 1
    else: bad.append(f"{label}: paper '{got}' vs recomputed '{want}'")
norm = lambda s: s.replace("-", "\u2212").replace("\u2013", "\u2212").strip()
def f(x, n): return norm(f"{x:.{n}f}")
def fs(x, n): return ("+" if round(x, n) > 0 else "") + f(x, n)
def cells(t): return [[" ".join(c.text.split()) for c in r.cells] for r in t.rows[1:]]   # collapses stray newlines/double spaces
def split_cmp(s):
    """'DR-SAFE (1.0) - HB', 'DR-SAFE (1.5) -HBP' and 'DR-SAFE (1.0) \u2212 HB' -> ('DR-SAFE (1.0)', 'HB'); hyphens inside names are kept."""
    a, b = re.split(r"\s+[-\u2212]\s*", s.strip(), maxsplit=1); return a, b
def pmatch(label, s, v):
    s = s.strip()
    if s.startswith("<"):
        chk(label, v < float(s[1:]), True)
    else:
        try:
            dec = len(s.split(".")[1])
        except IndexError:
            dec = 6
        chk(label, abs(float(s) - v) <= 0.5 * 10 ** (-dec) + 1e-12, True)
def holm(ps):
    o = np.argsort(ps); adj = np.empty(len(ps)); run = 0
    for rank, i in enumerate(o): run = max(run, (len(ps) - rank) * ps[i]); adj[i] = min(1, run)
    return adj
def wp(x, y):
    k = ~(np.isnan(x) | np.isnan(y)); x, y = x[k], y[k]
    try: return float(stats.wilcoxon(x, y, zero_method="wilcox").pvalue)
    except ValueError: return 1.0
def suite_series(src, arm, metric, ns):
    out = []
    for s in range(36):
        v = [src[f"{s}|{j}"][arm][metric] for j in range(ns) if src[f"{s}|{j}"][arm]["ok"]]
        out.append(np.mean(v) if v else np.nan)
    return np.array(out, float)
def series(kind, arm, metric):
    if kind == "dev": return np.array([DEV[arm](s)[metric] for s in dev_seeds], float)
    if kind == "fresh": return np.array([FRE[arm](s)[metric] for s in fr_seeds], float)
    return suite_series(su, arm, metric, SUITE_SEEDS)

# ---- Tables 18 and 20 (means)
def n_start(conv, _c={}):
    if conv not in _c:
        sys.path.insert(0, os.path.join(ROOT, "experiments")); import drsafe_lib as L
        real = L.real_obstacles_at(conv); _c[conv] = sum(L.base.dist((0, 0), o.traj[min(conv, len(o.traj) - 1)]) < 0.5 for o in real)
    return _c[conv]
def mean_row(get, seeds, a, adj=False):
    r = [get[a](s) for s in seeds]; c = np.array([x["coll"] for x in r], float)
    if adj:
        ac = np.array([x["coll"] - n_start(x["conv"]) for x in r], float)
        start = c - ac
        row = [f(np.mean([x["len"] for x in r]), 2), f(np.mean([x["turns"] for x in r]), 2),
               f(np.mean([x["clear"] for x in r]), 3), f(ac.mean(), 3),
               str(int((ac > 0).sum())), f(start.mean(), 3)]
    else:
        row = [f(np.mean([x["len"] for x in r]), 2), f(np.mean([x["turns"] for x in r]), 2),
               f(np.mean([x["clear"] for x in r]), 3), f(c.mean(), 3), str(int((c > 0).sum()))]
    row.append(f"{np.mean([x['fb'] for x in r]):,.0f}"); return row
for label, row, want in zip(["HB", "HBP", "DR", "Snapshot", "TA", "TB"], cells(TB("18")), [mean_row(DEV, dev_seeds, a, adj=True) for a in ("HB", "HBP", "DR", "DRS", "TA", "TB")]):
    for col, (g, w) in enumerate(zip(row[1:], want)): chk(f"Table 18 {label} col{col+1}", g, w)
for label, row, a in zip(["HB", "HBP", "DR", "SOFT", "APFP", "TA", "TB"], cells(TB("20")), ("HB", "HBP", "DR", "SOFT", "APFP", "TA", "TB")):
    for col, (g, w) in enumerate(zip(row[1:], mean_row(FRE, fr_seeds, a, adj=True))): chk(f"Table 20 {label} col{col+1}", g, w)

# ---- Tables 19, 11, 21 (primary families)
NAMES = {"DR-SAFE (1.0)": "TA", "DR-SAFE (1.5)": "TB", "HB": "HB", "HBP": "HBP"}
def check_family(num, kind):
    calc = []
    for r in cells(TB(str(num))):
        t, ref = split_cmp(r[1]); m = "coll" if r[0].startswith("Collisions") else "turns"
        x, y = series(kind, NAMES[ref], m), series(kind, NAMES[t], m)
        if m == "coll" and kind in ("dev", "fresh"):
            seeds = dev_seeds if kind == "dev" else fr_seeds
            getter = DEV if kind == "dev" else FRE
            x = np.array([getter[NAMES[ref]](s)["coll"] - n_start(getter[NAMES[ref]](s)["conv"]) for s in seeds], float)
            y = np.array([getter[NAMES[t]](s)["coll"] - n_start(getter[NAMES[t]](s)["conv"]) for s in seeds], float)
        calc.append((r, float(np.nanmean(y - x)), wp(x, y), m))
    hp = holm(np.array([c[2] for c in calc]))
    for (r, dm, p, m), h in zip(calc, hp):
        chk(f"Table {num} {r[0]} {r[1]} diff", norm(r[2].split(" [")[0].replace("+", "")), f(dm, 3 if m == "coll" else 2))
        pmatch(f"Table {num} {r[0]} {r[1]} Wilcoxon p", r[4], p); pmatch(f"Table {num} {r[0]} {r[1]} Holm p", r[5], h)
check_family(19, "dev"); check_family(11, "suite"); check_family(21, "fresh")

# ---- Table 10 (suite means; exact rows 10 seeds, noisy rows 5 seeds)
T5 = [("HB", su, "HB", SUITE_SEEDS), ("HBP", su, "HBP", SUITE_SEEDS), ("DR", su, "DR", SUITE_SEEDS), ("DR-SAFE 1.0", su, "TA", SUITE_SEEDS),
      ("DR-SAFE 1.5", su, "TB", SUITE_SEEDS), ("DR-SAFE 1.0 noisy", su, "TA_n", NOISY_SEEDS), ("DR-SAFE 1.5 noisy", su, "TB_n", NOISY_SEEDS)]
for row, (label, src, arm, ns) in zip(cells(TB("10")), T5):
    v = {m: np.nanmean(suite_series(src, arm, m, ns)) for m in ("len", "turns", "clear", "coll", "fb")}
    want = [f(v["len"], 2), f(v["turns"], 2), f(v["clear"], 3), f(v["coll"], 3), f"{v['fb']:,.0f}"]
    for col, (g, w) in enumerate(zip(row[1:], want)): chk(f"Table 10 {label} col{col+1}", norm(g), w)

# ---- Tables 12 and 13 (noisy-estimate studies, compared with NOISY HBP)
def noisy_table(num, get, units, rows):
    """rows: [(label as in paper, arm)] in table order; get(unit, arm, metric)."""
    x = lambda a, m: np.array([get(u, a, m) for u in units], float)
    targets = [a for _, a in rows if a in ("TA_n", "TB_n", "SOFT_n", "APFP_n")]
    calc = {}
    for t in targets:
        for m in ("coll", "turns"): calc[(t, m)] = (float(np.nanmean(x(t, m) - x("HBP_n", m))), wp(x("HBP_n", m), x(t, m)))
    keys = [(t, m) for t in targets for m in ("coll", "turns")]
    hp = dict(zip(keys, holm(np.array([calc[k][1] for k in keys]))))
    for row, (label, arm) in zip(cells(TB(str(num))), rows):
        chk(f"Table {num} {label} collisions", norm(row[1]), f(np.nanmean(x(arm, "coll")), 3))
        chk(f"Table {num} {label} sharp turns", norm(row[2]), f(np.nanmean(x(arm, "turns")), 2))
        if arm in targets:
            for (m, dcol, hcol, nd) in (("coll", 3, 4, 3), ("turns", 5, 6, 2)):
                chk(f"Table {num} {label} {m} diff vs noisy HBP", norm(row[dcol].split(" [")[0]), fs(calc[(arm, m)][0], nd))
                pmatch(f"Table {num} {label} {m} Holm p", row[hcol], hp[(arm, m)])
ROWS = [("HB", "HB"), ("HBP (exact)", "HBP"), ("HBP (noisy; reference)", "HBP_n"), ("DR-SAFE 1.0 (exact)", "TA"), ("DR-SAFE 1.0 (noisy)", "TA_n"),
        ("DR-SAFE 1.5 (exact)", "TB"), ("DR-SAFE 1.5 (noisy)", "TB_n"), ("Soft cost only (exact)", "SOFT"), ("Soft cost only (noisy)", "SOFT_n"),
        ("APF-ACO predicted (exact)", "APFP"), ("APF-ACO predicted (noisy)", "APFP_n")]
def s7(sid, a, m): return suite_series(su if a in ("HB", "HBP", "DR", "TA", "TB", "TA_n", "TB_n") else sadd, a, m, NOISY_SEEDS)[sid]
noisy_table(12, s7, range(36), ROWS)
nseeds = [s for s in sorted(fnoise, key=int)]
def s8(s, a, m):
    r = (fnoise if a.endswith("_n") else fr)[s][a]; return r[m] if r["ok"] else np.nan
noisy_table(13, s8, nseeds, ROWS)

# ---- Table 22 (fresh 300-run fixed-grid robustness block)
# The manuscript table is a descriptive block assembled from the independently
# stored Priority-13 summaries. HB is the clean/noise-invariant reference;
# HBP/APFP are noise-specific; DR-T/DR-SAFE-T come from the clean Step-6
# rerun. No inferential claim is checked here.
P13 = json.load(open(os.path.join(R, "priority13", "priority13_summary.json")))
S6 = json.load(open(os.path.join(R, "priority13_drt_extension_v3_clean", "step6_clean_analysis.json")))
P15 = [
    ("HB", P13["methods"]["HB_clean"]["summary"]),
    ("HBP 5°/10%", P13["methods"]["HBP_n1"]["summary"]),
    ("APFP 5°/10%", P13["methods"]["APFP_n1"]["summary"]),
    ("HBP 15°/20%", P13["methods"]["HBP_n"]["summary"]),
    ("APFP 15°/20%", P13["methods"]["APFP_n"]["summary"]),
    ("HBP 30°/40%", P13["methods"]["HBP_n3"]["summary"]),
    ("APFP 30°/40%", P13["methods"]["APFP_n3"]["summary"]),
    ("DR-T 5°/10%", S6["blocks"]["n1"]["DRT"]),
    ("DR-SAFE-T 5°/10%", S6["blocks"]["n1"]["DRSAFE"]),
    ("DR-T 15°/20%", S6["blocks"]["n"]["DRT"]),
    ("DR-SAFE-T 15°/20%", S6["blocks"]["n"]["DRSAFE"]),
    ("DR-T 30°/40%", S6["blocks"]["n3"]["DRT"]),
    ("DR-SAFE-T 30°/40%", S6["blocks"]["n3"]["DRSAFE"]),
]
for row, (label, e) in zip(cells(TB("22")), P15):
    # Table columns: Method, noise, N, runs with collision, collisions/run,
    # success, sharp turns, path length, minimum clearance.
    want = [
        str(e["N"]),
        f(e["collision_run_rate"] * 100, 1) + "%",
        f(e["collisions_per_run"], 3),
        f(e["success_rate"] * 100, 1) + "%",
        f(e["mean_sharp_turns_successful" if "mean_sharp_turns_successful" in e else "mean_turns"], 2),
        f(e["mean_path_length_successful" if "mean_path_length_successful" in e else "mean_path_length"], 2),
        f(e["mean_min_clearance_successful" if "mean_min_clearance_successful" in e else "mean_min_clearance"], 2),
    ]
    for col, (g, w) in enumerate(zip(row[2:], want), start=1):
        chk(f"Table 22 {label} col{col}", norm(g), w)

# ---- Tables B.1, B.2, C.1 (against stored analysis outputs)
SC = json.load(open(os.path.join(R, "start_cell_coprimary.json")))
PL = {"HB": "HB", "HBP": "HBP", "DR-SAFE 1.0": "TA", "DR-SAFE 1.5": "TB"}
for row in cells(TB("B.1")):
    e = SC["D1"][row[0]][PL[row[1]]]
    for lab, g, w in (("conv", row[2], f(e["conv"], 1)), ("start runs", row[3], str(e["runs_start"])), ("coll", row[4], f(e["coll"], 3)), ("coll excl start", row[5], f(e["adj"], 3))):
        chk(f"Table B.1 {row[0]} {row[1]} {lab}", norm(g), w)
for row in cells(TB("B.2")):
    t, ref = split_cmp(row[1]); e = SC["C"][f"{row[0]}|{PL[t]}-{PL[ref]}"]
    lab = f"Table B.2 {row[0]} {row[1]}"
    chk(lab + " diff [CI]", norm(row[2]), f"{f(e['diff'],3)} [{fs(e['diff_ci'][0],3)}, {fs(e['diff_ci'][1],3)}]")
    pmatch(lab + " Wilcoxon p", row[3], e["p_wilcoxon"]); pmatch(lab + " Holm p", row[4], e["p_holm"])
if "C.1" in tables:
    SP = json.load(open(os.path.join(R, "soft_primary_summary.json")))["family"]
    for row in cells(TB("C.1")):
        m = "coll" if "ollision" in row[1] else "turns"; ref = "HBP" if "HBP" in row[1] else "HB"; e = SP[f"{row[0]}|{m}|SOFT-{ref}"]; nd = 3 if m == "coll" else 2
        lab = f"Table C.1 {row[0]} {row[1]}"
        chk(lab + " diff [CI]", norm(row[2]), f"{f(e['diff'],nd)} [{fs(e['diff_ci'][0],nd)}, {fs(e['diff_ci'][1],nd)}]")
        pmatch(lab + " Wilcoxon p", row[3], e["p_wilcoxon"]); pmatch(lab + " Holm p", row[4], e["p_holm"])
print(f"{n_ok} cells/values agree; {len(bad)} disagree ({os.path.basename(paper)})")
for b in bad: print("  MISMATCH", b)
sys.exit(1 if bad else 0)
