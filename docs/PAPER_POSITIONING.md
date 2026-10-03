# Paper positioning and evidence boundary

## Primary contribution

The paper's primary design contribution is the **time-aligned danger-radius cost (DR-T)**. The cost is
computed using the predicted obstacle position at the step at which a candidate cell would be reached.
The underlying ABACO optimisation framework is established work; the contribution is the time-aligned
obstacle-cost modification evaluated inside that framework.

## Secondary extension

**DR-SAFE** adds a hard inner clearance floor to DR-T. The exact-estimate ablation did not detect an
incremental benefit from the floor. Limited noisy-estimate signals are retained as exploratory evidence,
but they are not treated as a primary contribution. The floor is not a safety guarantee.

## Statistical positioning

The manuscript uses the term **pre-specified** to mean fixed in an internal written protocol with code
and parameter hashes recorded before the relevant runs. It does **not** imply external registration.
DR-T-specific inferential comparisons that were added after the original analysis families were fixed are
reported as post hoc. ORCA/MPC were also added post hoc and are bounded by the manuscript's stated
inference scope.

The paper should not relabel post hoc analyses as primary analyses or imply external preregistration.

## Fixed-grid tuning limitation

The historical fixed-grid development block retains an asymmetric tuning history. Common ABACO
parameters were fixed, but DR-SAFE received a broader formulation-specific search over its parameters.
The later R=5.5 extension was not retroactively rerun as the frozen R=4.5 confirmation block. Equal-budget
tuning utilities are included in the repository, but no full historical fixed-grid equal-budget rebuild is
claimed.

Accordingly, fixed-grid descriptive differences should not be presented as a retroactive hyperparameter-
matched ranking of methods.

## Closed-loop implementation boundary

The 200-scenario closed-loop study uses a controlled ABACO-family adapter rather than the legacy
fixed-grid source implementation. The adapter differences are documented in `docs/ADAPTER_DIFFERENCES.md`.
The closed-loop results are therefore execution-level evidence for the time-aligned design within that
controlled interface, not source-level reproduction of the legacy fixed-grid implementation.

## Application and validation boundary

The intended application context is indoor autonomous mobile robots operating in shared workspaces,
including warehouse-like environments. The repository includes a deterministic warehouse-style scenario
generator, but the study does not report a completed full warehouse validation. Likewise, the N=8
high-fidelity study is simulation/interface evidence only; it is not physical-robot or ROS/Gazebo validation.

## Required wording discipline

Do not describe DR-T as a universally superior dynamic-obstacle planner. Do not describe DR-SAFE as
providing a safety guarantee. Keep the distinction between fixed-grid development evidence, closed-loop
execution evidence, post hoc analyses and high-fidelity simulation/interface validation explicit.
