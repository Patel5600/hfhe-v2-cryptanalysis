"""Parse pk.bin from the HFHE v2 challenge."""
import zlib, struct
from pathlib import Path
from typing import Any


def parse_pk_bin(path: str | Path) -> dict[str, Any]:
    """Return dict with public key parameters and H matrix."""
    raw = Path(path).read_bytes()
    data = zlib.decompress(raw)
    # Header: B(u32), m_bits(u32), n_bits(u32), h_col_wt(u32), x_col_wt(u32),
    #         err_wt(u32), lpn_n(u32), lpn_t(u32), tau_num(u32), tau_den(u32)
    off = 0
    fields = ["B", "m_bits", "n_bits", "h_col_wt", "x_col_wt",
              "err_wt", "lpn_n", "lpn_t", "tau_num", "tau_den"]
    params: dict[str, Any] = {}
    for f in fields:
        v, = struct.unpack_from("<I", data, off); off += 4
        params[f] = v
    params["tau"] = params["tau_num"] / params["tau_den"]
    # H matrix: n_bits columns of m_bits bits
    col_bytes = (params["m_bits"] + 7) // 8
    H_cols = []
    for _ in range(params["n_bits"]):
        col = data[off: off + col_bytes]; off += col_bytes
        H_cols.append(col)
    params["H_cols"] = H_cols
    return params
