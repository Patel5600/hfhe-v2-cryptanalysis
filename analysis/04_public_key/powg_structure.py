"""Checks the mathematical structure of the public powg_B sequence."""
from __future__ import annotations

P = 2**127 - 1


def check_sequence(powg: list[int]) -> dict[str, int | bool]:
    if not powg:
        return {"count": 0, "sequence_ok": False, "order_ok": False}
    g = powg[1] if len(powg) > 1 else 1
    ok = powg[0] == 1
    for i in range(len(powg) - 1):
        ok &= (powg[i + 1] % P) == (powg[i] * g % P)
    order_ok = pow(g, 337, P) == 1 and g != 1
    return {"count": len(powg), "sequence_ok": ok, "order_337": order_ok}


if __name__ == "__main__":
    print("Feed decoded powg_B integers from the public key.")
