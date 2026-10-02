# Priority 9 — APF distinction in the Method section

## Status
COMPLETE — verified against manuscript v87 (`Danger-Radius_Paper_v87_refs_1-3_fixed.docx`).

## Requirement
State the mathematical difference from the artificial potential field (APF) baseline in the Method section, rather than introducing the distinction only in the experimental comparison.

## Manuscript verification
Section 4 contains the paragraph headed **“Relation to artificial potential fields.”** It explicitly states:

- APF uses a quadratic shifted-reciprocal potential,
  `U(d) = 0.5·η·(1/d − 1/D0)^2` for `d < D0`.
- DR-T uses a single reciprocal penalty,
  `K/(d+ε)` within `R`, truncated at `R`.
- Both are inserted into the same ABACO transition rule for the controlled comparison.
- The comparison therefore isolates the repulsive-cost shape rather than claiming that DR-T replaces potential-field or local-control methods generally.

The paragraph occurs immediately before Section 4.2 in the v87 manuscript, so the distinction is part of the Method presentation.

## Code/repository verification
The repository already contains the APF comparison implementation and stored APF/DR-SAFE results used by the manuscript. No algorithmic code change was required for this priority.

## Scope
No manuscript numerical values were changed for Priority 9.
