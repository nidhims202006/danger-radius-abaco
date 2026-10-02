# Hard-floor evidence boundary (review item 2)

The manuscript's primary design contribution is DR-T, the time-aligned soft danger-radius cost. DR-SAFE is retained as a secondary extension that adds a hard inner clearance floor.

## What the evidence supports

- Under exact estimates, the component ablation does **not** show an incremental benefit from the floor.
- On the 300-run confirmation block, after start-waypoint exclusion, DR-SAFE minus soft-cost-only changed collisions by -0.017/run at `D_SAFE=1.0` (Holm p=0.372) and 0.000/run at `D_SAFE=1.5` (p=1.000).
- At `D_SAFE=1.5`, the floor was relaxed on the winning path in 29% of confirmation runs, so it is not a hard feasibility or safety guarantee.
- A limited post hoc noisy-estimate signal exists for `D_SAFE=1.5`, but it is not consistent across the tested conditions and is not used as a primary contribution.
- The N=8 high-fidelity continuous-kinematic check is reported as an execution-interface validation, not as evidence that the floor improves safety.

## Reporting rule

The fixed-grid DR-SAFE tables are retained for transparency because they document the historical floor extension and its ablation. They are not presented as evidence that the hard floor is the mechanism responsible for the DR-T result. Headline interpretation is based on DR-T and on the component ablation showing that prediction, rather than the floor, accounts for the principal exact-estimate effect.
