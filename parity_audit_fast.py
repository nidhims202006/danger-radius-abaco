import os,sys,json,time,multiprocessing as mp,numpy as np
ROOT=os.path.dirname(__file__); sys.path += [os.path.join(ROOT,x) for x in ('experiments','abaco','danger_radius','baselines')]
C={
'HB':[dict(ants=a,iterations=i,label=f'a{a}_i{i}') for a,i in [(20,50),(30,75),(40,100),(50,100),(40,125),(60,100)]],
'HBP':[dict(ants=a,iterations=i,label=f'a{a}_i{i}') for a,i in [(20,50),(30,75),(40,100),(50,100),(40,125),(60,100)]],
'DR-T':[dict(R=R,K=K,ants=40,iterations=100,label=f'R{R}_K{K}') for R,K in [(2.5,1),(3.5,1),(4.5,1),(3.5,2),(4.5,2),(5.5,2)]],
'DR-SAFE':[dict(R=R,K=K,D_SAFE=D,ants=40,iterations=100,label=f'R{R}_K{K}_D{D}') for R,K,D in [(3.5,1,1),(4.5,1,1),(3.5,2,1),(4.5,2,1.5),(5.5,2,1.5),(4.5,3,1.5)]]}
SEEDS=list(range(6000,6010))
def w(t):
 m,p,s=t; import drsafe_lib as L,ABACO_safety_pred as SP
 old=(L.base.NUM_ANTS,L.base.NUM_ITERATIONS); L.base.NUM_ANTS,L.base.NUM_ITERATIONS=p.get('ants',40),p.get('iterations',100)
 try:
  if m=='HB': r=L.run_hb(s)
  elif m=='HBP': r=L._flat(SP.run_abaco_safety_pred(L.GRID,s,mode='hb'),L.base)
  elif m=='DR-T': r=L.run_dr(s,R=p['R'],K=p['K'])
  else: r=L.run_drs(s,R=p['R'],K=p['K'],d_safe=p['D_SAFE'])
  return (m,p,s,r)
 finally: L.base.NUM_ANTS,L.base.NUM_ITERATIONS=old
def summ(items,m):
 rows=[]
 for p in C[m]:
  rs=[x[3] for x in items if x[1]==p]; valid=[r for r in rs if r['ok'] and r['coll'] is not None]
  rows.append({'params':p,'n':len(rs),'failure_rate':1-len(valid)/len(rs),'collision_rate':float(np.mean([r['coll'] for r in valid])),'sharp_turns':float(np.mean([r['turns'] for r in valid])),'mean_length':float(np.mean([r['len'] for r in valid]))})
 z=lambda x:(x-x.mean())/(x.std() if x.std()>0 else 1); sc=z(np.array([r['collision_rate'] for r in rows]))+z(np.array([r['sharp_turns'] for r in rows]))
 for r,s in zip(rows,sc):r['score']=float(s)
 return {'candidates':rows,'selected':min(rows,key=lambda r:(round(r['score'],12),r['mean_length']))}
if __name__=='__main__':
 t=time.time(); tasks=[(m,p,s) for m in C for p in C[m] for s in SEEDS]; print('tasks',len(tasks),flush=True)
 with mp.Pool(5) as pool: items=list(pool.imap_unordered(w,tasks))
 out={'protocol':{'seed_ids':SEEDS,'n_seeds':10,'candidates_per_method':6,'selection_rule':'within-method z(collision events/run)+z(sharp turns), ties by mean path length','status':'parity audit; primary frozen results not replaced'},'methods':{m:summ(items,m) for m in C}}
 json.dump(out,open(os.path.join(ROOT,'parity_audit.json'),'w'),indent=2); print(json.dumps(out,indent=2)); print('elapsed',time.time()-t)
