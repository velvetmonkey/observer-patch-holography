"""Independent verification of Pro's compact-Lie trichotomy. Trust nothing."""
import itertools, math
PHI=(1+5**0.5)/2
CS=[1,15,20,12,12]; ORD=60
CH={'1':[1,1,1,1,1],'3':[3,-1,0,PHI,1-PHI],"3'":[3,-1,0,1-PHI,PHI],
    '4':[4,0,1,-1,-1],'5':[5,1,-1,0,0]}
DIM={'1':1,'3':3,"3'":3,'4':4,'5':5}
def inner(a,b): return sum(c*x*y for c,x,y in zip(CS,a,b))/ORD
def dec(chi): return {k:round(inner(chi,v)) for k,v in CH.items() if abs(inner(chi,v))>1e-9}

P12=[12,0,0,2,2]
print("P12 decomposition:", dec(P12))

# (a) Which submodules of P12 are RATIONAL? A rational rep has Galois-stable character.
# 3 and 3' are conjugate under sqrt5 -> -sqrt5, so they must appear with EQUAL multiplicity.
print("\n--- rational submodules of P12 (3 and 3' must pair) ---")
rational=[]
for use1 in (0,1):
  for use5 in (0,1):
    for usetrip in (0,1):   # 0 = neither triplet, 1 = BOTH triplets
      mods=[]; d=0
      if use1: mods.append('1'); d+=1
      if use5: mods.append('5'); d+=5
      if usetrip: mods+=['3',"3'"]; d+=6
      rational.append((tuple(mods),d))
for m,d in sorted(rational,key=lambda x:x[1]): print(f"  z = {str(m) if m else '(0)':32s} dim {d:2d} -> semisimple dim {12-d}")

# (b) compact semisimple dims reachable
SIMPLE={'su2':3,'su3':8,'so5':10,'g2':14,'su4':15,'so7':21}
def ss_types(n):
    out=[]
    def rec(rem,start,cur):
        if rem==0: out.append(tuple(cur)); return
        for i,(nm,d) in enumerate(list(SIMPLE.items())[start:],start):
            if d<=rem: rec(rem-d,i,cur+[nm])
    rec(n,0,[]); return out
print("\n--- compact semisimple algebras by dimension ---")
for n in range(0,13):
    t=ss_types(n)
    print(f"  dim {n:2d}: {t if t else 'NONE'}")

print("\n=== VERDICT: which (z, ss) pairs survive? ===")
for m,d in sorted(rational,key=lambda x:x[1]):
    ssd=12-d; types=ss_types(ssd)
    zmod={k:1 for k in m}
    # complement module that the semisimple part must carry
    comp={k:1 for k in ['1','3',"3'",'5'] if k not in m}
    note=""
    if not types and ssd>0: note="EXCLUDED (no compact ss algebra of this dim)"
    elif ssd==0: note="ALLOWED -> u(1)^12 (abelian)"
    else:
        ok=[]
        for t in types:
            # A5 -> S_k permuting ideals is trivial (A5 simple, |A5|=60 > k! for k<=4)
            # so each ideal is A5-stable; ideal of dim 3 carries a 3-dim module (1+1+1, 3, or 3')
            # ideal su(3) carries 3+5 or 3'+5
            if all(x=='su2' for x in t):
                # k copies of su2, each carries a 3-dim A5 module -> cannot contain '5'
                if '5' in comp: continue
                ok.append(t)
            elif sorted(t)==sorted(['su3','su2']):
                # su3 -> 3+5 (or 3'+5); su2 -> 3' (or 3)
                if '5' in comp and '3' in comp and "3'" in comp: ok.append(t)
        note = f"ALLOWED via {ok}" if ok else "EXCLUDED (module mismatch)"
    print(f"  z={str(m) or '()':28s} ss dim {ssd:2d} | ss carries {sorted(comp)} | {note}")
