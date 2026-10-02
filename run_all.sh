#!/bin/bash
# Usage: ./run_all.sh --analysis-only   (minutes; regenerates every analysis output, figure and the number check from stored per-run results)
#        ./run_all.sh --full            (hours: re-runs every planner experiment first; each script checkpoints and resumes)
set -e
cd "$(dirname "$0")"
export PYTHONPATH=abaco:danger_radius:baselines:experiments
cd experiments
if [ "$1" == "--full" ]; then
  python3 sweep_drsafe_t.py && python3 select_drsafe_t.py               # tuning, seeds 6000-6029
  python3 run_main_new_arms.py && python3 run_ablation.py && python3 run_apf_main.py   # seeds 10000-10299
  python3 run_suite.py 10                                               # randomized suite, exact arms: 10 seeds per scenario
  ./run_fresh_chain.sh                                                  # seeds 20000-20299 + noisy-estimate stages (stage 4 optional, see script)
  python3 fallback_audit.py && python3 sweep_drsafe_t_extend.py
elif [ "$1" != "--analysis-only" ]; then echo "usage: $0 --analysis-only | --full"; exit 1; fi
python3 analyze_new_main.py && python3 analyze_suite.py && python3 analyze_suite_holm8.py 10 && python3 analyze_suite_holm8.py 5 && python3 analyze_ablation.py && python3 analyze_apf_main.py
python3 analyze_soft_primary.py
python3 analyze_start_cell_adjusted.py && python3 analyze_fresh.py && python3 analyze_noise.py && python3 analyze_fallback.py
python3 analyze_start_cell_coprimary.py && python3 select_drsafe_t_extended.py
python3 make_figures_drsafe_t.py && python3 make_figures_fresh.py && python3 make_figures_pilot.py && python3 make_figure4_v2.py
cd .. && python3 experiments/make_figures_progression.py && cd experiments
echo "Number check skipped: pass the final manuscript explicitly to experiments/check_paper_numbers.py"
# after any change to planner code:  python3 verify_reproduction.py 14   (re-runs sampled stored runs; ~1 min)
