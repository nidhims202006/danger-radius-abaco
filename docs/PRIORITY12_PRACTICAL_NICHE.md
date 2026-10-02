# Priority 12 — Practical niche
Date: 2026-10-02
Package checkpoint: v66.0-c6-item13-practical-significance

## Finding
The closed-loop evidence does not support presenting DR-T as a general replacement for the tested dynamic-obstacle planners. The documented results include about 0.020 s accumulated planning time per scenario and 21.5% any-collision for Space-time A*, and 95.5% success with 16.0% any-collision for ACO+DWA, compared with 72.5% success and 18.0% any-collision for DR-T.

## Practical niche selected
The paper now positions DR-T for an existing ACO-based grid-planning pipeline that needs time-aligned obstacle costing while retaining the ACO search and grid representation. DR-T changes the obstacle-cost term using predicted obstacle occupancy rather than replacing the planner with a time-expanded search or a separate local controller.

## Manuscript action
The niche is stated explicitly in the abstract, Application relevance discussion, and Conclusion. The text also states that the measured results do not support replacing Space-time A*, ACO+DWA, SIPP-style planning, or D* Lite + DWA.

## Scope
No numerical experiment was rerun for Priority 12. The item changes the practical positioning and interpretation of the existing evidence only.
