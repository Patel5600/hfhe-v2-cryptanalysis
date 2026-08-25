# Terminal Session 01 — Clone and Pin

## Commands executed

```powershell
# Clone challenge repo
git clone https://github.com/octra-labs/hfhe-challenge C:\Dev\octra
cd C:\Dev\octra
git log -1
# commit 071b0e9...

# Clone implementation
git clone https://github.com/octra-labs/pvac_hfhe_cpp C:\Dev\pvac_hfhe_cpp
cd C:\Dev\pvac_hfhe_cpp
git checkout 071b0e909c119de815e284b347c4bd979cb59ef3

# Verify artifact hashes
python -c "
import hashlib
for fn in ['secret.ct', 'pk.bin']:
    h = hashlib.sha256(open(fn,'rb').read()).hexdigest()
    s = len(open(fn,'rb').read())
    print(fn, h, s)
"
```

## Output

```
secret.ct  5da7f82724838bf7a8c4fe95fbf6d573b621c04c9b2f7ae849545cf60223fbab  1963107
pk.bin     1e788edff9dea19a782defae053f3757ccf5edd41cd3e24ae44e1496045e9410  3042901
```

## Key files found

```
C:\Dev\octra\secret.ct                                   (1.9 MB compressed)
C:\Dev\octra\pk.bin                                      (2.9 MB compressed)
C:\Dev\octra\source\pvac_artifact_serialize.hpp          (serializer)
C:\Dev\octra\source\hfhe_bounty_artifact.cpp             (bundle parser)
C:\Dev\octra\source\tools\verify_lpn_sample_binding.cpp (verifier)
C:\Dev\pvac_hfhe_cpp\include\pvac\core\types.hpp         (data types)
C:\Dev\pvac_hfhe_cpp\include\pvac\crypto\lpn.hpp         (PRF construction)
C:\Dev\pvac_hfhe_cpp\include\pvac\ops\encrypt.hpp        (encryption)
C:\Dev\pvac_hfhe_cpp\include\pvac\crypto\ristretto255.hpp (Pedersen commitment)
```
