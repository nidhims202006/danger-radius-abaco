"""Check Tables 4A and 4B of a manuscript .docx against the stored phase-5 per-run results.
Usage (from experiments/): python3 check_phase5_numbers.py <manuscript.docx>
Covers table cells only (success, any collision, path length, clearance); p-values and CIs quoted in the
text come from results/phase5/*.json written by analyze_phase5.py and are not parsed from the manuscript.
"""
import glob, json, sys, numpy as np, docx
R = '../results/'; IDS = range(4, 204)
def jl(p): return {(x['method'], x['scenario_id']): x for x in map(json.loads, open(R + 'phase5/' + p))}
prim = {(x['method'], x['scenario_id']): x for x in json.load(open(R + 'phase2_step3_v2/perrun.json'))}
for f in glob.glob(R + 'phase2_strong_chunks/*.json'):
    for x in json.load(open(f)):
        if x['method'] == 'aco_dwa': prim[('aco_dwa', x['scenario_id'])] = x
leg, hyb, hybl, cap, aq = jl('legacy.jsonl'), jl('hybrid.jsonl'), jl('hybrid_legacy.jsonl'), jl('cap_only.jsonl'), jl('ageq_only.jsonl')
S = lambda d, m, k: 100 * np.mean([d[(m, i)][k] for i in IDS])
D = lambda d, m, k='distance': np.mean([d[(m, i)][k] for i in IDS])
pc = lambda v: f'{v:.1f}%'
exp4a = [['Condition', 'Success', 'Any collision', 'Mean path length']]
for tag, d, lab in (('primary adapter (flat deposit)', prim, 'p'), ('age-based deposit and 500-step limit', leg, 'l')):
    for m in ('HB', 'HBP', 'DR-T', 'DR-SAFE'):
        exp4a.append([f'{m}, {tag}', pc(S(d, m, 'success')), pc(S(d, m, 'any_collision')), f'{D(d, m):.2f}'])
exp4a.append(['DR-T, 500-step limit only', pc(S(cap, 'DR-T', 'success')), pc(S(cap, 'DR-T', 'any_collision')), f"{D(cap, 'DR-T'):.2f}"])
exp4a.append(['DR-T, age-based deposit only', pc(S(aq, 'DR-T', 'success')), pc(S(aq, 'DR-T', 'any_collision')), f"{D(aq, 'DR-T'):.2f}"])
exp4b = [['Adapter', 'ACO stage', 'Success', 'Any collision', 'Mean path length', 'Mean min clearance']]
for lab, d in (('Flat deposit (primary)', hyb), ('Age-based deposit', hybl)):
    for nm, key in (('ACO+DWA (HB)', 'aco_dwa_hb'), ('ACO(HBP)+DWA', 'aco_dwa_hbp'), ('ACO(DR-T)+DWA', 'aco_dwa_drt')):
        src, k = (prim, 'aco_dwa') if (d is hyb and key == 'aco_dwa_hb') else (d, key)
        exp4b.append([lab, nm, pc(S(src, k, 'success')), pc(S(src, k, 'any_collision')), f'{D(src, k):.2f}', f"{D(src, k, 'min_clearance'):.2f}"])
doc = docx.Document(sys.argv[1]); body = doc.element.body; agree = disagree = 0
def grab(label):
    for cap_p in doc.paragraphs:
        if cap_p.text.startswith(label + '.'):
            prev = cap_p._p.getprevious()
            for t in doc.tables:
                if t._tbl is prev: return [[c.text.strip() for c in r.cells] for r in t.rows]
    raise SystemExit(f'{label} not found')
for label, exp in (('Table 4A', exp4a), ('Table 4B', exp4b)):
    got = grab(label)
    assert len(got) == len(exp), (label, len(got), len(exp))
    for gr, er in zip(got, exp):
        for g, e in zip(gr, er):
            if g == e: agree += 1
            else: disagree += 1; print('DISAGREE', label, repr(g), 'expected', repr(e))
print(f'{agree} cells/values agree; {disagree} disagree ({sys.argv[1].split("/")[-1]})')
sys.exit(1 if disagree else 0)
