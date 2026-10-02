# Priority 14 — Multi-case scaling and traced-memory revision
Date: 2026-10-02
Package checkpoint: v66.1-c6-item14-scaling-median-iqr

## Finding
The previous manuscript Tables 20–21 selected one three-dynamic-obstacle case per grid size and reported process RSS. This made the scaling probe sensitive to the individual deterministic case and did not isolate planner-side allocations.

## Action taken
The existing stored direct-planning matrix already contains three deterministic cases per grid size, using 1, 3 and 5 dynamic obstacles. No new numerical run was required. The revised tables aggregate those three cases at each grid size using median and IQR.

Table 20 now reports planner computation time in milliseconds as median [IQR]. Table 21 reports peak `tracemalloc` Python allocations during the planner call as median [IQR], excluding the process RSS baseline. Because `tracemalloc` does not capture native/C-level allocations, Table 21 is explicitly a planner-side traced-memory indicator rather than a complete algorithm-memory measurement.

## Scope
The underlying stored 90-case direct-planning matrix is unchanged. This priority changes the aggregation and interpretation of the scaling evidence only. It does not introduce a statistical performance claim or a deployment-level real-time guarantee.
