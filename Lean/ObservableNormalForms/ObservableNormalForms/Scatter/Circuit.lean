import Mathlib
import ObservableNormalForms.Scatter.Layout

/-!
# Compiling finite acyclic Boolean circuits into directional layouts

A `Circuit` is a topologically indexed finite acyclic Boolean circuit: wire
`w` is either an input or is driven by a binary gate whose argument wires
have strictly smaller index (`Circuit.topo`).  Fan-out of *reads* is
unrestricted: a wire may feed any number of gates.

`Circuit.compile` produces a `Scatter.Layout`: one register per wire and one
patch per gate.  The patch of gate `w` has read ports at the gate's argument
wires, write port at `w`, and table given by the gate's Boolean function.
Input wires get no patch, so under the directional rule they are the
protected boundary.

`Circuit.compileCert` certifies the compiled layout with rank given by
`Circuit.depth` (gate depth).  Everything downstream is then an instance of
the generic certified-layout theorems:

* `Circuit.compile_intertwiner` — one directional scatter-project round on
  the compiled layout is one ranked synchronous step (on every register
  state of the compiled layout);
* `Circuit.compile_settles` — `depthBound` rounds from any register state
  reach the circuit's evaluation of that state's boundary;
* `Circuit.compile_settled_*` — the settled state is fixed with zero
  mismatch, and is the unique such state over its boundary;
* `Circuit.compile_regCount` / `Circuit.compile_patchCount` — exact resource
  formulas.

`Circuit.depth` and `Circuit.eval` are implemented with structural fuel so
that the kernel can evaluate them; concrete instances can therefore be
checked by `decide`.
-/

namespace ObservableNormalForms
namespace Scatter

/-- A wire is either a circuit input or a binary gate applied to two earlier
wires.  Arbitrary two-argument Boolean functions are allowed; unary gates are
the special case that ignores or duplicates an argument. -/
inductive Node (n : ℕ) where
  | input : Node n
  | gate (f : Bool → Bool → Bool) (i j : Fin n) : Node n

/-- The dependency list of a node. -/
def Node.deps {n : ℕ} : Node n → List (Fin n)
  | .input => []
  | .gate _ i j => [i, j]

/-- `true` exactly on gate nodes. -/
def Node.isGate {n : ℕ} : Node n → Bool
  | .input => false
  | .gate _ _ _ => true

/-- The compiled patch of a node sitting on wire `w`: gates become a patch
with read ports at the argument wires and write port `w`; inputs compile to
no patch. -/
def Node.patch? {n : ℕ} (w : Fin n) : Node n → Option (Patch n)
  | .input => none
  | .gate f i j =>
    some { reads := [i, j], write := w
           table := fun bs => f (bs.getD 0 false) (bs.getD 1 false) }

/-- A finite acyclic Boolean circuit, topologically indexed: every gate's
arguments have strictly smaller wire index. -/
structure Circuit where
  wires : ℕ
  node : Fin wires → Node wires
  topo : ∀ w : Fin wires, ∀ d ∈ (node w).deps, d.val < w.val

namespace Circuit

variable (c : Circuit)

theorem dep_lt {w i j : Fin c.wires} {f : Bool → Bool → Bool}
    (h : c.node w = .gate f i j) : i.val < w.val ∧ j.val < w.val :=
  ⟨c.topo w i (by rw [h]; simp [Node.deps]),
   c.topo w j (by rw [h]; simp [Node.deps])⟩

/-! ### Depth and evaluation, with structural fuel -/

/-- Fuelled gate depth; `depth` fixes the fuel at `w.val + 1`. -/
def depthFuel : ℕ → Fin c.wires → ℕ
  | 0, _ => 0
  | fuel + 1, w =>
    match c.node w with
    | .input => 0
    | .gate _ i j => max (depthFuel fuel i) (depthFuel fuel j) + 1

/-- The depth of a wire: 0 on inputs, one more than the maximal argument
depth on gates (`depth_input`, `depth_gate`). -/
def depth (w : Fin c.wires) : ℕ := c.depthFuel (w.val + 1) w

theorem depthFuel_congr :
    ∀ f₁ f₂ (w : Fin c.wires), w.val < f₁ → w.val < f₂ →
      c.depthFuel f₁ w = c.depthFuel f₂ w := by
  intro f₁
  induction f₁ with
  | zero => omega
  | succ f ih =>
    intro f₂ w _ h2
    cases f₂ with
    | zero => omega
    | succ g =>
      cases hn : c.node w with
      | input => simp [depthFuel, hn]
      | gate fb i j =>
        have hi := (c.dep_lt hn).1
        have hj := (c.dep_lt hn).2
        simp only [depthFuel, hn]
        rw [ih g i (by omega) (by omega), ih g j (by omega) (by omega)]

theorem depth_input {w : Fin c.wires} (h : c.node w = .input) :
    c.depth w = 0 := by
  simp [depth, depthFuel, h]

theorem depth_gate {w i j : Fin c.wires} {f : Bool → Bool → Bool}
    (h : c.node w = .gate f i j) :
    c.depth w = max (c.depth i) (c.depth j) + 1 := by
  have hi := (c.dep_lt h).1
  have hj := (c.dep_lt h).2
  show c.depthFuel (w.val + 1) w = _
  simp only [depthFuel, h]
  rw [c.depthFuel_congr w.val (i.val + 1) i (by omega) (by omega),
    c.depthFuel_congr w.val (j.val + 1) j (by omega) (by omega)]
  rfl

theorem depth_eq_zero_iff {w : Fin c.wires} :
    c.depth w = 0 ↔ c.node w = .input := by
  constructor
  · intro h
    cases hn : c.node w with
    | input => rfl
    | gate f i j => rw [c.depth_gate hn] at h; omega
  · exact c.depth_input

/-- Fuelled evaluation; `eval` fixes the fuel at `w.val + 1`. -/
def evalFuel (env : Fin c.wires → Bool) : ℕ → Fin c.wires → Bool
  | 0, w => env w
  | fuel + 1, w =>
    match c.node w with
    | .input => env w
    | .gate f i j => f (evalFuel env fuel i) (evalFuel env fuel j)

/-- Circuit evaluation over an environment: inputs read the environment,
gates apply their Boolean function to the evaluations of their arguments
(`eval_input`, `eval_gate`).  Only the environment's values on input wires
matter. -/
def eval (env : Fin c.wires → Bool) (w : Fin c.wires) : Bool :=
  c.evalFuel env (w.val + 1) w

theorem evalFuel_congr (env : Fin c.wires → Bool) :
    ∀ f₁ f₂ (w : Fin c.wires), w.val < f₁ → w.val < f₂ →
      c.evalFuel env f₁ w = c.evalFuel env f₂ w := by
  intro f₁
  induction f₁ with
  | zero => omega
  | succ f ih =>
    intro f₂ w _ h2
    cases f₂ with
    | zero => omega
    | succ g =>
      cases hn : c.node w with
      | input => simp [evalFuel, hn]
      | gate fb i j =>
        have hi := (c.dep_lt hn).1
        have hj := (c.dep_lt hn).2
        simp only [evalFuel, hn]
        rw [ih g i (by omega) (by omega), ih g j (by omega) (by omega)]

theorem eval_input {env : Fin c.wires → Bool} {w : Fin c.wires}
    (h : c.node w = .input) : c.eval env w = env w := by
  simp [eval, evalFuel, h]

theorem eval_gate {env : Fin c.wires → Bool} {w i j : Fin c.wires}
    {f : Bool → Bool → Bool} (h : c.node w = .gate f i j) :
    c.eval env w = f (c.eval env i) (c.eval env j) := by
  have hi := (c.dep_lt h).1
  have hj := (c.dep_lt h).2
  show c.evalFuel env (w.val + 1) w = _
  simp only [evalFuel, h]
  rw [c.evalFuel_congr env w.val (i.val + 1) i (by omega) (by omega),
    c.evalFuel_congr env w.val (j.val + 1) j (by omega) (by omega)]
  rfl

/-- A uniform depth bound for the whole circuit. -/
def depthBound : ℕ := ((List.finRange c.wires).map c.depth).foldr max 0

theorem le_foldr_max {l : List ℕ} {a b : ℕ} (h : a ∈ l) :
    a ≤ l.foldr max b := by
  induction l with
  | nil => cases h
  | cons hd tl ih =>
    rcases List.mem_cons.mp h with rfl | h
    · exact le_max_left _ _
    · exact le_trans (ih h) (le_max_right _ _)

theorem depth_le_depthBound (w : Fin c.wires) : c.depth w ≤ c.depthBound :=
  le_foldr_max (List.mem_map.mpr ⟨w, List.mem_finRange w, rfl⟩)

/-! ### The compiler -/

/-- **The compiler**: one register per wire, one patch per gate, no patch on
inputs.  This is the only bridge between circuits and layouts; the update
law itself (`Layout.round`) never inspects the circuit. -/
@[reducible] def compile : Layout :=
  { regCount := c.wires
    patches := (List.finRange c.wires).filterMap fun w => (c.node w).patch? w }

theorem mem_compile_iff {p : Patch c.wires} :
    p ∈ c.compile.patches ↔ ∃ w, (c.node w).patch? w = some p := by
  constructor
  · intro h
    obtain ⟨w, -, hw⟩ := List.mem_filterMap.mp h
    exact ⟨w, hw⟩
  · rintro ⟨w, hw⟩
    exact List.mem_filterMap.mpr ⟨w, List.mem_finRange w, hw⟩

theorem patch?_write {n : ℕ} {w : Fin n} {nd : Node n} {p : Patch n}
    (h : nd.patch? w = some p) : p.write = w := by
  cases nd with
  | input => simp [Node.patch?] at h
  | gate f i j =>
    simp only [Node.patch?, Option.some.injEq] at h
    rw [← h]

theorem compile_writer (w : Fin c.wires) :
    c.compile.writer w = (c.node w).patch? w := by
  cases hp : (c.node w).patch? w with
  | none =>
    rw [Layout.writer, List.find?_eq_none]
    intro p hp'
    obtain ⟨v, hv⟩ := c.mem_compile_iff.mp hp'
    simp only [decide_eq_true_eq]
    intro hpw
    rw [patch?_write hv] at hpw
    subst hpw
    rw [hv] at hp
    cases hp
  | some p =>
    have hmem : p ∈ c.compile.patches := c.mem_compile_iff.mpr ⟨w, hp⟩
    have hw : p.write = w := patch?_write hp
    have hsome : (c.compile.writer w).isSome := by
      rw [Layout.writer, List.find?_isSome]
      exact ⟨p, hmem, by simp [hw]⟩
    obtain ⟨q, hq⟩ := Option.isSome_iff_exists.mp hsome
    obtain ⟨v, hv⟩ := c.mem_compile_iff.mp (c.compile.writer_mem hq)
    have hqw : q.write = w := c.compile.writer_write hq
    have hvw : v = w := by rw [← patch?_write hv]; exact hqw
    subst hvw
    exact hq.trans (congrArg some (Option.some.inj (hv.symm.trans hp)))

/-- The compiled layout's certificate: rank is gate depth. -/
def compileCert : c.compile.Cert where
  rank := c.depth
  singleWriter := by
    intro p hp q hq hw
    obtain ⟨wp, hwp⟩ := c.mem_compile_iff.mp hp
    obtain ⟨wq, hwq⟩ := c.mem_compile_iff.mp hq
    have hww : wp = wq := by
      rw [← patch?_write hwp, ← patch?_write hwq]
      exact hw
    subst hww
    exact Option.some.inj (hwp.symm.trans hwq)
  descending := by
    intro p hp a ha
    obtain ⟨w, hw⟩ := c.mem_compile_iff.mp hp
    cases hn : c.node w with
    | input => rw [hn] at hw; simp [Node.patch?] at hw
    | gate f i j =>
      rw [hn] at hw
      simp only [Node.patch?, Option.some.injEq] at hw
      subst hw
      simp only [List.mem_cons, List.not_mem_nil, or_false] at ha
      rw [c.depth_gate hn]
      rcases ha with rfl | rfl
      · omega
      · omega
  writtenPos := by
    intro p hp
    obtain ⟨w, hw⟩ := c.mem_compile_iff.mp hp
    cases hn : c.node w with
    | input => rw [hn] at hw; simp [Node.patch?] at hw
    | gate f i j =>
      rw [hn] at hw
      simp only [Node.patch?, Option.some.injEq] at hw
      subst hw
      rw [c.depth_gate hn]
      omega
  unwrittenZero := by
    intro a h
    rw [c.compile_writer] at h
    cases hn : c.node a with
    | input => exact c.depth_input hn
    | gate f i j => rw [hn] at h; simp [Node.patch?] at h

/-! ### The intertwiner and settling, instantiated to compiled layouts -/

/-- **The intertwiner** (issue #626 target 3), compiled form: one directional
scatter-project round on the compiled layout of `c` equals one synchronous
step of the presented ranked system, on **every** register state of the
compiled layout.  States outside a compiled (more generally, certified)
layout are *not* covered; see the module docstring of
`ObservableNormalForms.Scatter.Layout`. -/
theorem compile_intertwiner (x : c.compile.RegState) :
    c.compile.round x = (c.compile.system c.compileCert).synchronousStep x :=
  c.compile.round_eq_synchronousStep c.compileCert x

/-- The compiled solution is circuit evaluation.  Proved by uniqueness of
generated extensions, not by re-running the recursion. -/
theorem compile_solution_eq_eval (x : c.compile.RegState) :
    c.compile.solution c.compileCert x = c.eval x := by
  have hext : (c.compile.system c.compileCert).IsGeneratedExtension
      (c.eval x) := by
    intro s hs
    have hn : ∃ f i j, c.node s = .gate f i j := by
      cases hn : c.node s with
      | input => exact absurd (c.depth_input hn) hs
      | gate f i j => exact ⟨f, i, j, rfl⟩
    obtain ⟨f, i, j, hn⟩ := hn
    show (c.compile.writer s).elim false
        (fun p => p.output (c.eval x)) = c.eval x s
    rw [c.compile_writer, hn]
    show f (c.eval x i) (c.eval x j) = c.eval x s
    exact (c.eval_gate hn).symm
  have hb : (c.compile.system c.compileCert).SameBoundary
      (c.compile.solution c.compileCert x) (c.eval x) := by
    intro s hs
    have hn : c.node s = .input := c.depth_eq_zero_iff.mp hs
    rw [c.compile.solution_rank_zero c.compileCert x hs, c.eval_input hn]
  exact (c.compile.system c.compileCert).generatedExtension_unique
    (c.compile.solution_isGeneratedExtension c.compileCert x) hext hb
    (fun s => c.depth_le_depthBound s)

/-- **Settling** (issue #626 target 4): `depthBound c` directional rounds
from **any** register state of the compiled layout reach the circuit's
evaluation of that state's input registers.  In particular the declared
output wire carries the circuit's output. -/
theorem compile_settles (x : c.compile.RegState) :
    c.compile.evolve c.depthBound x = c.eval x := by
  rw [c.compile.evolve_settles c.compileCert x
    (fun a => c.depth_le_depthBound a)]
  exact c.compile_solution_eq_eval x

/-- The settled state is a fixed point of the directional round. -/
theorem compile_settled_fixed (x : c.compile.RegState) :
    c.compile.round (c.eval x) = c.eval x := by
  rw [← c.compile_solution_eq_eval x]
  exact c.compile.round_solution c.compileCert x

/-- The settled state has zero total mismatch. -/
theorem compile_settled_mismatch (x : c.compile.RegState) :
    c.compile.totalMismatch (c.eval x) = 0 := by
  rw [← c.compile_solution_eq_eval x]
  exact c.compile.totalMismatch_solution c.compileCert x

/-- Uniqueness: any zero-mismatch state agreeing with `x` on the input wires
is the circuit evaluation.  This is the "unique zero-mismatch extension"
phrasing of #328/#626. -/
theorem compile_zeroMismatch_unique {x e : c.compile.RegState}
    (hboundary : ∀ a, c.depth a = 0 → e a = x a)
    (hm : c.compile.totalMismatch e = 0) : e = c.eval x := by
  rw [← c.compile_solution_eq_eval x]
  exact c.compile.zeroMismatch_unique c.compileCert
    (fun a => c.depth_le_depthBound a) hboundary hm

/-! ### Explicit resource bounds (issue #626 target 5) -/

/-- The number of gate nodes of the circuit. -/
def gateCount : ℕ := (List.finRange c.wires).countP fun w => (c.node w).isGate

/-- Register count formula: exactly one register per wire. -/
theorem compile_regCount : c.compile.regCount = c.wires := rfl

/-- Patch count formula: exactly one patch per gate. -/
theorem compile_patchCount : c.compile.patches.length = c.gateCount := by
  rw [compile, gateCount]
  rw [List.length_filterMap_eq_countP]
  refine List.countP_congr fun w _ => ?_
  cases hn : c.node w <;> simp [Node.patch?, Node.isGate]

end Circuit

end Scatter
end ObservableNormalForms
