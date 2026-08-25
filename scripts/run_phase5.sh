#!/usr/bin/env bash
# Phase 5: Pedersen commitments
set -e
ARTIFACTS="${1:-$ARTIFACTS_DIR}"
python analysis/phase5_pedersen/pc_distribution.py --artifacts "$ARTIFACTS"
python analysis/phase5_pedersen/cross_field_inversion.py --artifacts "$ARTIFACTS"
