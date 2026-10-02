"""Closed-loop planner entry point with a supplied FastDStarLite replacement.

The historical standalone FastDStarLite source was not present in the recovered
archive. The class exported here is a newly authored runner-compatible
implementation in ``fast_dstar_lite.py``. It is not claimed to be the missing
historical source.
"""
from phase3_abaco_v2 import abaco_plan
from fast_dstar_lite import FastDStarLite

__all__ = ["abaco_plan", "FastDStarLite"]
