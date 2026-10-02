"""Phase-2 implementation smoke test. Does not inspect existing experiment results."""
from phase2_scenario_generator import generate_scenarios
from phase2_closed_loop import run_closed_loop

scenarios = generate_scenarios(200)
assert len(scenarios) == 200
assert len({s.seed for s in scenarios}) == 200
assert len({(s.rows,s.cols) for s in scenarios}) >= 3
assert len({s.static_density for s in scenarios}) >= 3
assert len({len(s.dynamic_obstacles) for s in scenarios}) >= 3
assert len({s.dynamic_obstacles[0].motion for s in scenarios}) >= 4
assert len({s.observation_sigma for s in scenarios}) >= 4

for s in scenarios[:2]:
    for planner in ("space_time_astar", "dstar_dwa"):
        rec = run_closed_loop(s, planner, max_ticks=30)
        assert rec["metrics"]["scenario_id"] == s.scenario_id
        assert rec["replans"]
        assert all("planning_time_s" in x for x in rec["replans"])

print("PHASE2 SMOKE TEST: PASS")
print(f"scenarios={len(scenarios)}")
