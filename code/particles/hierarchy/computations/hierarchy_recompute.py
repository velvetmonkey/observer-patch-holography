#!/usr/bin/env python3
"""
Recompute the OPH R_U hierarchy witness.

This script intentionally uses mpmath for high-precision formula-stack evaluation and mpmath.iv
for interval derivative enclosures. It is a reproducibility witness, not a substitute for a
proof-assistant-certified interval log.
"""
import mpmath as mp
mp.mp.dps = 80

P = mp.mpf('1.630968209403959324879279847782648941')
a = mp.mpf('0.041124336195630495')
N2, N3 = 128, 64
b1, b2, b3 = mp.mpf(33)/5, mp.mpf(1), mp.mpf(-3)

def ell_su2(t, N=N2):
    Z=S=mp.mpf('0')
    for n in range(N+1):
        j=mp.mpf(n)/2
        d=2*j+1
        C=j*(j+1)
        w=d*mp.e**(-t*C)
        Z += w
        S += w*mp.log(d)
    return S/Z

def ell_su3(t, N=N3):
    Z=S=mp.mpf('0')
    for p in range(N+1):
        for q in range(N+1):
            d=mp.mpf((p+1)*(q+1)*(p+q+2))/2
            C=mp.mpf(p*p+q*q+p*q+3*p+3*q)/3
            w=d*mp.e**(-t*C)
            Z += w
            S += w*mp.log(d)
    return S/Z

def phi_for_a(av):
    av=mp.mpf(av)
    MU=mp.e**(-2*mp.pi)*P**(mp.mpf(1)/6)
    v=P**(-mp.mpf(1)/2)*mp.e**(-2*mp.pi/(4*av))
    def alpha(mu,b):
        return 1/(1/av + b/(2*mp.pi)*mp.log(MU/mu))
    def fmu(mu):
        return v/2*mp.sqrt(4*mp.pi*alpha(mu,b2)+4*mp.pi*(mp.mpf(3)/5*alpha(mu,b1)))
    mu=v*mp.mpf('0.3714')
    for _ in range(60):
        mu=fmu(mu)
    t2=4*mp.pi**2*alpha(mu,b2)
    t3=4*mp.pi**2*alpha(mu,b3)
    return ell_su2(t2)+ell_su3(t3)-P/4

if __name__ == "__main__":
    MU=mp.e**(-2*mp.pi)*P**(mp.mpf(1)/6)
    v=P**(-mp.mpf(1)/2)*mp.e**(-2*mp.pi/(4*a))
    print("M_U/E_star", mp.nstr(MU, 60))
    print("v/E_star", mp.nstr(v, 60))
    print("Phi(lower)", mp.nstr(phi_for_a(mp.mpf('0.041123336195630494')), 60))
    print("Phi(candidate)", mp.nstr(phi_for_a(a), 60))
    print("Phi(upper)", mp.nstr(phi_for_a(mp.mpf('0.041125336195630496')), 60))
