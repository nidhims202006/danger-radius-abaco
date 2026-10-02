"""
exec_aligned_metrics.py

Single shared implementation of the execution-aligned (Method B, corrected)
collision/clearance metric used throughout this repo, wherever a script
reports execution-aligned collisions or minimum clearance:
danger_radius/ABACO_safety_radius.py, experiments/run_safety_batch.py,
experiments/rerun_apf_methodb.py, experiments/rerun_generalization_methodb.py,
and experiments/broaden_validation.py.

Previously this was five separate copies -- four identical inline
definitions plus broaden_validation.py silently falling back to a third,
unrelated metric (the raw 'collisions'/'min_clearance' fields that
ABACO_baseline.run_abaco()/ABACO_novelty.run_abaco() compute for their own,
non-execution-aligned, from-t=0 purposes). All five now call this one
function, so a future fix only has to happen once.

Sits in abaco/ so every experiment can import one canonical implementation.
ABACO_baseline.py also uses this function for its returned collision and
clearance fields, eliminating the previous hidden from-t=0 metric.

Definition (see Section 2.5 of the paper): waypoint i of the winning path is
checked against the relevant obstacle's recorded trajectory position at
run-iteration (conv + i), where `conv` is the iteration the winning path was
found at -- i.e. "if this already-computed path were handed to the robot at
the moment it was found, and the obstacle kept moving on its real
trajectory, would they collide?"

CORRECTED (was conv - 1 + i): DynObs.step() appends the new obstacle
position *before* ants plan each iteration, so the obstacle snapshot
actually used to plan the path found during iteration `it` is traj[it+1],
and `conv == it+1` for that iteration. So the planning-time snapshot is
traj[conv], not traj[conv-1], and waypoint i must be checked against
traj[conv+i]. The previous offset compared every waypoint to the obstacle
position one iteration earlier than the one the path was actually planned
against. This is a different, more correct definition than the from-t=0
indexing ABACO_baseline.run_abaco() / ABACO_novelty.run_abaco() use
internally for their own 'collisions'/'min_clearance' fields -- do not read
those fields directly when an execution-aligned number is wanted; call this
function on the result dict instead.
"""


def execution_aligned_metrics(result, module, collision_threshold=0.5, exclude_start=False):
    """Compute (collisions, min_clearance) for one run's result dict using
    the execution-aligned (Method B, corrected) definition above.

    result: a dict as returned by run_abaco() / run_abaco_safety() /
        run_abaco_apf(), i.e. must contain 'best_path', 'convergence', and
        'dyn_obs'.
    module: the ABACO_baseline / ABACO_novelty module whose dist() to use
        (the two modules define an identical dist(), but callers pass the
        one matching the condition being scored).
    collision_threshold: distance below which a waypoint/obstacle pair
        counts as a collision. Same default (0.5) used throughout the repo.
    exclude_start: if True, waypoint i=0 is treated as a pre-handoff
        occupancy event and excluded from the primary collision count. The
        event remains available to a separate start-waypoint audit.
    """
    best_p = result["best_path"]
    conv = result["convergence"]
    dyn = result["dyn_obs"]
    offset = conv
    cols = 0
    min_cl = float("inf")
    for si, node in enumerate(best_p):
        if exclude_start and si == 0:
            continue
        for o in dyn:
            idx = min(offset + si, len(o.traj) - 1)
            op = o.traj[idx]
            d = module.dist(node, op)
            min_cl = min(min_cl, d)
            if d < collision_threshold:
                cols += 1
    return cols, min_cl
