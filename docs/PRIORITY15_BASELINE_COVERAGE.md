# Priority 15 — Baseline coverage audit
Date: 2026-10-02
Package checkpoint: v66.2-c6-item15-baseline-coverage

## Finding
The closed-loop study already contains matched-interface dynamic-avoidance baselines (ACO+DWA and a SIPP-style safe-interval planner) plus time-explicit space-time A* and D* Lite with DWA. These provide implemented alternatives to the proposed time-aligned obstacle-cost modification.

Gong et al. (2022) is a closely related ACO-plus-local-avoidance method, but the current repository does not contain a source-level reproduction of its collar-path construction, adaptive pheromone rules, and shape/motion-specific local avoidance strategies. ORCA and MPC are likewise not numerically implemented.

## Action taken
The manuscript now explicitly distinguishes implemented baselines from contextual literature and states that the benchmark is not a comprehensive comparison across all dynamic-obstacle planning families. The limitations section now names the missing ORCA/MPC and non-reproduced Gong baseline rather than implying complete baseline coverage.

## Scope
No numerical baseline results were invented and no existing numerical result was changed. This priority therefore closes the documentation/claim gap while preserving the repository's reproducibility boundary.
