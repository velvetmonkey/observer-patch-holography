import Mathlib
import ObservableNormalForms.Scatter.Circuit

/-!
# Negative controls: every guard watched failing

House rule: a guard nobody has watched fail is not a guard.  Each certificate
field of `Layout.Cert` is exercised here by a deliberately broken layout that
(a) provably admits **no** certificate, with the violated field named, and
(b) exhibits the concrete bad behaviour the certificate exists to exclude.

* `collide` / `collideSwapped` — **write collision (cross-talk)**: two
  patches drive the same register with contradictory tables.  No certificate
  (`singleWriter` fails, witness: the two patches), and the produced value
  depends on patch order (`collide_order_dependent`), which is exactly the
  nondeterminism the single-writer clause excludes.  Write fan-*out* is
  excluded at the type level: a `Patch` has exactly one write port.

* `latch` — **cycle**: two registers feeding each other.  No certificate
  (`descending` fails: any rank must satisfy `rank 1 < rank 0 < rank 1`),
  no fixed point, and no register state ever has zero mismatch — settling
  genuinely fails, it is not merely unproved.

* `selfLoop` — **degenerate cycle**: a patch reading its own write port
  through negation.  Same failure mode in the smallest case.

* `fanOut` — **read fan-out is safe** (positive control): a circuit whose
  input wire feeds three gates settles from every register state; fan-out of
  *reads* needs no gadget under the directional rule.

The layouts here are outside the certified class, so nothing in
`ObservableNormalForms.Scatter.Layout` claims anything about them; these
controls show the boundary sits where the docstrings say it does.
-/

namespace ObservableNormalForms
namespace Scatter

/-! ### Control 1: write collision (cross-talk) -/

/-- Two patches drive register 0 with contradictory constant tables. -/
@[reducible] def collide : Layout :=
  { regCount := 1
    patches := [⟨[], 0, fun _ => true⟩, ⟨[], 0, fun _ => false⟩] }

/-- The same two patches in the opposite order. -/
@[reducible] def collideSwapped : Layout :=
  { regCount := 1
    patches := [⟨[], 0, fun _ => false⟩, ⟨[], 0, fun _ => true⟩] }

/-- The write collision admits no certificate: `singleWriter` fails on the
two colliding patches. -/
theorem collide_no_cert : IsEmpty collide.Cert := by
  constructor
  intro C
  have h := C.singleWriter ⟨[], 0, fun _ => true⟩ List.mem_cons_self
    ⟨[], 0, fun _ => false⟩ (List.mem_cons_of_mem _ List.mem_cons_self) rfl
  have := congrFun (congrArg Patch.table h) []
  simp at this

/-- The bad behaviour the guard excludes, watched happening: with a write
collision the round's outcome depends on patch order. -/
theorem collide_order_dependent :
    collide.round (fun _ => false) 0 = true ∧
    collideSwapped.round (fun _ => false) 0 = false := by decide

/-! ### Control 2: a two-register cycle -/

/-- A latch: register 0 recomputes `¬ r1`, register 1 recomputes `r0`. -/
@[reducible] def latch : Layout :=
  { regCount := 2
    patches := [⟨[1], 0, fun bs => !(bs.getD 0 false)⟩,
                ⟨[0], 1, fun bs => bs.getD 0 false⟩] }

/-- The cycle admits no certificate: `descending` would need
`rank 1 < rank 0 < rank 1`. -/
theorem latch_no_cert : IsEmpty latch.Cert := by
  constructor
  intro C
  have h1 : C.rank 1 < C.rank 0 := by
    simpa using C.descending ⟨[1], 0, fun bs => !(bs.getD 0 false)⟩
      List.mem_cons_self 1 List.mem_cons_self
  have h2 : C.rank 0 < C.rank 1 := by
    simpa using C.descending ⟨[0], 1, fun bs => bs.getD 0 false⟩
      (List.mem_cons_of_mem _ List.mem_cons_self) 0 List.mem_cons_self
  omega

/-- Settling genuinely fails on the cycle: no register state has zero
mismatch. -/
theorem latch_never_zero_mismatch :
    ∀ x : Fin 2 → Bool, 0 < latch.totalMismatch x := by decide

/-- The cycle has no fixed point of the directional round at all. -/
theorem latch_no_fixed_point :
    ∀ x : Fin 2 → Bool, ∃ a, latch.round x a ≠ x a := by decide

/-! ### Control 3: the smallest cycle -/

/-- A patch reading its own write port through negation. -/
@[reducible] def selfLoop : Layout :=
  { regCount := 1
    patches := [⟨[0], 0, fun bs => !(bs.getD 0 false)⟩] }

/-- No certificate: `descending` would need `rank 0 < rank 0`. -/
theorem selfLoop_no_cert : IsEmpty selfLoop.Cert := by
  constructor
  intro C
  have h : C.rank 0 < C.rank 0 := by
    simpa using C.descending ⟨[0], 0, fun bs => !(bs.getD 0 false)⟩
      List.mem_cons_self 0 List.mem_cons_self
  omega

/-- And indeed no state of the self-loop has zero mismatch. -/
theorem selfLoop_never_zero_mismatch :
    ∀ x : Fin 1 → Bool, 0 < selfLoop.totalMismatch x := by decide

/-! ### Control 4: read fan-out is safe (positive control) -/

/-- Wire 0 feeds three gate reads: `1 = OR(a, a)`, `2 = AND(a, a)`,
`3 = XOR(w1, w2)`. -/
@[reducible] def fanOut : Circuit where
  wires := 4
  node := fun w =>
    match w with
    | ⟨0, _⟩ => .input
    | ⟨1, _⟩ => .gate or 0 0
    | ⟨2, _⟩ => .gate and 0 0
    | ⟨3, _⟩ => .gate Bool.xor 1 2
    | ⟨n + 4, h⟩ => absurd h (by omega)
  topo := by decide

theorem fanOut_depthBound : fanOut.depthBound = 2 := by decide

/-- Read fan-out settles, by instantiation of the generic theorem. -/
theorem fanOut_settles (x : fanOut.compile.RegState) :
    fanOut.compile.evolve fanOut.depthBound x = fanOut.eval x :=
  fanOut.compile_settles x

/-- The same fact for every start state, checked by raw kernel
computation. -/
theorem fanOut_settles_kernel :
    ∀ (x : Fin 4 → Bool) a, fanOut.compile.evolve 2 x a = fanOut.eval x a := by
  decide

end Scatter
end ObservableNormalForms
