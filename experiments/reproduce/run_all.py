#!/usr/bin/env python3
"""
Run all HFHE v2 cryptanalysis experiments end-to-end.

Usage:
    python experiments/reproduce/run_all.py --artifacts /path/to/artifacts
"""
import argparse, subprocess, sys
from pathlib import Path

PHASES = [
    ("Phase 0 — Artifact verification",
     "analysis/00_artifact_verification/secret_ct_structure.py"),
    ("Phase 5 — PC distribution",
     "analysis/05_commitments/pc_distribution.py"),
    ("Phase 5 — Cross-field inversion",
     "analysis/05_commitments/cross_field_inversion.py"),
    ("Phase 6 — Character/parity tests",
     "analysis/06_wrapped_ratio/character_tests.py"),
    ("Phase 6 — Toy ratio experiment",
     "analysis/06_wrapped_ratio/toy_ratio_experiment.py"),
    ("Phase 7 — LPN complexity",
     "analysis/07_lpn_complexity/work_factor.py"),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", required=True,
                        help="Directory containing secret.ct and pk.bin")
    args = parser.parse_args()
    root = Path(__file__).parent.parent.parent
    artifacts = Path(args.artifacts).resolve()

    for label, script in PHASES:
        print(f"\n{'='*60}")
        print(f"  {label}")
        print(f"{'='*60}")
        rc = subprocess.run(
            [sys.executable, str(root / script), "--artifacts", str(artifacts)],
            cwd=root,
        ).returncode
        if rc != 0:
            print(f"[WARN] {script} exited with code {rc}")

    print("\n[DONE] All phases complete. See results/ for JSON outputs.")


if __name__ == "__main__":
    main()
