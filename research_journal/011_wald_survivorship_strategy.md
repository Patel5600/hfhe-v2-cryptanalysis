# Entry 011 — Wald's Survivorship Bias Strategy

**Date:** Mid-investigation  
**Status:** Methodology decision

## The Wald lesson

In WWII, statistician Abraham Wald advised the military NOT to armour the
already-damaged areas of returning planes, but to armour the areas with
no bullet holes (the planes that got those holes did not return).

## Application to this investigation

After closing the R_com, sigma, and tuple-order branches, there was pressure
to re-test the same surface with fancier statistics.

Wald says: stop re-armoring the already-hit surfaces. Attack what has not
been examined.

## What Wald told us to attack next

At this decision point, the unexplored branches were:
1. Joint prf_k cross-layer distinguisher (Phase 2)
2. H matrix rank and structure (Phase 4)
3. powg_B DLP (Phase 4)
4. Cross-field Fp/Z-l arithmetic (Phase 5)
5. Wrapped-ratio algebra (Phase 6)

All of these were subsequently attacked. All closed.

## Lesson documented

The strategy of exhausting the tested surface before exploring the untested
surface is the correct approach for systematic cryptanalysis.
It prevents wasted cycles and ensures complete coverage.
