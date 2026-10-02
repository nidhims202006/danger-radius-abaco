# What the paper is (decision taken in v22, 2026-09-30)

## Decision
The proposed method is the **time-aligned soft danger-radius cost (DR-T)**. **DR-SAFE (= DR-T + hard clearance floor)** is an extension that the paper reports honestly as adding no detectable benefit with exact estimates.
The title already describes DR-T ("Time-Aligned Danger-Radius Cost Weighting ..."), so it stays. What changed is the method name, the abstract, the contribution paragraph, Section 4.1, the conclusion and a new Appendix C.

## Why (evidence already in the paper, nothing new run)
| Question | Answer from the data | Where |
|---|---|---|
| Where do the collision reductions come from? | Prediction. HB 0.203 -> HBP 0.077 (dev), 0.257 -> 0.093 (confirmation); DR-T 0.050 / 0.060 | Tables 3, 9, 13 |
| Does the floor add anything with exact estimates? | No. DR-SAFE minus soft-only: collisions -0.017 / 0.000, sharp turns +0.37 / +0.17, all n.s. (confirmation); dev Holm p >= 0.64 | Tables 10, Section 5.10 |
| Is the floor really enforced? | D_SAFE = 1.0: relaxed on the winning path in 0 / 300 runs. D_SAFE = 1.5: in 88 / 300 runs (29%) | Table A.1 |
| What does DR-T give beyond prediction? | Smoother, shorter, more clearance: vs HBP 1.7-2.1 fewer sharp turns, 0.8-0.9 m shorter (Holm p < 0.0001, both blocks). Collisions vs HBP: -0.027 / -0.033, Holm p 0.30 | Table C.1 (post hoc) |
| Is there any evidence FOR the floor? | Only under noisy estimates: DR-SAFE 1.5 vs noisy HBP, Holm p 0.013 (suite), 0.030 (main); DR-T (soft only) does not reduce collisions vs noisy HBP. Floor-vs-soft under noise is post hoc (p = 0.004 main env, 0.14 suite) and comes with a 29% relaxation rate | Tables 7-8, Section 5.7 |

## Claims that survive / claims dropped
- Keep: evaluating obstacle cost at the predicted position for the arrival step is what reduces collisions; a smooth cost gives smoother, shorter, safer-margin paths; the effect on collisions is small once prediction is present and not consistent across seed blocks.
- Drop (v22 abstract no longer says it): "halved collisions" as a property of the danger radius; DR-SAFE as *the* proposed method; anything implying a safety guarantee.
- Do not treat the floor as a co-contribution. A limited post hoc signal exists under some noisy-estimate conditions, but it is inconsistent across the tested blocks, while the exact-estimate ablation shows no incremental benefit. DR-SAFE remains a secondary evaluated extension.

## What would change the decision
The current paper does not make the floor a headline component. Any future claim for the floor would require a separately pre-registered comparison against soft-cost-only across multiple noise levels with relaxation explicitly controlled and reported.

## Disclosure that must stay in the paper
The pre-registered primary families (Tables 4, 6, 14) are about DR-SAFE. DR-T comparisons with HB and HBP were not declared beforehand (dev block: DR-T was added after the design was informed by those seeds; confirmation block: arm was declared, comparisons were not). They are reported as post hoc in Appendix C and the abstract says "post hoc". Do not relabel them as primary in the response letter.
