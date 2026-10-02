"""Structured logging for phase-2 closed-loop runs."""
from __future__ import annotations
import json, os, time


class RunLogger:
    def __init__(self):
        self.replans = []
        self.events = []
        self.t0 = time.perf_counter()

    def replan(self, tick, planner, planning_seconds, path_length=0, success=False):
        self.replans.append({
            "tick": int(tick), "planner": planner,
            "planning_time_s": float(planning_seconds),
            "planned_path_length": float(path_length), "success": bool(success),
        })

    def event(self, tick, kind, **data):
        self.events.append({"tick": int(tick), "kind": kind, **data})

    def finish(self, **metrics):
        return {
            "metrics": metrics,
            "replans": self.replans,
            "events": self.events,
            "wall_time_s": time.perf_counter() - self.t0,
        }


def save_json(path, record):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
    os.replace(tmp, path)
