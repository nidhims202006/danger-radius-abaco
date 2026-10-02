**Table 17C. Post hoc paired comparisons on the 200-scenario closed-loop set.** Differences are DR-T minus comparator. CIs are 95% percentile bootstrap intervals for paired scenario-level differences; p values are exact two-sided McNemar tests; Holm correction is across the 10-test family. A positive collision difference means a higher collision rate for DR-T.

| Comparison | Outcome | N | DR-T | Comparator | Difference (pp) | 95% CI (pp) | Exact p | Holm p |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| DR-T vs HBP | success | 200 | 72.5% | 75.0% | -2.5 | [-8.5, +3.5] | 0.5114 | 1 |
| DR-T vs HBP | collision | 200 | 18.0% | 26.5% | -8.5 | [-15.0, -2.0] | 0.02409 | 0.1489 |
| DR-T vs HB | success | 200 | 72.5% | 69.0% | +3.5 | [-1.5, +8.5] | 0.2478 | 0.9912 |
| DR-T vs HB | collision | 200 | 18.0% | 31.0% | -13.0 | [-20.0, -6.0] | 0.0004095 | 0.003276 |
| DR-T vs DR-SAFE | success | 200 | 72.5% | 67.5% | +5.0 | [+1.0, +9.0] | 0.02127 | 0.1489 |
| DR-T vs DR-SAFE | collision | 200 | 18.0% | 23.0% | -5.0 | [-9.0, -1.0] | 0.04139 | 0.2069 |
| DR-T vs ACO+DWA | success | 200 | 72.5% | 95.5% | -23.0 | [-29.0, -17.0] | 2.267e-12 | 2.04e-11 |
| DR-T vs ACO+DWA | collision | 200 | 18.0% | 16.0% | +2.0 | [-4.5, +8.0] | 0.644 | 1 |
| DR-T vs D* Lite+DWA | success | 200 | 72.5% | 100.0% | -27.5 | [-33.5, -21.5] | 5.551e-17 | 5.551e-16 |
| DR-T vs D* Lite+DWA | collision | 200 | 18.0% | 22.5% | -4.5 | [-12.5, +3.5] | 0.3135 | 0.9912 |

**A1 shifted-index extra row (not part of the 10-test family):** DR-T vs HBP under prediction index step + 1.
- success: DR-T 72.0% vs HBP 76.0%; difference -4.0 pp; 95% CI [-10.5, +2.5]; exact McNemar p=0.28.
- collision: DR-T 21.5% vs HBP 33.0%; difference -11.5 pp; 95% CI [-19.5, -3.5]; exact McNemar p=0.006741.
