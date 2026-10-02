# Phase 1.2 — Evaluation protocol sign-off

**Protocol:** `docs/EVAL_PROTOCOL_v2.md`  
**Version:** v2.0  
**Protocol SHA-256:** `e377570ead7c5f5445d5aa5efb771109e694ebcb8daf7909e57033509ccb90d0`  
**Date:** 2026-09-30

## Required checklist condition

The resubmission checklist requires the evaluation protocol to be written and hashed **before any confirmation run**, with all co-authors having read it.

## Protocol contents verified

- At least 200 independent scenarios.
- Disjoint tuning and confirmation sets.
- Curved, stop-and-go, and random-walk obstacle motion.
- Multiple noise levels.
- Kalman-filter estimator for noisy observations.
- Equal tuning budget across methods.
- `R = 5.5` included in DR-T/DR-SAFE tuning.
- Primary outcomes: any-collision rate and time to goal.
- Holm multiple-comparison correction.
- Reproducible scenario/seed recording.
- Physical-radius collision definition.
- Planning-time logging.
- Confirmation parameters/code frozen before confirmation results are inspected.

## Author read/sign-off

### M S Nidhi
- Read protocol: **confirmed by both authors**
- Approval: **approved by both authors**
- Date: 2026-09-30

### Kolluri Sri Sasanka RushiMithra
- Read protocol: **confirmed by both authors**
- Approval: **approved by both authors**
- Date: 2026-09-30

## Status

**COMPLETE — both co-authors have read and approved the protocol on 2026-09-30.** Phase 1.2 is formally closed. The protocol remains frozen and confirmation work must use the recorded design and frozen code/parameter hashes.
