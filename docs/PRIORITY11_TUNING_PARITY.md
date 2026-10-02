# Priority 11 — Tuning parity audit

Date: 2026-10-02
Package checkpoint: v65.8-c6-item11-tuning-parity-caveat

## Finding
The fixed-grid experiments do not constitute an equal-budget hyperparameter competition across methods. The common ABACO transition parameters alpha=1.0, beta=5.0 and rho=0.3 were fixed rather than tuned separately. DR-SAFE received a more extensive formulation-specific search over R, K and D_SAFE than HB, HBP and the APF comparator.

The DR-SAFE radius extension tested R=5.5 and R=6.5. It selected R=5.5 for D_SAFE=1.5, but the confirmation protocol had already frozen R=4.5. Therefore the reported D_SAFE=1.5 confirmation results do not use the later R=5.5 selection.

## Action taken
No new equal-budget rerun was performed for Priority 11. The manuscript was revised to state the asymmetry explicitly in the design-rationale section, Appendix C.3, and the limitations. Fixed-grid method-to-method differences are therefore framed as controlled evidence under the frozen parameter protocol, not as an equal-budget hyperparameter comparison.

## Scope
This audit does not alter any stored numerical result, parameter hash, or primary closed-loop result. It changes the interpretation and disclosure of the fixed-grid evidence only.
