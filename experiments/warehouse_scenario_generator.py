"""Generate 24 deterministic warehouse-style grid scenarios.

This is a validation-data generator: it creates longitudinal rack blocks,
cross-aisles, loading openings and moving-worker/forklift-like obstacles.
It does not claim experimental results; execution must be run separately with
an explicitly frozen analysis protocol.
"""
from dataclasses import dataclass
import random, json
from phase2_scenario_generator import Scenario, DynamicSpec

SEEDS=list(range(91000,91024))

def make(i):
    rng=random.Random(SEEDS[i]); rows=cols=24; blocked=set()
    for c in (4,8,12,16,20):
        for r in range(3,21):
            if r not in (7,14): blocked.add((r,c))
    if i%4==0:
        blocked.update((19,c) for c in (3,4,5))
    if i%4==2:
        blocked.update((r,18) for r in (3,4,5))
    dyn=(
      DynamicSpec(6,9,0.35+rng.random()*0.15,0,'stop_go'),
      DynamicSpec(15,13,0.30+rng.random()*0.20,180,'constant'),
      DynamicSpec(10,20,0.25+rng.random()*0.25,90,'curved',12+i%8,180),
    )
    return Scenario(i,SEEDS[i],rows,cols,len(blocked)/(rows*cols),(1,1),(22,22),tuple(sorted(blocked)),dyn,0.15)

if __name__=='__main__':
    out=[make(i).to_dict() for i in range(24)]
    with open('results/warehouse_scenarios_24.json','w') as f: json.dump(out,f,indent=2)
    print('generated=24')
