import json,glob,os,statistics,math
from collections import defaultdict
from scipy.stats import wilcoxon, binomtest
BASE='/mnt/data/dr_phase2/results/priority13_drt_extension'
OUT=f'{BASE}/step6_analysis.json'
NOISES=['n1','n','n3']
NOISE_LABELS={'n1':'5deg_10pct','n':'15deg_20pct','n3':'30deg_40pct'}

def load(method,noise):
    if noise=='n1':
        d=json.load(open(f'{BASE}/confirmation_{method}_n1.json'))
        return d['runs']
    runs=[]
    for f in sorted(glob.glob(f'{BASE}/chunks_{method}_{noise}/*.json')):
        runs += json.load(open(f))['runs']
    return runs

def vals(runs):
    return {
      'N':len(runs),
      'success_rate':sum(r['result']['ok'] for r in runs)/len(runs),
      'collision_run_rate':sum(r['result']['coll']>0 for r in runs)/len(runs),
      'collisions_per_run':sum(r['result']['coll'] for r in runs)/len(runs),
      'mean_turns_successful':statistics.mean([r['result']['turns'] for r in runs if r['result']['ok']]),
      'mean_path_length_successful':statistics.mean([r['result']['len'] for r in runs if r['result']['ok']]),
      'mean_min_clearance_successful':statistics.mean([r['result']['clear'] for r in runs if r['result']['ok']]),
      'mean_convergence_successful':statistics.mean([r['result']['conv'] for r in runs if r['result']['ok']]),
      'mean_fallbacks':statistics.mean([r['result']['fb'] for r in runs]),
    }

res={'summaries':{},'paired_drt_vs_drsafe':{},'comparison_with_legacy_priority13':{}}
for noise in NOISES:
    for method in ['DRT','DRSAFE']:
        rr=load(method,noise)
        seeds=[r['seed'] for r in rr]
        assert len(rr)==300 and len(set(seeds))==300
        res['summaries'][f'{method}_{noise}']=vals(rr)
    a={r['seed']:r for r in load('DRT',noise)}; b={r['seed']:r for r in load('DRSAFE',noise)}
    common=sorted(set(a)&set(b)); assert len(common)==300
    pairs={}
    for metric in ['coll','len','turns','clear']:
        xa=[a[s]['result'][metric] for s in common]
        xb=[b[s]['result'][metric] for s in common]
        try: stat,p=wilcoxon(xa,xb,zero_method='wilcox',alternative='two-sided')
        except Exception: stat,p=float('nan'),float('nan')
        pairs[metric]={'wilcoxon_stat':float(stat),'p':float(p),'median_drt_minus_drsafe':statistics.median(x-y for x,y in zip(xa,xb))}
    res['paired_drt_vs_drsafe'][noise]=pairs
# Legacy Priority-13 descriptive comparisons only; not inferentially paired because scenarios/protocol differ.
legacy=json.load(open('/mnt/data/dr_phase2/results/priority13/priority13_summary.json'))['methods']
for noise in NOISES:
    keymap={'n1':('HBP_n1','APFP_n1'),'n':('HBP_n','APFP_n'),'n3':('HBP_n3','APFP_n3')}
    h,a=keymap[noise]
    res['comparison_with_legacy_priority13'][noise]={
      'HBP':legacy[h]['summary'],'APFP':legacy[a]['summary'],
      'DRT':res['summaries'][f'DRT_{noise}'],'DRSAFE':res['summaries'][f'DRSAFE_{noise}'],
      'comparison_note':'Descriptive only: legacy Priority-13 HBP/APFP and the new continuous DR-T/DR-SAFE extension use different planner interfaces/protocols and are not treated as paired inferential comparisons.'
    }
json.dump(res,open(OUT,'w'),indent=2)
print(json.dumps(res['summaries'],indent=2))
print('--- paired')
print(json.dumps(res['paired_drt_vs_drsafe'],indent=2))
print('saved',OUT)
