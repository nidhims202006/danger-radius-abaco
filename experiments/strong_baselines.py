"""Additional closed-loop comparison baselines for Phase 2.

These are matched-interface baselines, not source-code reproductions of any
published implementation.
"""
from __future__ import annotations
import heapq, math, time
from phase2_planners import neighbors, dwa_local_step
from phase3_abaco_v2 import abaco_plan


def sipp(rows, cols, start, goal, static_blocked, predicted, max_time=60):
    """Grid Safe Interval Path Planning over predicted discrete occupancy.

    Waiting is allowed. For each cell, free-time intervals are constructed
    from the predicted occupancy sequence, and search states are (cell,
    interval, arrival_time). Edge traversal takes one world tick.
    """
    t0 = time.perf_counter()
    horizon = min(max_time, max(0, len(predicted)-1))
    cells = [(r,c) for r in range(rows) for c in range(cols)
             if (r,c) not in static_blocked]
    free = {}
    for cell in cells:
        intervals=[]; start_t=0
        for t in range(horizon+1):
            blocked = t < len(predicted) and cell in predicted[t]
            if blocked:
                if start_t <= t-1: intervals.append((start_t,t-1))
                start_t=t+1
        if start_t <= horizon: intervals.append((start_t,horizon))
        free[cell]=intervals
    if start not in free or goal not in free:
        return [], time.perf_counter()-t0

    def interval_id(cell,t):
        for i,(a,b) in enumerate(free[cell]):
            if a <= t <= b: return i
        return None

    si=interval_id(start,0)
    if si is None: return [], time.perf_counter()-t0
    # state: (cell, interval index, arrival time)
    pq=[(math.dist(start,goal),0,start,si)]
    best={(start,si):0}
    parent={}
    while pq:
        f,t,cell,iv=heapq.heappop(pq)
        if t != best.get((cell,iv)): continue
        if cell==goal:
            out=[]; key=(cell,iv)
            # Parent stores predecessor state and chosen wait/move time.
            cur=(cell,iv,t)
            while cur is not None:
                c,i,arr=cur; out.append(c)
                cur=parent.get((c,i,arr))
            return list(reversed(out)), time.perf_counter()-t0
        a,b=free[cell][iv]
        # Wait in current safe interval and move to a neighbor at earliest
        # feasible arrival. A move takes one tick.
        for nb,_ in neighbors(cell,rows,cols):
            if nb not in free: continue
            for j,(na,nb_end) in enumerate(free[nb]):
                arr=max(t+1,na)
                if arr <= nb_end and arr <= horizon:
                    # We may wait only while the current cell remains safe.
                    depart=arr-1
                    if depart < a or depart > b: continue
                    key=(nb,j)
                    if arr < best.get(key,10**9):
                        best[key]=arr
                        parent[(nb,j,arr)]=(cell,iv,t)
                        heapq.heappush(pq,(arr+math.dist(nb,goal),arr,nb,j))
                    break
    return [], time.perf_counter()-t0


def aco_dwa_plan(rows, cols, start, goal, static_blocked, current_obs,
                 ants=12, iterations=20, clearance_weight=0.25,
                 goal_weight=1.0, seed=0):
    """ACO global path + DWA-style local step.

    The ACO stage is static/global; DWA handles current dynamic occupancy.
    This is a matched-interface hybrid baseline, not an exact reproduction
    of Gong et al. (2022) or another published implementation.
    """
    t0=time.perf_counter()
    pred=[list(current_obs)]
    path,_,_=abaco_plan(rows,cols,start,goal,set(static_blocked),pred,
                        mode='HB',ants=ants,iterations=iterations,seed=seed)
    if len(path)<2:
        return start,time.perf_counter()-t0
    blocked=set(static_blocked)|set(current_obs)
    target=path[min(3,len(path)-1)]
    cand=[x for x,_ in neighbors(start,rows,cols)]
    best=None; best_score=-1e18
    for cell in cand:
        if cell in blocked: continue
        progress=-goal_weight*math.dist(cell,target)
        clearance=min((math.dist(cell,b) for b in blocked),default=5.0)
        score=progress+clearance_weight*min(clearance,5.0)
        if score>best_score: best_score,best=score,cell
    return (best if best is not None else start), time.perf_counter()-t0
