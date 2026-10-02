import os, sys, json, time
from concurrent.futures import ProcessPoolExecutor
import drsafe_lib as L
import ABACO_safety_pred_continuous as NEW

ROOT=L.ROOT

def one(seed):
    def flat(res): return L._flat(res,L.base)
    soft=flat(NEW.run_abaco_safety_pred(L.GRID,seed=seed,d_safe=0.0,R=4.5,K=2.0,mode='safe'))
    safe=flat(NEW.run_abaco_safety_pred(L.GRID,seed=seed,d_safe=1.5,R=4.5,K=2.0,mode='safe'))
    return str(seed), {'SOFT_CONT':soft,'DRSAFE_CONT':safe}

if __name__=='__main__':
    lo=int(sys.argv[1]); hi=int(sys.argv[2]); out=sys.argv[3]
    t=time.time()
    with ProcessPoolExecutor(max_workers=5) as ex:
        rows=dict(ex.map(one, range(lo,hi)))
    payload={'meta':{'seeds':f'{lo}-{hi-1}','R':4.5,'K':2.0,'workers':5},'runs':rows}
    with open(out,'w') as f: json.dump(payload,f)
    print(f'{lo}-{hi-1} done {time.time()-t:.1f}s')
