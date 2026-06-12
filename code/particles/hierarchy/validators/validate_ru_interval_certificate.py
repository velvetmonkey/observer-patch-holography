#!/usr/bin/env python3
import json, pathlib, decimal, sys
from decimal import Decimal
decimal.getcontext().prec=80

def main(cert_path="certificates/R_U_krawczyk_certificate.json"):
    c = json.loads(pathlib.Path(cert_path).read_text())
    I_lo = Decimal(c["I_U"]["lower"]); I_hi = Decimal(c["I_U"]["upper"])
    K_lo = Decimal(c["K_I"]["lower"]); K_hi = Decimal(c["K_I"]["upper"])
    D_lo = Decimal(c["derivative_interval"]["lower"]); D_hi = Decimal(c["derivative_interval"]["upper"])
    ok = (I_lo < K_lo < K_hi < I_hi) and (D_hi < 0 or D_lo > 0)
    out = {
        "K_subset_interior_I": I_lo < K_lo < K_hi < I_hi,
        "derivative_excludes_zero": D_hi < 0 or D_lo > 0,
        "pass": ok
    }
    print(json.dumps(out, indent=2))
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv)>1 else "certificates/R_U_krawczyk_certificate.json"))
