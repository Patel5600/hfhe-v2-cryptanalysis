# Terminal Session 03 — Artifact Extraction

## Decompressing and parsing secret.ct

```python
import zlib, struct

raw = open('secret.ct', 'rb').read()
MAGIC = b'OCTRA-HFHE-BTY02'
assert raw[:16] == MAGIC
body = zlib.decompress(raw[16:])
print(f'Decompressed: {len(body):,} bytes')

off = 0
n_ct = 0
while off < len(body):
    tag = body[off]; off += 1
    sz = struct.unpack_from('<Q', body, off)[0]; off += 8
    blob = body[off:off+sz]; off += sz
    if tag == 0:
        n_ct += 1
        n_edges = struct.unpack_from('<Q', blob, 0)[0]
        print(f'  CT {n_ct}: {n_edges} edges')
print(f'Total CT objects: {n_ct}')
```

## Output

```
Decompressed: 19,073,XXX bytes
  CT 1: 1829 edges
  CT 2: 1829 edges
  ...
  CT 22: 1829 edges
Total CT objects: 22
```

## Decompressing pk.bin

```python
import zlib, struct
raw = open('pk.bin','rb').read()
data = zlib.decompress(raw)
print(f'pk.bin decompressed: {len(data):,} bytes')

# Read header
fields = ['B','m_bits','n_bits','h_col_wt','x_col_wt',
          'err_wt','lpn_n','lpn_t','tau_num','tau_den']
off = 0
for f in fields:
    v = struct.unpack_from('<I', data, off)[0]; off += 4
    print(f'  {f} = {v}')
```

## Output

```
pk.bin decompressed: 17,110,454 bytes
  B        = 337
  m_bits   = 8192
  n_bits   = 16384
  h_col_wt = 192
  x_col_wt = 128
  err_wt   = 128
  lpn_n    = 4096
  lpn_t    = 16384
  tau_num  = 1
  tau_den  = 8
```
