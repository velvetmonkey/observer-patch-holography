import Geometry.SourceCheckpointPipeline

/-!
# Cut capacity of an isolated two-record path

All means and retained samples in this module use exact real arithmetic on a
declared path. The statements do not choose a physical record interface or
deadline, and make no claim about finite precision.
-/

set_option autoImplicit false

namespace OPH.SourceCheckpointPathBound
noncomputable section
open OPH.SourceTemporalGuard
open ObserverPatchHolography.ScalarSeamRepair

/-- Two independent real source deviations. -/
abbrev Pair := ℝ × ℝ

/-- The ports of a path of `d` edges. -/
abbrev Port (d : ℕ) := Fin (d + 1)

/-- The only allowed mean for path edge `i`. -/
def pathEdge (d : ℕ) (i : Fin d) : Port d × Port d :=
  (i.castSucc, i.succ)

/-- The source deviations occupy ports zero and one; other ports are calibrated. -/
def initialState (d : ℕ) (p : Pair) (i : Port d) : ℝ :=
  if (i : ℕ) = 0 then p.1 else if (i : ℕ) = 1 then p.2 else 0

/-- The receiver is sampled before the first mean. -/
def initial (d : ℕ) : Checkpoint Pair (Port d) where
  state := initialState d
  record p := [initialState d p (Fin.last d)]

private def segment (d start : ℕ) : (n : ℕ) → start + n ≤ d → List (Fin d)
  | 0, _ => []
  | n + 1, h => segment d start n (by omega) ++ [⟨start + n, by omega⟩]

private theorem segment_length (d start n : ℕ) (h : start + n ≤ d) :
    (segment d start n h).length = n := by
  induction n with
  | zero => rfl
  | succ n ih => simp [segment, ih]

/-- The serial two-wave word first uses edges `1, …, d-1` and then edges
`0, …, d-1`. -/
def serialWord : (d : ℕ) → List (Fin d)
  | 0 => []
  | d + 1 =>
      segment (d + 1) 1 d (by omega) ++
      segment (d + 1) 0 (d + 1) (by omega)

/-- The serial word has the proposed sharp length. -/
theorem serialWord_length (d : ℕ) (hd : 1 ≤ d) :
    (serialWord d).length = 2 * d - 1 := by
  cases d with
  | zero => omega
  | succ n =>
    simp [serialWord, segment_length]
    omega

private def DownstreamEq {d : ℕ} (cut : Fin d)
    (s t : Port d → ℝ) : Prop :=
  ∀ j : Port d, cut.val < j.val → s j = t j

private theorem average_preserves_downstream {d : ℕ}
    (cut edge : Fin d) (hne : edge ≠ cut)
    (s t : Port d → ℝ) (h : DownstreamEq cut s t) :
    DownstreamEq cut (pairAverage edge.castSucc edge.succ s)
      (pairAverage edge.castSucc edge.succ t) := by
  intro j hj
  by_cases hlt : edge.val < cut.val
  · have hleft : j ≠ edge.castSucc := by
      intro he
      have : j.val = edge.val := congrArg Fin.val he
      omega
    have hright : j ≠ edge.succ := by
      intro he
      have : j.val = edge.val + 1 := by simpa using congrArg Fin.val he
      omega
    simp [pairAverage, hleft, hright, h j hj]
  · have hgt : cut.val < edge.val := by
      have : edge.val ≠ cut.val := by
        intro he
        exact hne (Fin.ext he)
      omega
    have hleft : cut.val < edge.castSucc.val := by simpa using hgt
    have hright : cut.val < edge.succ.val := by simp; omega
    by_cases hseam : j = edge.castSucc ∨ j = edge.succ
    · simp [pairAverage, hseam, h edge.castSucc hleft, h edge.succ hright]
    · simp [pairAverage, hseam, h j hj]

private theorem run_preserves_downstream {d : ℕ} (cut : Fin d)
    (c : Checkpoint Pair (Port d)) (w : List (Fin d))
    (p q : Pair) (hrec : c.record p = c.record q)
    (hdown : DownstreamEq cut (c.state p) (c.state q))
    (havoid : ∀ edge ∈ w, edge ≠ cut) :
    (run (Fin.last d) (w.map (pathEdge d)) c).record p =
      (run (Fin.last d) (w.map (pathEdge d)) c).record q ∧
    DownstreamEq cut
      ((run (Fin.last d) (w.map (pathEdge d)) c).state p)
      ((run (Fin.last d) (w.map (pathEdge d)) c).state q) := by
  induction w generalizing c with
  | nil => exact ⟨hrec, hdown⟩
  | cons edge rest ih =>
    have hroot : cut.val < (Fin.last d).val := by
      simpa using cut.isLt
    have hnext : DownstreamEq cut
        ((advance (Fin.last d) c (pathEdge d edge)).state p)
        ((advance (Fin.last d) c (pathEdge d edge)).state q) := by
      exact average_preserves_downstream cut edge (havoid edge (by simp))
        (c.state p) (c.state q) hdown
    have hnextrec : (advance (Fin.last d) c (pathEdge d edge)).record p =
        (advance (Fin.last d) c (pathEdge d edge)).record q := by
      exact congrArg₂ List.cons (hnext (Fin.last d) hroot) hrec
    simpa only [List.map_cons, run] using
      ih (advance (Fin.last d) c (pathEdge d edge)) hnextrec hnext
        (by intro e he; exact havoid e (by simp [he]))

private def LinearState {d : ℕ} (c : Checkpoint Pair (Port d)) : Prop :=
  (∀ p q : Pair, c.state (p + q) = c.state p + c.state q) ∧
  (∀ (r : ℝ) (p : Pair), c.state (r • p) = r • c.state p)

private theorem initial_linear (d : ℕ) : LinearState (initial d) := by
  constructor
  · intro p q
    funext j
    by_cases h0 : j.val = 0 <;> by_cases h1 : j.val = 1 <;>
      simp [initial, initialState, h0, h1, Pi.add_apply]
  · intro r p
    funext j
    by_cases h0 : j.val = 0 <;> by_cases h1 : j.val = 1 <;>
      simp [initial, initialState, h0, h1, Pi.smul_apply]

private theorem advance_linear {d : ℕ} (c : Checkpoint Pair (Port d))
    (e : Port d × Port d) (h : LinearState c) :
    LinearState (advance (Fin.last d) c e) := by
  constructor
  · intro p q
    change pairAverage e.1 e.2 (c.state (p + q)) =
      pairAverage e.1 e.2 (c.state p) + pairAverage e.1 e.2 (c.state q)
    rw [h.1 p q, map_add]
  · intro r p
    change pairAverage e.1 e.2 (c.state (r • p)) =
      r • pairAverage e.1 e.2 (c.state p)
    rw [h.2 r p, map_smul]

private theorem run_linear {d : ℕ} (c : Checkpoint Pair (Port d))
    (w : List (Fin d)) (h : LinearState c) :
    LinearState (run (Fin.last d) (w.map (pathEdge d)) c) := by
  induction w generalizing c with
  | nil => exact h
  | cons e rest ih =>
    simpa only [List.map_cons, run] using
      ih (advance (Fin.last d) c (pathEdge d e))
        (advance_linear c (pathEdge d e) h)

private theorem state_coordinate_has_kernel {d : ℕ}
    (c : Checkpoint Pair (Port d)) (j : Port d) (h : LinearState c) :
    ∃ p : Pair, p ≠ 0 ∧ c.state p j = c.state (0 : Pair) j := by
  let L : Pair →ₗ[ℝ] ℝ := {
    toFun := fun p => c.state p j
    map_add' := fun p q => congrFun (h.1 p q) j
    map_smul' := fun r p => congrFun (h.2 r p) j
  }
  have hdim : Module.finrank ℝ ℝ < Module.finrank ℝ Pair := by
    simp [Pair, Module.finrank_prod]
  have hker : LinearMap.ker L ≠ ⊥ := LinearMap.ker_ne_bot_of_finrank_lt hdim
  obtain ⟨p, hp, hpne⟩ := Submodule.exists_mem_ne_zero_of_ne_bot hker
  refine ⟨p, hpne, ?_⟩
  have hz : L p = 0 := LinearMap.mem_ker.mp hp
  have hzero : L (0 : Pair) = 0 := map_zero L
  exact hz.trans hzero.symm

private theorem initial_downstream_eq {d : ℕ} (cut : Fin d)
    (hcut : 1 ≤ cut.val) (p q : Pair) :
    DownstreamEq cut ((initial d).state p) ((initial d).state q) := by
  intro j hj
  have h0 : j.val ≠ 0 := by omega
  have h1 : j.val ≠ 1 := by omega
  simp [initial, initialState, h0, h1]

private theorem initial_record_eq {d : ℕ} (cut : Fin d)
    (hcut : 1 ≤ cut.val) (p q : Pair) :
    (initial d).record p = (initial d).record q := by
  have hd : 2 ≤ d := by have := cut.isLt; omega
  have h0 : d ≠ 0 := by omega
  have h1 : d ≠ 1 := by omega
  simp [initial, initialState, h0, h1]

private theorem crossing_at_least_once {d : ℕ} (cut : Fin d)
    (w : List (Fin d))
    (hcomplete : Complete (Fin.last d) (initial d) (w.map (pathEdge d))) :
    1 ≤ w.count cut := by
  by_contra hcount
  have hzero : w.count cut = 0 := by omega
  have havoid : ∀ edge ∈ w, edge ≠ cut := by
    intro edge he heq
    subst edge
    have hpos := List.count_pos_iff.mpr he
    omega
  let p : Pair := (1, 0)
  have hd : 1 ≤ d := by have := cut.isLt; omega
  have hrec : (initial d).record p = (initial d).record (0 : Pair) := by
    have hd0 : d ≠ 0 := by omega
    simp [initial, initialState, p, hd0]
  have hdown : DownstreamEq cut ((initial d).state p)
      ((initial d).state (0 : Pair)) := by
    intro j hj
    have hj0 : j.val ≠ 0 := by omega
    simp [initial, initialState, p, hj0]
  have heq := (run_preserves_downstream cut (initial d) w p 0 hrec hdown havoid).1
  have hp := hcomplete heq
  norm_num [p] at hp

private theorem average_cross_preserves_downstream {d : ℕ} (cut : Fin d)
    (s t : Port d → ℝ) (h : DownstreamEq cut s t)
    (hu : s cut.castSucc = t cut.castSucc) :
    DownstreamEq cut (pairAverage cut.castSucc cut.succ s)
      (pairAverage cut.castSucc cut.succ t) := by
  intro j hj
  have hjleft : j ≠ cut.castSucc := by
    intro he
    have : j.val = cut.val := congrArg Fin.val he
    omega
  by_cases hjright : j = cut.succ
  · simp [pairAverage, hjright, hu, h cut.succ (by simp)]
  · simp [pairAverage, hjleft, hjright, h j hj]

private theorem run_append {d : ℕ} (c : Checkpoint Pair (Port d))
    (xs ys : List (Port d × Port d)) :
    run (Fin.last d) (xs ++ ys) c =
      run (Fin.last d) ys (run (Fin.last d) xs c) := by
  induction xs generalizing c with
  | nil => rfl
  | cons x rest ih =>
    simpa only [List.cons_append, run] using
      (ih (advance (Fin.last d) c x))

private theorem segment_off_right {d start n : ℕ} (h : start + n ≤ d)
    (c : Checkpoint Pair (Port d)) (p : Pair) (j : Port d)
    (hj : start + n < j.val) :
    (run (Fin.last d) ((segment d start n h).map (pathEdge d)) c).state p j =
      c.state p j := by
  induction n with
  | zero => rfl
  | succ n ih =>
    let e : Fin d := ⟨start + n, by omega⟩
    have hleft : j ≠ e.castSucc := by
      intro he
      have : j.val = start + n := by simpa [e] using congrArg Fin.val he
      omega
    have hright : j ≠ e.succ := by
      intro he
      have : j.val = start + n + 1 := by simpa [e] using congrArg Fin.val he
      omega
    simp only [segment, List.map_append, List.map_singleton, run_append,
      run, advance]
    change (pairAverage e.castSucc e.succ _ ) j = _
    rw [pairAverage_off_seam _ _ _ _ hleft hright]
    exact ih (by omega) (by omega)

private theorem segment_off_left {d start n : ℕ} (h : start + n ≤ d)
    (c : Checkpoint Pair (Port d)) (p : Pair) (j : Port d)
    (hj : j.val < start) :
    (run (Fin.last d) ((segment d start n h).map (pathEdge d)) c).state p j =
      c.state p j := by
  induction n with
  | zero => rfl
  | succ n ih =>
    let e : Fin d := ⟨start + n, by omega⟩
    have hleft : j ≠ e.castSucc := by
      intro he
      have : j.val = start + n := by simpa [e] using congrArg Fin.val he
      omega
    have hright : j ≠ e.succ := by
      intro he
      have : j.val = start + n + 1 := by simpa [e] using congrArg Fin.val he
      omega
    simp only [segment, List.map_append, List.map_singleton, run_append,
      run, advance]
    change (pairAverage e.castSucc e.succ _ ) j = _
    rw [pairAverage_off_seam _ _ _ _ hleft hright]
    exact ih (by omega)

private theorem first_prefix (d k : ℕ) (h : 1 + k ≤ d) :
    ∀ (p : Pair) (j : Port d), 1 ≤ j.val → j.val ≤ 1 + k →
      (run (Fin.last d) ((segment d 1 k h).map (pathEdge d)) (initial d)).state p j =
        if j.val = 1 + k then p.2 / 2 ^ k else p.2 / 2 ^ j.val := by
  induction k with
  | zero =>
    intro p j hj1 hjk
    have hj : j.val = 1 := by omega
    simp [segment, run, initial, initialState, hj]
  | succ k ih =>
    intro p j hj1 hjk
    let e : Fin d := ⟨1 + k, by omega⟩
    let cprev := run (Fin.last d)
      ((segment d 1 k (by omega)).map (pathEdge d)) (initial d)
    have hfar : cprev.state p e.succ = 0 := by
      change (run (Fin.last d)
        ((segment d 1 k (by omega)).map (pathEdge d)) (initial d)).state p e.succ = 0
      rw [segment_off_right (by omega) (initial d) p e.succ (by simp [e])]
      have he0 : e.succ.val ≠ 0 := by simp [e]
      have he1 : e.succ.val ≠ 1 := by simp [e]
      change (if e.succ.val = 0 then p.1 else if e.succ.val = 1 then p.2 else 0) = 0
      simp only [if_neg he0, if_neg he1]
    have htip : cprev.state p e.castSucc = p.2 / 2 ^ k := by
      have hk := ih (by omega) p e.castSucc (by simp [e]) (by simp [e])
      simpa [cprev, e] using hk
    have hstep :
        (run (Fin.last d) ((segment d 1 (k + 1) h).map (pathEdge d))
          (initial d)).state p j =
        pairAverage e.castSucc e.succ (cprev.state p) j := by
      simp only [segment, List.map_append, List.map_singleton, run_append, run, advance]
      rfl
    rw [hstep]
    by_cases hjlow : j.val ≤ k
    · have hjleft : j ≠ e.castSucc := by
        intro he
        have : j.val = 1 + k := by simpa [e] using congrArg Fin.val he
        omega
      have hjright : j ≠ e.succ := by
        intro he
        have : j.val = 1 + k + 1 := by simpa [e] using congrArg Fin.val he
        omega
      rw [pairAverage_off_seam _ _ _ _ hjleft hjright]
      have hk := ih (by omega) p j hj1 (by omega)
      simp [cprev, show j.val ≠ 1 + k by omega,
        show j.val ≠ 1 + (k + 1) by omega] at hk ⊢
      exact hk
    · have hjcases : j = e.castSucc ∨ j = e.succ := by
        have hjv : j.val = 1 + k ∨ j.val = 2 + k := by omega
        rcases hjv with hv | hv
        · exact Or.inl (Fin.ext (by simpa [e] using hv))
        · exact Or.inr (Fin.ext (by simp [e]; omega))
      rcases hjcases with hjEq | hjEq
      · rw [hjEq, pairAverage_left, htip, hfar]
        simp [e, pow_succ] <;> ring_nf <;> simp
      · rw [hjEq, pairAverage_right, htip, hfar]
        simp [e, pow_succ] <;> ring_nf <;> simp

private def firstWave (d : ℕ) (hd : 1 ≤ d) : List (Fin d) :=
  segment d 1 (d - 1) (by omega)

private def secondWave (d : ℕ) : List (Fin d) :=
  segment d 0 d (by omega)

private theorem serialWord_eq_waves (d : ℕ) (hd : 1 ≤ d) :
    serialWord d = firstWave d hd ++ secondWave d := by
  cases d with
  | zero => omega
  | succ n => simp [serialWord, firstWave, secondWave]

private def firstCheckpoint (d : ℕ) (hd : 1 ≤ d) :
    Checkpoint Pair (Port d) :=
  run (Fin.last d) ((firstWave d hd).map (pathEdge d)) (initial d)

private theorem first_state_root (d : ℕ) (hd : 1 ≤ d) (p : Pair) :
    (firstCheckpoint d hd).state p (Fin.last d) = p.2 / 2 ^ (d - 1) := by
  have hk := first_prefix d (d - 1) (by omega) p (Fin.last d)
    (by simp; omega) (by simp; omega)
  simpa [firstCheckpoint, firstWave, Nat.add_sub_of_le hd] using hk

private theorem first_state_interior (d : ℕ) (hd : 1 ≤ d) (p : Pair)
    (j : Port d) (hj1 : 1 ≤ j.val) (hjd : j.val < d) :
    (firstCheckpoint d hd).state p j = p.2 / 2 ^ j.val := by
  have hk := first_prefix d (d - 1) (by omega) p j hj1 (by omega)
  have hne : j.val ≠ 1 + (d - 1) := by omega
  simpa [firstCheckpoint, firstWave, hne] using hk

private theorem first_state_zero (d : ℕ) (hd : 1 ≤ d) (p : Pair) :
    (firstCheckpoint d hd).state p (⟨0, by omega⟩ : Port d) = p.1 := by
  rw [firstCheckpoint, firstWave,
    segment_off_left (by omega) (initial d) p (⟨0, by omega⟩ : Port d) (by simp)]
  simp [initial, initialState]

private theorem second_prefix (d : ℕ) (hd : 1 ≤ d) (k : ℕ) (hk : k < d) :
    ∀ p : Pair,
      (run (Fin.last d) ((segment d 0 k (by omega)).map (pathEdge d))
        (firstCheckpoint d hd)).state p (⟨k, by omega⟩ : Port d) =
        p.1 / 2 ^ k + (k : ℝ) * p.2 / 2 ^ (k + 1) := by
  induction k with
  | zero =>
    intro p
    simpa [segment, run] using first_state_zero d hd p
  | succ k ih =>
    intro p
    let e : Fin d := ⟨k, by omega⟩
    let cprev := run (Fin.last d)
      ((segment d 0 k (by omega)).map (pathEdge d)) (firstCheckpoint d hd)
    have hfront : cprev.state p e.castSucc =
        p.1 / 2 ^ k + (k : ℝ) * p.2 / 2 ^ (k + 1) := by
      simpa [cprev, e] using ih (by omega) p
    have hnext : cprev.state p e.succ = p.2 / 2 ^ (k + 1) := by
      change (run (Fin.last d)
        ((segment d 0 k (by omega)).map (pathEdge d))
          (firstCheckpoint d hd)).state p e.succ = _
      rw [segment_off_right (by omega) (firstCheckpoint d hd) p e.succ (by simp [e])]
      exact first_state_interior d hd p e.succ (by simp [e]) (by simp [e]; omega)
    have hstep :
        (run (Fin.last d) ((segment d 0 (k + 1) (by omega)).map (pathEdge d))
          (firstCheckpoint d hd)).state p (⟨k + 1, by omega⟩ : Port d) =
        pairAverage e.castSucc e.succ (cprev.state p) e.succ := by
      simp only [segment, List.map_append, List.map_singleton, run_append, run, advance]
      simp [e, cprev, pathEdge]
    rw [hstep, pairAverage_right, hfront, hnext]
    simp [pow_succ, Nat.cast_add]
    ring

private theorem final_state (n : ℕ) (p : Pair) :
    (run (Fin.last (n + 1))
      ((secondWave (n + 1)).map (pathEdge (n + 1)))
      (firstCheckpoint (n + 1) (by omega))).state p (Fin.last (n + 1)) =
      OPH.SourceCheckpointPipeline.finalSample n p.1 p.2 := by
  let e : Fin (n + 1) := ⟨n, by omega⟩
  let cprev := run (Fin.last (n + 1))
    ((segment (n + 1) 0 n (by omega)).map (pathEdge (n + 1)))
    (firstCheckpoint (n + 1) (by omega))
  have heRoot : e.succ = Fin.last (n + 1) := Fin.ext (by simp [e])
  have hfront : cprev.state p e.castSucc =
      p.1 / 2 ^ n + (n : ℝ) * p.2 / 2 ^ (n + 1) := by
    simpa [cprev, e] using second_prefix (n + 1) (by omega) n (by omega) p
  have hroot : cprev.state p e.succ = p.2 / 2 ^ n := by
    change (run (Fin.last (n + 1))
      ((segment (n + 1) 0 n (by omega)).map (pathEdge (n + 1)))
      (firstCheckpoint (n + 1) (by omega))).state p e.succ = _
    rw [segment_off_right (by omega)
      (firstCheckpoint (n + 1) (by omega)) p e.succ (by simp [e])]
    rw [heRoot]
    exact first_state_root (n + 1) (by omega) p
  have hstep :
      (run (Fin.last (n + 1))
        ((secondWave (n + 1)).map (pathEdge (n + 1)))
        (firstCheckpoint (n + 1) (by omega))).state p (Fin.last (n + 1)) =
      pairAverage e.castSucc e.succ (cprev.state p) e.succ := by
    simp only [secondWave, segment, List.map_append, List.map_singleton,
      run_append, run, advance]
    simp [e, cprev, pathEdge, heRoot]
  rw [hstep, pairAverage_right, hfront, hroot]
  unfold OPH.SourceCheckpointPipeline.finalSample
  simp [pow_succ, Nat.cast_add]
  ring

private theorem run_head {d : ℕ} (c : Checkpoint Pair (Port d))
    (es : List (Port d × Port d)) (p : Pair)
    (hhead : (c.record p).head? = some (c.state p (Fin.last d))) :
    ((run (Fin.last d) es c).record p).head? =
      some ((run (Fin.last d) es c).state p (Fin.last d)) := by
  induction es generalizing c with
  | nil => exact hhead
  | cons e rest ih =>
    simpa only [run] using ih (advance (Fin.last d) c e) (by simp [advance])

private theorem first_head (n : ℕ) (p : Pair) :
    ((firstCheckpoint (n + 1) (by omega)).record p).head? =
      some (OPH.SourceCheckpointPipeline.firstSample n p.2) := by
  have hh := run_head (initial (n + 1))
    ((firstWave (n + 1) (by omega)).map (pathEdge (n + 1))) p
    (by simp [initial])
  change ((firstCheckpoint (n + 1) (by omega)).record p).head? =
    some ((firstCheckpoint (n + 1) (by omega)).state p (Fin.last (n + 1))) at hh
  rw [first_state_root] at hh
  simpa [OPH.SourceCheckpointPipeline.firstSample] using hh

private theorem final_head (n : ℕ) (p : Pair) :
    ((run (Fin.last (n + 1))
      ((serialWord (n + 1)).map (pathEdge (n + 1)))
      (initial (n + 1))).record p).head? =
      some (OPH.SourceCheckpointPipeline.finalSample n p.1 p.2) := by
  have hstatehead : ((firstCheckpoint (n + 1) (by omega)).record p).head? =
      some ((firstCheckpoint (n + 1) (by omega)).state p (Fin.last (n + 1))) := by
    rw [first_state_root]
    simpa [OPH.SourceCheckpointPipeline.firstSample] using first_head n p
  have hh := run_head (firstCheckpoint (n + 1) (by omega))
    ((secondWave (n + 1)).map (pathEdge (n + 1))) p hstatehead
  rw [final_state] at hh
  rw [serialWord_eq_waves (n + 1) (by omega), List.map_append, run_append]
  exact hh

/-- The serial two-wave path word reaches a complete exact retained record.
The two receiver samples are decoded by `recover_second` and `recover_first`. -/
theorem serialWord_complete (d : ℕ) (hd : 1 ≤ d) :
    Complete (Fin.last d) (initial d) ((serialWord d).map (pathEdge d)) := by
  cases d with
  | zero => omega
  | succ n =>
    intro p q hrecord
    have hpre : (firstCheckpoint (n + 1) (by omega)).record p =
        (firstCheckpoint (n + 1) (by omega)).record q := by
      apply run_record_extends (Fin.last (n + 1))
        ((secondWave (n + 1)).map (pathEdge (n + 1)))
        (firstCheckpoint (n + 1) (by omega)) p q
      rw [serialWord_eq_waves (n + 1) (by omega), List.map_append, run_append] at hrecord
      exact hrecord
    have hysome : some (OPH.SourceCheckpointPipeline.firstSample n p.2) =
        some (OPH.SourceCheckpointPipeline.firstSample n q.2) := by
      calc
        _ = ((firstCheckpoint (n + 1) (by omega)).record p).head? :=
          (first_head n p).symm
        _ = ((firstCheckpoint (n + 1) (by omega)).record q).head? :=
          congrArg List.head? hpre
        _ = _ := first_head n q
    have hySample := Option.some.inj hysome
    have hy : p.2 = q.2 := by
      calc
        p.2 = 2 ^ n * OPH.SourceCheckpointPipeline.firstSample n p.2 :=
          (OPH.SourceCheckpointPipeline.recover_second n p.2).symm
        _ = 2 ^ n * OPH.SourceCheckpointPipeline.firstSample n q.2 := by rw [hySample]
        _ = q.2 := OPH.SourceCheckpointPipeline.recover_second n q.2
    have hxsome : some (OPH.SourceCheckpointPipeline.finalSample n p.1 p.2) =
        some (OPH.SourceCheckpointPipeline.finalSample n q.1 q.2) := by
      calc
        _ = ((run (Fin.last (n + 1))
          ((serialWord (n + 1)).map (pathEdge (n + 1)))
          (initial (n + 1))).record p).head? := (final_head n p).symm
        _ = ((run (Fin.last (n + 1))
          ((serialWord (n + 1)).map (pathEdge (n + 1)))
          (initial (n + 1))).record q).head? := congrArg List.head? hrecord
        _ = _ := final_head n q
    have hxSample := Option.some.inj hxsome
    have hx : p.1 = q.1 := by
      calc
        p.1 = 2 ^ (n + 1) * OPH.SourceCheckpointPipeline.finalSample n p.1 p.2 -
            ((n + 2 : ℝ) * 2 ^ n / 2) *
              OPH.SourceCheckpointPipeline.firstSample n p.2 :=
          (OPH.SourceCheckpointPipeline.recover_first n p.1 p.2).symm
        _ = 2 ^ (n + 1) * OPH.SourceCheckpointPipeline.finalSample n q.1 q.2 -
            ((n + 2 : ℝ) * 2 ^ n / 2) *
              OPH.SourceCheckpointPipeline.firstSample n q.2 := by rw [hxSample, hy]
        _ = q.1 := OPH.SourceCheckpointPipeline.recover_first n q.1 q.2
    exact Prod.ext hx hy

private theorem crossing_at_least_twice {d : ℕ} (cut : Fin d)
    (hcut : 1 ≤ cut.val) (w : List (Fin d))
    (hcomplete : Complete (Fin.last d) (initial d) (w.map (pathEdge d))) :
    2 ≤ w.count cut := by
  have hone := crossing_at_least_once cut w hcomplete
  by_contra htwo
  have hcount : w.count cut = 1 := by omega
  obtain ⟨pre, post, hw⟩ := List.append_of_mem
    (List.count_pos_iff.mp (by omega : 0 < w.count cut))
  subst w
  have hcounts : pre.count cut = 0 ∧ post.count cut = 0 := by
    simp only [List.count_append, List.count_cons_self] at hcount
    omega
  obtain ⟨hprezero, hpostzero⟩ := hcounts
  have havpre : ∀ e ∈ pre, e ≠ cut := by
    intro e he heq
    subst e
    have := List.count_pos_iff.mpr he
    omega
  have havpost : ∀ e ∈ post, e ≠ cut := by
    intro e he heq
    subst e
    have := List.count_pos_iff.mpr he
    omega
  let cpre := run (Fin.last d) (pre.map (pathEdge d)) (initial d)
  have hlinear : LinearState cpre := run_linear (initial d) pre (initial_linear d)
  obtain ⟨p, hpne, hup⟩ := state_coordinate_has_kernel cpre cut.castSucc hlinear
  have hpre := run_preserves_downstream cut (initial d) pre p 0
    (initial_record_eq cut hcut p 0)
    (initial_downstream_eq cut hcut p 0) havpre
  have hafterdown : DownstreamEq cut
      ((advance (Fin.last d) cpre (pathEdge d cut)).state p)
      ((advance (Fin.last d) cpre (pathEdge d cut)).state (0 : Pair)) :=
    average_cross_preserves_downstream cut (cpre.state p) (cpre.state 0) hpre.2 hup
  have hroot : cut.val < (Fin.last d).val := by simpa using cut.isLt
  have hafterrec : (advance (Fin.last d) cpre (pathEdge d cut)).record p =
      (advance (Fin.last d) cpre (pathEdge d cut)).record (0 : Pair) := by
    exact congrArg₂ List.cons (hafterdown (Fin.last d) hroot) hpre.1
  have hsuf := (run_preserves_downstream cut
    (advance (Fin.last d) cpre (pathEdge d cut)) post p 0
    hafterrec hafterdown havpost).1
  have hword : (pre ++ cut :: post).map (pathEdge d) =
      pre.map (pathEdge d) ++ pathEdge d cut :: post.map (pathEdge d) := by simp
  have hrecord : (run (Fin.last d)
      ((pre ++ cut :: post).map (pathEdge d)) (initial d)).record p =
      (run (Fin.last d)
      ((pre ++ cut :: post).map (pathEdge d)) (initial d)).record (0 : Pair) := by
    simpa only [hword, run_append, run] using hsuf
  exact hpne (hcomplete hrecord)

/-- A completing exact-real path word crosses the first cut once and every
later cut at least twice. Its alphabet contains only the declared path edges;
the initial receiver sample is retained. -/
theorem crossing_count (d : ℕ) (hd : 1 ≤ d) (w : List (Fin d))
    (hcomplete : Complete (Fin.last d) (initial d) (w.map (pathEdge d))) :
    1 ≤ w.count ⟨0, hd⟩ ∧
      ∀ i : Fin d, 1 ≤ i.val → 2 ≤ w.count i := by
  exact ⟨crossing_at_least_once ⟨0, hd⟩ w hcomplete,
    fun i hi => crossing_at_least_twice i hi w hcomplete⟩

private theorem sum_counts_eq_length {d : ℕ} (w : List (Fin d)) :
    (∑ i : Fin d, w.count i) = w.length := by
  induction w with
  | nil => simp
  | cons a rest ih =>
    calc
      (∑ i : Fin d, (a :: rest).count i) =
          ∑ i : Fin d, ((if a = i then 1 else 0) + rest.count i) := by
            apply Finset.sum_congr rfl
            intro i _
            by_cases h : a = i <;> simp [h, Nat.add_comm]
      _ = 1 + ∑ i : Fin d, rest.count i := by
          rw [Finset.sum_add_distrib]
          simp
      _ = (a :: rest).length := by simp [ih, Nat.add_comm]

/-- Exact retained samples on the isolated path require at least `2d - 1`
means for two independent source deviations. -/
theorem complete_length_ge (d : ℕ) (hd : 1 ≤ d) (w : List (Fin d))
    (hcomplete : Complete (Fin.last d) (initial d) (w.map (pathEdge d))) :
    2 * d - 1 ≤ w.length := by
  have hcuts := crossing_count d hd w hcomplete
  have hsum : (∑ i : Fin d, (if i.val = 0 then 1 else 2)) ≤
      ∑ i : Fin d, w.count i := by
    apply Finset.sum_le_sum
    intro i _
    by_cases hi : i.val = 0
    · have hieq : i = ⟨0, hd⟩ := Fin.ext hi
      simpa [hi, hieq] using hcuts.1
    · have hipos : 1 ≤ i.val := by omega
      simpa [hi] using hcuts.2 i hipos
  rw [sum_counts_eq_length] at hsum
  cases d with
  | zero => omega
  | succ n =>
    have hclosed : (∑ i : Fin (n + 1), (if i.val = 0 then 1 else 2)) =
        1 + 2 * n := by
      rw [Fin.sum_univ_succ]
      simp
      omega
    rw [hclosed] at hsum
    omega

/-- A two-edge route with a nonpath chord from port zero to port two. -/
def chordWord : List (Port 2 × Port 2) :=
  [(⟨0, by omega⟩, ⟨2, by omega⟩),
   (⟨1, by omega⟩, ⟨2, by omega⟩)]

private theorem chord_record (p : Pair) :
    (run (Fin.last 2) chordWord (initial 2)).record p =
      [p.1 / 4 + p.2 / 2, p.1 / 2, 0] := by
  simp [chordWord, run, advance, initial, initialState, pairAverage] <;> ring

/-- Admitting the chord `(0,2)` permits two means to recover both deviations
at depth two, violating the path-only `2d - 1` lower bound. -/
theorem chord_countermodel :
    Complete (Fin.last 2) (initial 2) chordWord ∧
      chordWord.length < 2 * 2 - 1 := by
  constructor
  · intro p q h
    rw [chord_record p, chord_record q] at h
    have hlast : p.1 / 2 = q.1 / 2 := by
      exact (List.cons.inj (List.cons.inj h).2).1
    have hfirst : p.1 / 4 + p.2 / 2 = q.1 / 4 + q.2 / 2 :=
      (List.cons.inj h).1
    apply Prod.ext <;> dsimp <;> linarith
  · norm_num [chordWord]

/-- The same path with one unknown deviation at port zero. -/
def initialOne : Checkpoint ℝ (Port 2) where
  state x i := if i.val = 0 then x else 0
  record _ := [0]

/-- The one-unknown path needs only one mean per edge. -/
def oneWord : List (Fin 2) := [⟨0, by omega⟩, ⟨1, by omega⟩]

private theorem one_record (x : ℝ) :
    (run (Fin.last 2) (oneWord.map (pathEdge 2)) initialOne).record x =
      [x / 4, 0, 0] := by
  simp [oneWord, pathEdge, run, advance, initialOne, pairAverage] <;> ring

/-- Removing the second independent unknown makes the sharp two-record
length claim false at depth two. -/
theorem one_unknown_countermodel :
    Complete (Fin.last 2) initialOne (oneWord.map (pathEdge 2)) ∧
      oneWord.length < 2 * 2 - 1 := by
  constructor
  · intro x y h
    rw [one_record x, one_record y] at h
    have hx : x / 4 = y / 4 := (List.cons.inj h).1
    linarith
  · norm_num [oneWord]

#print axioms crossing_count
#print axioms complete_length_ge
#print axioms serialWord_length
#print axioms serialWord_complete
#print axioms chord_countermodel
#print axioms one_unknown_countermodel

end
end OPH.SourceCheckpointPathBound
