#!/bin/bash
# Post hoc phase-5 analyses (legacy-pheromone adapter; ACO+DWA with a prediction-aware ACO stage).
# Usage: ./run_phase5.sh --analysis-only   (seconds; regenerates results/phase5/*.json from the stored per-run .jsonl files)
#        ./run_phase5.sh --full            (about 40 min on one core; re-runs every phase-5 experiment; each run resumes)
set -e
cd "$(dirname "$0")"
export PYTHONPATH=../abaco:../danger_radius:../baselines:.
if [ "$1" == "--full" ]; then
  python3 verify_phase5_gate.py                                              # gate: must report 0 mismatches
  ADAPTER=legacy python3 phase5_run.py legacy HB,HBP,DR-T,DR-SAFE            # item (iii) rules restored
  ADAPTER=legacy P5_CAP=500 P5_AGEQ=0 python3 phase5_run.py cap_only DR-T    # single factor: 500-step limit only
  ADAPTER=legacy P5_CAP=100 P5_AGEQ=1 python3 phase5_run.py ageq_only DR-T   # single factor: age-based deposit only
  python3 phase5_run.py hybrid aco_dwa_hbp,aco_dwa_drt                       # ACO+DWA variants, flat deposit
  ADAPTER=legacy python3 phase5_run.py hybrid_legacy aco_dwa_hb,aco_dwa_hbp,aco_dwa_drt   # ... age-based deposit
elif [ "$1" != "--analysis-only" ]; then echo "usage: $0 --analysis-only | --full"; exit 1; fi
python3 analyze_phase5.py
echo "Table check: python3 check_phase5_numbers.py <manuscript.docx>"
