# Terminal Session 10 — Final Artifact Hash Verification

## Final verification before committing investigation

```powershell
cd C:\Dev\octra

python -c "
import hashlib
for fn,expected in [
    ('secret.ct', '5da7f82724838bf7a8c4fe95fbf6d573b621c04c9b2f7ae849545cf60223fbab'),
    ('pk.bin',    '1e788edff9dea19a782defae053f3757ccf5edd41cd3e24ae44e1496045e9410'),
]:
    got = hashlib.sha256(open(fn,'rb').read()).hexdigest()
    print(fn, 'MATCH' if got==expected else f'MISMATCH got={got}')
"

git -C C:\Dev\pvac_hfhe_cpp log -1 --format='%H %ai %s'
```

## Output

```
secret.ct  MATCH
pk.bin     MATCH
071b0e909c119de815e284b347c4bd979cb59ef3 2026-07-09 18:29:59 +0000 public matrix sampling
```

## Summary of all experiments run

| Session | Experiment | Result |
|---------|-----------|--------|
| 03 | Artifact extraction | 22 CT objects, 1829 edges, pk params verified |
| 04 | H digest verification | MATCH |
| 05 | H rank (GF2) | 8192/8192 full rank |
| 06 | powg_B analysis | B=337=ord(g), trivial |
| 07 | Cross-field inversion | 0/100,000 cancellations |
| 08 | Population B distinguisher | KS p=0.523, CLOSED |
| 09 | Ratio/character/parity | All p>>0.05, CLOSED |
| 10 | Final hash verification | MATCH |
