#!/usr/bin/env bash
# Phase 2: PRF/LPN Generation
set -e
ARTIFACTS="${1:-$ARTIFACTS_DIR}"
python analysis/phase2_prf_lpn/population_b.py --artifacts "$ARTIFACTS"\n