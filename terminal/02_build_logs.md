# Terminal Session 02 — Build Logs

```bash
$ g++ -O2 -std=c++17 -Iinclude -c source/pvac_artifact_serialize.hpp
$ g++ -O2 -std=c++17 -Iinclude source/hfhe_bounty_artifact.cpp -lz -o build/bounty_parser
$ g++ -O2 -std=c++17 -Iinclude source/tools/verify_lpn_sample_binding.cpp -o build/verify_binding
$ ./build/verify_binding
[INFO] Binding verifier compiled successfully.
```\n