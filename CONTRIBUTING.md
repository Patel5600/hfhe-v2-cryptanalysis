# Contributing

Contributions that extend, correct, or independently verify the documented experiments
are welcome.

## Principles

1. **Reproducibility first.** Every new experiment must include: a fixed seed, a null
   model, a pre-specified decision rule, and machine-readable output in `results/`.
2. **No premature claims.** A statistical deviation is insufficient. Follow the
   five-condition test in `docs/METHODOLOGY.md` before labelling anything an exploit.
3. **Negative results count.** A well-designed experiment that closes another branch
   is as valuable as a positive result.

## Workflow

1. Fork the repository and create a feature branch.
2. Add your experiment script under `analysis/<phase>/`.
3. Add your results JSON under `results/<phase>/`.
4. Update `docs/ATTACK_TREE.md` to reflect the new branch status.
5. Open a pull request with a description of the observable, null model, and outcome.

## Code style

- Python 3.10+, type annotations encouraged.
- `black` for formatting, `ruff` for linting.
- All scripts must be runnable standalone: `python analysis/.../myscript.py`.
