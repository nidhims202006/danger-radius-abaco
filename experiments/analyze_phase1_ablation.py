import json, os, statistics, math
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
new=json.load(open(os.path.join(ROOT,'results','phase1_continuous_ablation.json')))['runs']
old=json.load(open(os.path.join(ROOT,'results','ablation_main.json')))['runs']
seeds=sorted(set(new)&set(old), key=int)
metrics=['len','turns','clear','coll']
out={'n':len(seeds),'seeds':[int(s) for s in seeds],'comparisons':{}}
for pair in [('SOFT','SOFT_CONT'),('DRSAFE','DRSAFE_CONT')]:
    oldk,newk=pair
    c={}
    for m in metrics:
        a=[old[s][oldk][m] for s in seeds]
        b=[new[s][newk][m] for s in seeds]
        dif=[b[i]-a[i] for i in range(len(a)) if a[i] is not None and b[i] is not None]
        c[m]={'old_mean':statistics.mean(a),'new_mean':statistics.mean(b),'mean_new_minus_old':statistics.mean(dif),'max_abs_difference':max(abs(x) for x in dif),'identical_runs':sum(x==0 for x in dif),'n_compared':len(dif)}
    out['comparisons'][oldk+'__'+newk]=c
# pointwise old/new implementation sanity for exact metric equality
json.dump(out,open(os.path.join(ROOT,'results','phase1_ablation_summary.json'),'w'),indent=2)
print(json.dumps(out,indent=2))
