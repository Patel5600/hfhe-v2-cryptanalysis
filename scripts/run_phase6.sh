#!/usr/bin/env bash
# Phase 6: Wrapped-mask ratio attacks
set -e
ARTIFACTS="${1:-$ARTIFACTS_DIR}"
python analysis/phase6_wrapped_ratio/character_tests.py --artifacts "$ARTIFACTS"
python analysis/phase6_wrapped_ratio/toy_ratio_experiment.py
