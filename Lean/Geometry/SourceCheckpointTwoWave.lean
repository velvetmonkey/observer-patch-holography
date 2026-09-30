import Geometry.SourceCheckpointPathBound
import Mathlib.Combinatorics.Enumerative.DyckWord

/-!
# Two-wave controls for the isolated path

The event dependencies below transcribe `pipeline_extensions` in
`code/source_checkpoint_selection/verify.py:176-192`: first-wave edges run in
increasing order, second-wave edges run in increasing order, and first-wave
edge `i + 1` precedes second-wave edge `i`.
-/

set_option autoImplicit false

namespace OPH.SourceCheckpointTwoWave
noncomputable section
open OPH.SourceCheckpointPathBound
open OPH.SourceTemporalGuard
open ObserverPatchHolography.ScalarSeamRepair

/-- The first occurrence of edge `i` (`i > 0`) or the later occurrence of edge
`i`; edge zero has only a second-wave event. -/
inductive Event (d : ℕ) where
  | first (i : Fin d) (hi : 1 ≤ i.val)
  | second (i : Fin d)
  deriving DecidableEq

/-- The edge performed by an event. -/
def Event.edge {d : ℕ} : Event d → Fin d
  | .first i _ => i
  | .second i => i

/-- Direct precedence constraints of the Python `pipeline_extensions` poset,
`code/source_checkpoint_selection/verify.py:176-192`. -/
def Before {d : ℕ} : Event d → Event d → Prop
  | .first i _, .first j _ => i.val + 1 = j.val
  | .second i, .second j => i.val + 1 = j.val
  | .first i _, .second j => i.val = j.val + 1
  | .second _, .first _ _ => False

private theorem total_counts {d : ℕ} (w : List (Fin d)) :
    (∑ i : Fin d, w.count i) = w.length := by
  induction w with
  | nil => simp
  | cons a w ih =>
    simp only [List.count_cons, beq_iff_eq]
    simp only [Finset.sum_add_distrib, ih]
    simp

/-- At the sharp horizon, all cut-capacity lower bounds are attained.
The positive-depth hypothesis is the one in `complete_length_ge`. -/
theorem shortest_counts (d : ℕ) (hd : 1 ≤ d) (w : List (Fin d))
    (hlen : w.length = 2 * d - 1)
    (hc : Complete (Fin.last d) (initial d) (w.map (pathEdge d))) :
    ∀ i : Fin d, w.count i = if i.val = 0 then 1 else 2 := by
  have hcuts := crossing_count d hd w hc
  have hle : ∀ i : Fin d, (if i.val = 0 then 1 else 2) ≤ w.count i := by
    intro i
    by_cases hi : i.val = 0
    · have he : i = ⟨0, hd⟩ := Fin.ext hi
      simpa [hi, he] using hcuts.1
    · simpa [hi] using hcuts.2 i (by omega)
  have hsum : (∑ i : Fin d, (if i.val = 0 then 1 else 2)) = 2 * d - 1 := by
    cases d with
    | zero => omega
    | succ n =>
      rw [Fin.sum_univ_succ]
      simp
      omega
  have heq : (∑ i : Fin d, (if i.val = 0 then 1 else 2)) =
      ∑ i : Fin d, w.count i := by rw [total_counts, hlen, hsum]
  have hall := (Finset.sum_eq_sum_iff_of_le (fun i _ => hle i)).mp heq
  exact fun i => (hall i (Finset.mem_univ i)).symm

private theorem run_hasRoot {d : ℕ} (w : List (Fin d))
    (c : Checkpoint Pair (Port d)) (h : HasRoot (Fin.last d) c) :
    HasRoot (Fin.last d) (run (Fin.last d) (w.map (pathEdge d)) c) := by
  induction w generalizing c with
  | nil => exact h
  | cons e w ih => exact ih _ (advance_has_root _ _ _)

private theorem run_append_path {d : ℕ} (u v : List (Fin d))
    (c : Checkpoint Pair (Port d)) :
    run (Fin.last d) ((u ++ v).map (pathEdge d)) c =
      run (Fin.last d) (v.map (pathEdge d))
        (run (Fin.last d) (u.map (pathEdge d)) c) := by
  induction u generalizing c with
  | nil => rfl
  | cons e u ih => simpa only [List.cons_append, List.map_cons, run] using ih _

private theorem run_record_congr {d : ℕ} (u : List (Fin d))
    (c c' : Checkpoint Pair (Port d))
    (hs : c.state = c'.state)
    (hr : ∀ p q, c.record p = c.record q ↔ c'.record p = c'.record q) :
    ∀ p q, (run (Fin.last d) (u.map (pathEdge d)) c).record p =
      (run (Fin.last d) (u.map (pathEdge d)) c).record q ↔
      (run (Fin.last d) (u.map (pathEdge d)) c').record p =
      (run (Fin.last d) (u.map (pathEdge d)) c').record q := by
  induction u generalizing c c' with
  | nil => exact hr
  | cons e u ih =>
    apply ih
    · simp only [advance, hs]
    · intro p q
      simp only [advance, List.cons.injEq, hs, hr]

/-- A shortest completing word cannot contain a mean that leaves every
source-dependent scalar state unchanged at that point. The retained receiver
sample is included when removing such a step. -/
theorem shortest_no_idle (d : ℕ) (hd : 1 ≤ d)
    (pre post : List (Fin d)) (e : Fin d)
    (hlen : (pre ++ e :: post).length = 2 * d - 1)
    (hc : Complete (Fin.last d) (initial d)
      ((pre ++ e :: post).map (pathEdge d))) :
    ¬ (∀ p : Pair,
      pairAverage e.castSucc e.succ
        ((run (Fin.last d) (pre.map (pathEdge d)) (initial d)).state p) =
        (run (Fin.last d) (pre.map (pathEdge d)) (initial d)).state p) := by
  intro hidle
  let c := run (Fin.last d) (pre.map (pathEdge d)) (initial d)
  have hroot : HasRoot (Fin.last d) c :=
    run_hasRoot pre (initial d) (by intro p q h; exact List.cons.inj h |>.1)
  have hs : (advance (Fin.last d) c (pathEdge d e)).state = c.state := by
    funext p
    exact hidle p
  have hr : ∀ p q,
      (advance (Fin.last d) c (pathEdge d e)).record p =
        (advance (Fin.last d) c (pathEdge d e)).record q ↔
      c.record p = c.record q := by
    intro p q
    change _ :: c.record p = _ :: c.record q ↔ _
    rw [List.cons.injEq]
    constructor
    · exact And.right
    · intro h
      refine ⟨?_, h⟩
      change (advance (Fin.last d) c (pathEdge d e)).state p (Fin.last d) =
        (advance (Fin.last d) c (pathEdge d e)).state q (Fin.last d)
      rw [hs]
      exact hroot p q h
  have hshort : Complete (Fin.last d) (initial d)
      ((pre ++ post).map (pathEdge d)) := by
    intro p q h
    apply hc
    rw [run_append_path] at h ⊢
    exact (run_record_congr post _ _ hs hr p q).mpr h
  have hbound := complete_length_ge d hd (pre ++ post) hshort
  simp only [List.length_append, List.length_cons] at hlen hbound
  omega

/-- For depth at least two, a completing word cannot start by mixing the
source pair before any source information has reached the next port. -/
theorem complete_not_first_zero (d : ℕ) (hd : 2 ≤ d) (w : List (Fin d)) :
    ¬ Complete (Fin.last d) (initial d)
      ((⟨0, by omega⟩ :: w).map (pathEdge d)) := by
  intro hc
  have hp := complete_first_protected (Fin.last d) (initial d)
    (pathEdge d ⟨0, by omega⟩) (w.map (pathEdge d)) hc
  have hs : (advance (Fin.last d) (initial d) (pathEdge d ⟨0, by omega⟩)).state
      ((1, 0) : Pair) =
      (advance (Fin.last d) (initial d) (pathEdge d ⟨0, by omega⟩)).state
      ((0, 1) : Pair) := by
    funext j
    let z : Port d := ⟨0, by omega⟩
    let o : Port d := ⟨1, by omega⟩
    change (if j = z ∨ j = o then ((1 : ℝ) + 0) / 2 else initialState d (1, 0) j) =
      (if j = z ∨ j = o then ((0 : ℝ) + 1) / 2 else initialState d (0, 1) j)
    by_cases hj : j = z ∨ j = o
    · simp only [if_pos hj]; norm_num
    · have h0 : j.val ≠ 0 := by intro h; exact hj (Or.inl (Fin.ext h))
      have h1 : j.val ≠ 1 := by intro h; exact hj (Or.inr (Fin.ext h))
      simp only [if_neg hj, initialState, h0, h1, if_false]
  have hr : (advance (Fin.last d) (initial d) (pathEdge d ⟨0, by omega⟩)).record
      ((1, 0) : Pair) =
      (advance (Fin.last d) (initial d) (pathEdge d ⟨0, by omega⟩)).record
      ((0, 1) : Pair) := by
    apply congrArg₂ List.cons (congrFun hs (Fin.last d))
    simp [initial, initialState, show d ≠ 0 by omega, show d ≠ 1 by omega]
  have he := hp (1, 0) (0, 1) hr hs
  norm_num at he

/-- At positive nontrivial depth, every shortest completing word starts with
edge one. Edges farther to the right would be idle; edge zero erases the two
independent source deviations. -/
theorem shortest_first (d : ℕ) (hd : 2 ≤ d) (e : Fin d) (w : List (Fin d))
    (hlen : (e :: w).length = 2 * d - 1)
    (hc : Complete (Fin.last d) (initial d) ((e :: w).map (pathEdge d))) :
    e.val = 1 := by
  by_cases hzero : e.val = 0
  · have he : e = ⟨0, by omega⟩ := Fin.ext hzero
    rw [he] at hc
    exact False.elim (complete_not_first_zero d hd w hc)
  by_contra hone
  have he : 2 ≤ e.val := by omega
  apply shortest_no_idle d (by omega) [] w e hlen hc
  intro p
  funext j
  have hleft : (initial d).state p e.castSucc = 0 := by
    simp [initial, initialState, show e.val ≠ 0 by omega, show e.val ≠ 1 by omega]
  have hright : (initial d).state p e.succ = 0 := by
    simp [initial, initialState, show e.val ≠ 0 by omega]
  change pairAverage e.castSucc e.succ ((initial d).state p) j = (initial d).state p j
  by_cases h : j = e.castSucc ∨ j = e.succ
  · rcases h with rfl | rfl <;> simp [pairAverage, hleft, hright]
  · simp [pairAverage, h]

private theorem avoid_cut_zero {d : ℕ} (cut : Fin d) (w : List (Fin d))
    (c : Checkpoint Pair (Port d))
    (hz : ∀ p (j : Port d), cut.val < j.val → c.state p j = 0)
    (ha : ∀ e ∈ w, e ≠ cut) :
    ∀ p (j : Port d), cut.val < j.val →
      (run (Fin.last d) (w.map (pathEdge d)) c).state p j = 0 := by
  induction w generalizing c with
  | nil => exact hz
  | cons e w ih =>
    apply ih
    · intro p j hj
      have hne : e.val ≠ cut.val := by
        intro h
        exact ha e (by simp) (Fin.ext h)
      by_cases he : e.val < cut.val
      · have hl : j ≠ e.castSucc := by intro h; have := congrArg Fin.val h; simp at this; omega
        have hr : j ≠ e.succ := by intro h; have := congrArg Fin.val h; simp at this; omega
        simpa [advance, pathEdge, pairAverage, hl, hr] using hz p j hj
      · have hgt : cut.val < e.val := by omega
        have hl := hz p e.castSucc (by simpa using hgt)
        have hr := hz p e.succ (by simp; omega)
        simp [advance, pathEdge, pairAverage, hl, hr, hz p j hj]
    · intro a h
      exact ha a (by simp [h])

/-- Before the first use of a noninitial edge, its predecessor must
have been used. Otherwise that first mean acts on two calibrated zeros. -/
theorem shortest_first_precedence (d : ℕ) (hd : 1 ≤ d)
    (cut e : Fin d) (hcut : 1 ≤ cut.val) (he : e.val = cut.val + 1)
    (pre post : List (Fin d))
    (hlen : (pre ++ e :: post).length = 2 * d - 1)
    (hc : Complete (Fin.last d) (initial d)
      ((pre ++ e :: post).map (pathEdge d))) : cut ∈ pre := by
  by_contra hmem
  have hz := avoid_cut_zero cut pre (initial d)
    (by
      intro p j hj
      simp [initial, initialState, show j.val ≠ 0 by omega, show j.val ≠ 1 by omega])
    (by intro a ha heq; subst a; exact hmem ha)
  apply shortest_no_idle d hd pre post e hlen hc
  intro p
  funext j
  have hl := hz p e.castSucc (by simp; omega)
  have hr := hz p e.succ (by simp; omega)
  by_cases hj : j = e.castSucc ∨ j = e.succ
  · rcases hj with rfl | rfl <;> simp [pairAverage, hl, hr]
  · simp [pairAverage, hj]

private def RightEq {d : ℕ} (cut : Fin d) (s t : Port d → ℝ) : Prop :=
  ∀ j, cut.val < j.val → s j = t j

private theorem mean_rightEq {d : ℕ} (cut e : Fin d) (he : e ≠ cut)
    (s t : Port d → ℝ) (h : RightEq cut s t) :
    RightEq cut (pairAverage e.castSucc e.succ s) (pairAverage e.castSucc e.succ t) := by
  intro j hj
  by_cases hlt : e.val < cut.val
  · have hl : j ≠ e.castSucc := by intro h; have := congrArg Fin.val h; simp at this; omega
    have hr : j ≠ e.succ := by intro h; have := congrArg Fin.val h; simp at this; omega
    simp [pairAverage, hl, hr, h j hj]
  · have hgt : cut.val < e.val := by
      have hne : e.val ≠ cut.val := by intro h; exact he (Fin.ext h)
      omega
    have hl := h e.castSucc (by simpa using hgt)
    have hr := h e.succ (by simp; omega)
    simp [pairAverage, hl, hr, h j hj]

private theorem run_rightEq {d : ℕ} (cut : Fin d) (w : List (Fin d))
    (c : Checkpoint Pair (Port d)) (p q : Pair)
    (hr : c.record p = c.record q) (hs : RightEq cut (c.state p) (c.state q))
    (ha : ∀ e ∈ w, e ≠ cut) :
    (run (Fin.last d) (w.map (pathEdge d)) c).record p =
      (run (Fin.last d) (w.map (pathEdge d)) c).record q := by
  induction w generalizing c with
  | nil => exact hr
  | cons e w ih =>
    have hs' := mean_rightEq cut e (ha e (by simp)) _ _ hs
    apply ih
    · exact congrArg₂ List.cons (hs' (Fin.last d) (by simpa using cut.isLt)) hr
    · exact hs'
    · intro a h
      exact ha a (by simp [h])

private theorem run_record_congr_right {d : ℕ} (cut : Fin d) (w : List (Fin d))
    (c c' : Checkpoint Pair (Port d))
    (hs : ∀ p, RightEq cut (c.state p) (c'.state p))
    (hr : ∀ p q, c.record p = c.record q ↔ c'.record p = c'.record q)
    (ha : ∀ e ∈ w, e ≠ cut) :
    ∀ p q, (run (Fin.last d) (w.map (pathEdge d)) c).record p =
      (run (Fin.last d) (w.map (pathEdge d)) c).record q ↔
      (run (Fin.last d) (w.map (pathEdge d)) c').record p =
      (run (Fin.last d) (w.map (pathEdge d)) c').record q := by
  induction w generalizing c c' with
  | nil => exact hr
  | cons e w ih =>
    have hs' := fun p => mean_rightEq cut e (ha e (by simp)) _ _ (hs p)
    apply ih
    · exact hs'
    · intro p q
      change _ :: c.record p = _ :: c.record q ↔ _ :: c'.record p = _ :: c'.record q
      rw [List.cons.injEq, List.cons.injEq, hr]
      simp only [pathEdge]
      rw [hs' p (Fin.last d) (by simpa using cut.isLt),
        hs' q (Fin.last d) (by simpa using cut.isLt)]
    · intro a h
      exact ha a (by simp [h])

/-- Every use of a nonfinal edge in a shortest completing word is followed
by a use of the next edge. In particular, last occurrences are increasing.
Deleting an edge with no future downstream crossing leaves the retained
observations equally informative and would contradict the sharp bound. -/
theorem shortest_second_precedence (d : ℕ) (hd : 1 ≤ d)
    (e next : Fin d) (hne : next.val = e.val + 1)
    (pre post : List (Fin d))
    (hlen : (pre ++ e :: post).length = 2 * d - 1)
    (hc : Complete (Fin.last d) (initial d)
      ((pre ++ e :: post).map (pathEdge d))) : next ∈ post := by
  by_contra hmem
  let c := run (Fin.last d) (pre.map (pathEdge d)) (initial d)
  have hroot : HasRoot (Fin.last d) c :=
    run_hasRoot pre (initial d) (by intro p q h; exact List.cons.inj h |>.1)
  have hs : ∀ p, RightEq next
      ((advance (Fin.last d) c (pathEdge d e)).state p) (c.state p) := by
    intro p j hj
    have hl : j ≠ e.castSucc := by intro h; have := congrArg Fin.val h; simp at this; omega
    have hr : j ≠ e.succ := by intro h; have := congrArg Fin.val h; simp at this; omega
    simp [advance, pathEdge, pairAverage, hl, hr]
  have hr : ∀ p q,
      (advance (Fin.last d) c (pathEdge d e)).record p =
        (advance (Fin.last d) c (pathEdge d e)).record q ↔ c.record p = c.record q := by
    intro p q
    change _ :: c.record p = _ :: c.record q ↔ _
    rw [List.cons.injEq]
    constructor
    · exact And.right
    · intro h
      refine ⟨?_, h⟩
      change (advance (Fin.last d) c (pathEdge d e)).state p (Fin.last d) =
        (advance (Fin.last d) c (pathEdge d e)).state q (Fin.last d)
      rw [hs p _ (by simpa using next.isLt), hs q _ (by simpa using next.isLt)]
      exact hroot p q h
  have hshort : Complete (Fin.last d) (initial d) ((pre ++ post).map (pathEdge d)) := by
    intro p q h
    apply hc
    rw [run_append_path] at h ⊢
    exact (run_record_congr_right next post _ _ hs hr
      (by intro a ha he; subst a; exact hmem ha) p q).mpr h
  have hb := complete_length_ge d hd (pre ++ post) hshort
  simp only [List.length_append, List.length_cons] at hlen hb
  omega

private theorem run_linear_form {d : ℕ} (w : List (Fin d)) :
    ∀ (p : Pair) (j : Port d),
      (run (Fin.last d) (w.map (pathEdge d)) (initial d)).state p j =
        p.1 * (run (Fin.last d) (w.map (pathEdge d)) (initial d)).state (1, 0) j +
        p.2 * (run (Fin.last d) (w.map (pathEdge d)) (initial d)).state (0, 1) j := by
  have hgen : ∀ (u : List (Fin d)) (c : Checkpoint Pair (Port d)),
      (∀ (p : Pair) (j : Port d), c.state p j = p.1 * c.state (1, 0) j + p.2 * c.state (0, 1) j) →
      ∀ (p : Pair) (j : Port d),
        (run (Fin.last d) (u.map (pathEdge d)) c).state p j =
          p.1 * (run (Fin.last d) (u.map (pathEdge d)) c).state (1, 0) j +
          p.2 * (run (Fin.last d) (u.map (pathEdge d)) c).state (0, 1) j := by
    intro u
    induction u with
    | nil => intro c h; exact h
    | cons e u ih =>
      intro c h
      apply ih
      intro p j
      change pairAverage e.castSucc e.succ (c.state p) j = _
      by_cases hj : j = e.castSucc ∨ j = e.succ
      · simp [advance, pathEdge, pairAverage, hj, h p e.castSucc, h p e.succ]
        ring
      · simpa [advance, pathEdge, pairAverage, hj] using h p j
  apply hgen w (initial d)
  intro p j
  by_cases h0 : j.val = 0 <;> by_cases h1 : j.val = 1 <;>
    simp [initial, initialState, h0, h1]

private theorem coordinate_kernel {d : ℕ} (w : List (Fin d)) (j : Port d) :
    ∃ p : Pair, p ≠ 0 ∧
      (run (Fin.last d) (w.map (pathEdge d)) (initial d)).state p j =
        (run (Fin.last d) (w.map (pathEdge d)) (initial d)).state 0 j := by
  let c := run (Fin.last d) (w.map (pathEdge d)) (initial d)
  let a := c.state (1, 0) j
  let b := c.state (0, 1) j
  by_cases hz : a = 0 ∧ b = 0
  · refine ⟨(1, 0), by norm_num, ?_⟩
    rw [run_linear_form w (1, 0) j, run_linear_form w 0 j]
    change 1 * a + 0 * b = 0 * a + 0 * b
    simp [hz.1]
  · refine ⟨(-b, a), ?_, ?_⟩
    · intro he
      apply hz
      have h1 := congrArg Prod.fst he
      have h2 := congrArg Prod.snd he
      simp only [Prod.fst_zero, Prod.snd_zero] at h1 h2
      exact ⟨h2, neg_eq_zero.mp h1⟩
    · rw [run_linear_form w (-b, a) j, run_linear_form w 0 j]
      change -b * a + a * b = 0 * a + 0 * b
      ring

/-- Before the last use of edge `i`, edge `i+1` must have been used.
Otherwise all future downstream data depend on a single scalar coordinate,
which cannot distinguish two independent real source deviations. This is the
cross-wave precedence in `pipeline_extensions` at lines 176–192. -/
theorem complete_cross_precedence (d : ℕ) (e next : Fin d)
    (hne : next.val = e.val + 1) (pre post : List (Fin d))
    (hc : Complete (Fin.last d) (initial d)
      ((pre ++ e :: post).map (pathEdge d))) :
    next ∈ pre ∨ e ∈ post := by
  by_contra h
  push_neg at h
  have hen : e ≠ next := by intro he; have := congrArg Fin.val he; omega
  have hav : ∀ a ∈ pre ++ [e], a ≠ next := by
    intro a ha he
    subst a
    simp only [List.mem_append, List.mem_singleton] at ha
    rcases ha with ha | ha
    · exact h.1 ha
    · exact hen ha.symm
  have hz := avoid_cut_zero next (pre ++ [e]) (initial d)
    (by intro p j hj; simp [initial, initialState,
      show j.val ≠ 0 by omega, show j.val ≠ 1 by omega]) hav
  obtain ⟨p, hp, hk⟩ := coordinate_kernel (pre ++ [e]) next.castSucc
  let c := run (Fin.last d) ((pre ++ [e]).map (pathEdge d)) (initial d)
  have hr : c.record p = c.record 0 := by
    apply run_rightEq next (pre ++ [e]) (initial d) p 0
    · have hn := next.isLt
      simp [initial, initialState, show d ≠ 0 by omega, show d ≠ 1 by omega]
    · intro j hj
      simp [initial, initialState, show j.val ≠ 0 by omega, show j.val ≠ 1 by omega]
    · exact hav
  have hs : RightEq e (c.state p) (c.state 0) := by
    intro j hj
    by_cases heq : j.val = next.val
    · have hjn : j = next.castSucc := Fin.ext heq
      rw [hjn]
      exact hk
    · have hgt : next.val < j.val := by omega
      exact (hz p j hgt).trans (hz 0 j hgt).symm
  have hfinal := run_rightEq e post c p 0 hr hs
    (by intro a ha he; subst a; exact h.2 ha)
  apply hp
  apply hc
  have hw : pre ++ e :: post = (pre ++ [e]) ++ post := by simp
  rw [hw, run_append_path]
  exact hfinal

/-- Occurrence position of a two-wave event: first occurrences tag the
first wave, and last occurrences tag the second wave. At the sharp counts
these are distinct for every positive edge; edge zero has only a last event. -/
def Event.position {d : ℕ} (w : List (Fin d)) : Event d → ℕ
  | .first i _ => w.idxOf i
  | .second i => w.length - 1 - w.reverse.idxOf i

/-- Linear extensions of the poset in
`code/source_checkpoint_selection/verify.py:176-192`, expressed by occurrence
positions in the edge word. The multiplicities give every event exactly one
position; the `Before` inequalities are its three direct precedence families. -/
def TwoWave {d : ℕ} (w : List (Fin d)) : Prop :=
  (∀ i : Fin d, w.count i = if i.val = 0 then 1 else 2) ∧
  ∀ a b : Event d, Before a b → a.position w < b.position w

private theorem split_first {d : ℕ} (w : List (Fin d)) (i : Fin d) (hm : i ∈ w) :
    ∃ pre post, w = pre ++ i :: post ∧ i ∉ pre := by
  induction w with
  | nil => simp at hm
  | cons a w ih =>
    by_cases ha : a = i
    · subst a
      exact ⟨[], w, rfl, by simp⟩
    · have hi : i ∈ w := by simpa [Ne.symm ha] using hm
      obtain ⟨pre, post, he, hn⟩ := ih hi
      exact ⟨a :: pre, post, by simp [he], by simp [Ne.symm ha, hn]⟩

private theorem split_last {d : ℕ} (w : List (Fin d)) (i : Fin d) (hm : i ∈ w) :
    ∃ pre post, w = pre ++ i :: post ∧ i ∉ post := by
  obtain ⟨pre, post, he, hn⟩ := split_first w.reverse i (by simpa using hm)
  refine ⟨post.reverse, pre.reverse, ?_, by simpa using hn⟩
  have hh := congrArg List.reverse he
  simpa using hh

private theorem last_position {d : ℕ} (pre post : List (Fin d)) (i : Fin d)
    (hn : i ∉ post) :
    (pre ++ i :: post).length - 1 - (pre ++ i :: post).reverse.idxOf i = pre.length := by
  have hi : (pre ++ i :: post).reverse.idxOf i = post.length := by
    simp [List.reverse_append, List.reverse_cons, List.append_assoc,
      List.idxOf_append_of_notMem, hn]
  rw [hi]
  simp only [List.length_append, List.length_cons]
  omega

/-- Every shortest completing word obeys all three event-order families.
This is the necessity direction of the two-wave classification at `d ≥ 1`;
no sufficiency or enumeration assumption occurs in its hypotheses. -/
theorem twoWave_necessary (d : ℕ) (hd : 1 ≤ d) (w : List (Fin d))
    (hlen : w.length = 2 * d - 1)
    (hc : Complete (Fin.last d) (initial d) (w.map (pathEdge d))) : TwoWave w := by
  have hcounts := shortest_counts d hd w hlen hc
  have hmem : ∀ i : Fin d, i ∈ w := by
    intro i
    apply List.count_pos_iff.mp
    rw [hcounts i]
    split_ifs <;> omega
  refine ⟨hcounts, ?_⟩
  intro a b hb
  cases a with
  | first i hi =>
    cases b with
    | first j hj =>
      change i.val + 1 = j.val at hb
      obtain ⟨pre, post, rfl, hn⟩ := split_first w j (hmem j)
      have hm := shortest_first_precedence d hd i j hi hb.symm pre post hlen hc
      change (pre ++ j :: post).idxOf i < (pre ++ j :: post).idxOf j
      rw [List.idxOf_append_of_mem hm, List.idxOf_append_of_notMem hn]
      simpa using List.idxOf_lt_length_of_mem hm
    | second j =>
      change i.val = j.val + 1 at hb
      obtain ⟨pre, post, rfl, hn⟩ := split_last w j (hmem j)
      have hm : i ∈ pre := (complete_cross_precedence d j i hb pre post hc).resolve_right hn
      change (pre ++ j :: post).idxOf i <
        (pre ++ j :: post).length - 1 - (pre ++ j :: post).reverse.idxOf j
      rw [last_position pre post j hn, List.idxOf_append_of_mem hm]
      exact List.idxOf_lt_length_of_mem hm
  | second i =>
    cases b with
    | first j hj => exact False.elim hb
    | second j =>
      change i.val + 1 = j.val at hb
      obtain ⟨pre, post, rfl, hn⟩ := split_last w i (hmem i)
      have hm := shortest_second_precedence d hd i j hb.symm pre post hlen hc
      change (pre ++ i :: post).length - 1 - (pre ++ i :: post).reverse.idxOf i <
        (pre ++ i :: post).length - 1 - (pre ++ i :: post).reverse.idxOf j
      rw [last_position pre post i hn]
      have hmr : j ∈ post.reverse := by simpa using hm
      have hjidx : (pre ++ i :: post).reverse.idxOf j = post.reverse.idxOf j := by
        simp [List.reverse_append, List.reverse_cons, List.append_assoc,
          List.idxOf_append_of_mem hmr]
      rw [hjidx]
      have hlt := List.idxOf_lt_length_of_mem hmr
      simp only [List.length_reverse] at hlt
      simp only [List.length_append, List.length_cons]
      omega

/-- Completing shortest words, using the original path alphabet and exact
retained-record semantics. -/
def ShortestWord (d : ℕ) :=
  {w : List (Fin d) // w.length = 2 * d - 1 ∧
    Complete (Fin.last d) (initial d) (w.map (pathEdge d))}

/-- Decode wave letters with `u` first-wave events and `v` second-wave
 events emitted. First edges start at one; second edges start at zero. -/
def waveDecode (u v : ℕ) : List DyckStep → List ℕ
  | [] => []
  | .U :: s => (u + 1) :: waveDecode (u + 1) v s
  | .D :: s => v :: waveDecode u (v + 1) s

/-- Recover wave letters from edge indices, keeping the next first-wave
 index. On ballot inputs, a second-wave index is never that next index. -/
def waveEncode (u : ℕ) : List ℕ → List DyckStep
  | [] => []
  | e :: w => if e = u + 1 then .U :: waveEncode (u + 1) w
      else .D :: waveEncode u w

private def BallotFrom (u v : ℕ) (s : List DyckStep) : Prop :=
  ∀ i, v + (s.take i).count .D ≤ u + (s.take i).count .U

private theorem ballot_tail_U {u v : ℕ} {s : List DyckStep}
    (h : BallotFrom u v (.U :: s)) : BallotFrom (u + 1) v s := by
  intro i
  have hi := h (i + 1)
  simpa [List.take_succ_cons, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using hi

private theorem ballot_tail_D {u v : ℕ} {s : List DyckStep}
    (h : BallotFrom u v (.D :: s)) : BallotFrom u (v + 1) s := by
  intro i
  have hi := h (i + 1)
  simpa [List.take_succ_cons, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using hi

private theorem waveEncode_decode (s : List DyckStep) (u v : ℕ)
    (h : BallotFrom u v s) : waveEncode u (waveDecode u v s) = s := by
  induction s generalizing u v with
  | nil => rfl
  | cons a s ih =>
    cases a with
    | U => simp [waveDecode, waveEncode, ih _ _ (ballot_tail_U h)]
    | D =>
      have hv : v ≤ u := by simpa using h 0
      simp [waveDecode, waveEncode, show v ≠ u + 1 by omega,
        ih _ _ (ballot_tail_D h)]

private theorem waveDecode_length (s : List DyckStep) (u v : ℕ) :
    (waveDecode u v s).length = s.length := by
  induction s generalizing u v with
  | nil => rfl
  | cons a s ih => cases a <;> simp [waveDecode, ih]

private theorem waveDecode_bound (s : List DyckStep) (u v n : ℕ)
    (hu : u + s.count .U ≤ n) (hv : v + s.count .D ≤ n) :
    ∀ e ∈ waveDecode u v s, e ≤ n := by
  induction s generalizing u v with
  | nil => simp [waveDecode]
  | cons a s ih =>
    cases a with
    | U =>
      simp only [List.count_cons_self, List.count_cons_of_ne (by decide : DyckStep.U ≠ .D)] at hu hv
      intro e he
      rcases List.mem_cons.mp he with rfl | he
      · omega
      · exact ih (u + 1) v (by omega) hv e he
    | D =>
      simp only [List.count_cons_self, List.count_cons_of_ne (by decide : DyckStep.D ≠ .U)] at hu hv
      intro e he
      rcases List.mem_cons.mp he with rfl | he
      · omega
      · exact ih u (v + 1) hu (by omega) e he

/-- The edge-index word decoded from a Dyck word, with the final second-wave
 edge appended. Its length is odd, unlike the balanced wave-letter list. -/
def dyckIndices (p : DyckWord) : List ℕ :=
  waveDecode 0 0 p.toList ++ [p.semilength]

/-- Decoding and then recovering wave letters returns the original Dyck list.
 The mandatory final second-wave event is removed before recovering letters. -/
theorem dyckIndices_roundtrip (p : DyckWord) :
    waveEncode 0 (dyckIndices p).dropLast = p.toList := by
  simp only [dyckIndices, List.dropLast_concat]
  exact waveEncode_decode p.toList 0 0 (by simpa [BallotFrom] using p.count_D_le_count_U)

/-- Distinct Dyck words decode to distinct edge words. -/
theorem dyckIndices_injective : Function.Injective dyckIndices := by
  intro p q h
  apply DyckWord.ext
  rw [← dyckIndices_roundtrip p, ← dyckIndices_roundtrip q, h]

private theorem dyckIndices_bound (p : DyckWord) :
    ∀ e ∈ dyckIndices p, e ≤ p.semilength := by
  intro e he
  rcases List.mem_append.mp he with he | he
  · exact waveDecode_bound p.toList 0 0 p.semilength (by simp [DyckWord.semilength])
      (by simp [DyckWord.semilength, p.count_U_eq_count_D]) e he
  · exact (List.mem_singleton.mp he).le

/-- A Dyck word of semilength `n` gives a word in the original path alphabet
 `Fin (n + 1)`, with both wave indices retained. -/
def dyckPathWord (n : ℕ) (p : {p : DyckWord // p.semilength = n}) : List (Fin (n + 1)) :=
  (dyckIndices p.val).attach.map fun e =>
    ⟨e.val, by have := dyckIndices_bound p.val e.val e.property; omega⟩

private theorem dyckPathWord_values (n : ℕ) (p : {p : DyckWord // p.semilength = n}) :
    (dyckPathWord n p).map Fin.val = dyckIndices p.val := by
  simp [dyckPathWord, List.map_map]

/-- Recovering letters from the path alphabet is a left inverse to decoding. -/
theorem dyckPathWord_roundtrip (n : ℕ) (p : {p : DyckWord // p.semilength = n}) :
    waveEncode 0 ((dyckPathWord n p).map Fin.val).dropLast = p.val.toList := by
  rw [dyckPathWord_values, dyckIndices_roundtrip]

/-- The decoder into the original path alphabet is injective at every depth. -/
theorem dyckPathWord_injective (n : ℕ) : Function.Injective (dyckPathWord n) := by
  intro p q h
  apply Subtype.ext
  apply dyckIndices_injective
  simpa only [dyckPathWord_values] using congrArg (List.map Fin.val) h

/-- Every decoded path word has the sharp path horizon. -/
theorem dyckPathWord_length (n : ℕ) (p : {p : DyckWord // p.semilength = n}) :
    (dyckPathWord n p).length = 2 * (n + 1) - 1 := by
  have hv := congrArg List.length (dyckPathWord_values n p)
  simp only [List.length_map, dyckIndices, List.length_append, List.length_singleton,
    waveDecode_length] at hv
  have hl := p.val.two_mul_semilength_eq_length
  rw [p.property] at hl
  omega

private theorem waveDecode_count (s : List DyckStep) (u v e : ℕ) :
    (waveDecode u v s).count e =
      (if u < e ∧ e ≤ u + s.count .U then 1 else 0) +
      (if v ≤ e ∧ e < v + s.count .D then 1 else 0) := by
  induction s generalizing u v with
  | nil => simp only [waveDecode, List.count_nil, Nat.add_zero]; split_ifs <;> omega
  | cons a s ih =>
    cases a <;>
      simp only [waveDecode, List.count_cons, beq_iff_eq, ih,
        List.count_cons_self, List.count_cons_of_ne (by decide : DyckStep.U ≠ .D),
        List.count_cons_of_ne (by decide : DyckStep.D ≠ .U)] <;>
      split_ifs <;> omega

/-- Decoded path words use edge zero once and every positive edge twice. -/
theorem dyckPathWord_counts (n : ℕ) (p : {p : DyckWord // p.semilength = n})
    (i : Fin (n + 1)) : (dyckPathWord n p).count i = if i.val = 0 then 1 else 2 := by
  rw [← List.count_map_of_injective _ Fin.val Fin.val_injective i,
    dyckPathWord_values, dyckIndices, List.count_append, waveDecode_count]
  have hU : p.val.toList.count .U = n := p.property
  have hD : p.val.toList.count .D = n := p.val.count_U_eq_count_D.symm.trans hU
  simp only [hU, hD, p.property, Nat.zero_add, Nat.zero_le, true_and,
    List.count_singleton, beq_iff_eq]
  split_ifs <;> omega

/-- Without the ballot condition, different wave-letter lists can decode
 to the same edge indices. Two descending steps collide with a descent and
 an ascent when both counters start at zero. -/
theorem waveDecode_without_ballot_collision :
    ([DyckStep.D, .D] : List DyckStep) ≠ [.D, .U] ∧
      waveDecode 0 0 [.D, .D] = waveDecode 0 0 [.D, .U] := by
  decide

/-- Image of the explicit Dyck decoder in the original word alphabet.
 This type records decoded candidates; completion is a separate proposition. -/
def DyckPathWord (n : ℕ) := Set.range (dyckPathWord n)

/-- Recover the Dyck word from a word in the decoder image, using the
 explicit wave-letter encoder on its edge indices. -/
def pathWordDyck (n : ℕ) (w : DyckPathWord n) : {p : DyckWord // p.semilength = n} :=
  ⟨⟨waveEncode 0 (w.val.map Fin.val).dropLast, by
      obtain ⟨p, hp⟩ := w.property
      rw [← hp, dyckPathWord_roundtrip]
      exact p.val.count_U_eq_count_D, by
      obtain ⟨p, hp⟩ := w.property
      rw [← hp, dyckPathWord_roundtrip]
      exact p.val.count_D_le_count_U⟩, by
    obtain ⟨p, hp⟩ := w.property
    change (waveEncode 0 (w.val.map Fin.val).dropLast).count .U = n
    rw [← hp, dyckPathWord_roundtrip]
    exact p.property⟩

/-- The explicit encoder is a left inverse to the path-word decoder. -/
theorem pathWordDyck_decode (n : ℕ) (p : {p : DyckWord // p.semilength = n}) :
    pathWordDyck n ⟨dyckPathWord n p, ⟨p, rfl⟩⟩ = p := by
  apply Subtype.ext
  apply DyckWord.ext
  exact dyckPathWord_roundtrip n p

/-- The explicit decoder is a left inverse to the encoder on its image. -/
theorem dyckPathWord_encode (n : ℕ) (w : DyckPathWord n) :
    dyckPathWord n (pathWordDyck n w) = w.val := by
  obtain ⟨p, hp⟩ := w.property
  have hw : w = ⟨dyckPathWord n p, ⟨p, rfl⟩⟩ := Subtype.ext hp.symm
  subst w
  rw [pathWordDyck_decode]

/-- The decoder and explicit encoder identify Dyck words with the decoder
 image in the original path alphabet. -/
def dyckPathEquiv (n : ℕ) : {p : DyckWord // p.semilength = n} ≃ DyckPathWord n where
  toFun p := ⟨dyckPathWord n p, ⟨p, rfl⟩⟩
  invFun := pathWordDyck n
  left_inv := pathWordDyck_decode n
  right_inv w := Subtype.ext (dyckPathWord_encode n w)

/-- There are Catalan-many distinct decoded path words. The theorem counts
 the decoder image; identifying that image with `ShortestWord` also requires
 completion and coverage proofs. -/
theorem dyckPathWord_card (n : ℕ) : Nat.card (DyckPathWord n) = catalan n := by
  rw [← Nat.card_congr (dyckPathEquiv n), Nat.card_eq_fintype_card]
  exact DyckWord.card_dyckWord_semilength_eq_catalan n

private def WaveOrder {d : ℕ} (w : List (Fin d)) : Prop :=
  (∀ i : Fin d, w.count i = if i.val = 0 then 1 else 2) ∧
  ∀ i j : Fin d, i.val + 1 = j.val →
    (1 ≤ i.val → w.idxOf i < w.idxOf j) ∧
    (w.length - 1 - w.reverse.idxOf i < w.length - 1 - w.reverse.idxOf j) ∧
    w.idxOf j < w.length - 1 - w.reverse.idxOf i

private instance {d : ℕ} (w : List (Fin d)) : Decidable (WaveOrder w) := by
  unfold WaveOrder
  infer_instance

private theorem waveOrder_of_twoWave {d : ℕ} (w : List (Fin d)) (h : TwoWave w) :
    WaveOrder w := by
  refine ⟨h.1, ?_⟩
  intro i j hij
  refine ⟨fun hi => h.2 (.first i hi) (.first j (by omega)) hij, ?_, ?_⟩
  · exact h.2 (.second i) (.second j) hij
  · exact h.2 (.first j (by omega)) (.second i) hij.symm

private theorem shortest_last (d : ℕ) (hd : 1 ≤ d) (pre : List (Fin d)) (e : Fin d)
    (hlen : (pre ++ [e]).length = 2 * d - 1)
    (hc : Complete (Fin.last d) (initial d) ((pre ++ [e]).map (pathEdge d))) :
    e.val = d - 1 := by
  by_contra h
  let next : Fin d := ⟨e.val + 1, by omega⟩
  have hn := shortest_second_precedence d hd e next rfl pre [] hlen hc
  simp at hn

private theorem shortest_card_of_finset (d : ℕ) (s : Finset (List (Fin d)))
    (hs : ∀ w ∈ s, w.length = 2 * d - 1 ∧
      Complete (Fin.last d) (initial d) (w.map (pathEdge d)))
    (hc : ∀ w : ShortestWord d, w.val ∈ s) : Nat.card (ShortestWord d) = s.card := by
  let e : ShortestWord d ≃ {w // w ∈ s} :=
    { toFun := fun w => ⟨w.val, hc w⟩
      invFun := fun w => ⟨w.val, hs w.val w.property⟩
      left_inv := fun _ => rfl
      right_inv := fun _ => rfl }
  rw [Nat.card_congr e, Nat.card_eq_fintype_card, Fintype.card_coe]

/-- The depth-one census contains only its single-edge serial word. -/
theorem shortest_one_unique (w : ShortestWord 1) : w.val = [0] := by
  have hlen : w.val.length = 1 := by simpa using w.property.1
  obtain ⟨a, ha⟩ := List.length_eq_one_iff.mp hlen
  have he : a = (0 : Fin 1) := Subsingleton.elim _ _
  simpa [he] using ha

/-- The depth-one completing-word count is one. -/
theorem shortest_card_one : Nat.card (ShortestWord 1) = 1 := by
  apply Nat.card_eq_one_iff_exists.mpr
  refine ⟨⟨serialWord 1, serialWord_length 1 (by omega), serialWord_complete 1 (by omega)⟩, ?_⟩
  intro w
  apply Subtype.ext
  exact (shortest_one_unique w).trans (shortest_one_unique _).symm

/-- The repeated first mean at depth two carries no source-zero information
to the receiver before the only use of edge zero. -/
theorem depth_two_repeat_not_complete :
    ¬ Complete (Fin.last 2) (initial 2)
      (([1, 1, 0] : List (Fin 2)).map (pathEdge 2)) := by
  intro h
  have hs :
      (run (Fin.last 2) (([1, 1, 0] : List (Fin 2)).map (pathEdge 2)) (initial 2)).record
          ((0, 0) : Pair) =
        (run (Fin.last 2) (([1, 1, 0] : List (Fin 2)).map (pathEdge 2)) (initial 2)).record
          ((1, 0) : Pair) := by rfl
  have hp := h hs
  norm_num at hp

/-- The depth-two census contains only `[1,0,1]`. -/
theorem shortest_two_unique (w : ShortestWord 2) : w.val = [1, 0, 1] := by
  obtain ⟨xs, hlen, hc⟩ := w
  have hl : xs.length = 3 := by simpa using hlen
  obtain ⟨a, rest, rfl⟩ := List.exists_of_length_succ xs hl
  have hlrest : rest.length = 2 := by simpa using hl
  obtain ⟨b, rest, rfl⟩ := List.exists_of_length_succ rest hlrest
  have hlrest : rest.length = 1 := by simpa using hlrest
  obtain ⟨c, rfl⟩ := List.length_eq_one_iff.mp hlrest
  have ha : a = (1 : Fin 2) := Fin.ext (shortest_first 2 (by omega) a [b, c] hlen hc)
  subst a
  have hcount := shortest_counts 2 (by omega) [1, b, c] hlen hc 0
  fin_cases b <;> fin_cases c
  · norm_num at hcount
  · rfl
  · exact False.elim (depth_two_repeat_not_complete hc)
  · norm_num at hcount

/-- The depth-two completing-word count is one. -/
theorem shortest_card_two : Nat.card (ShortestWord 2) = 1 := by
  apply Nat.card_eq_one_iff_exists.mpr
  refine ⟨⟨serialWord 2, serialWord_length 2 (by omega), serialWord_complete 2 (by omega)⟩, ?_⟩
  intro w
  apply Subtype.ext
  exact (shortest_two_unique w).trans (shortest_two_unique _).symm

private def candidates_three : Finset (List (Fin 3)) :=
  {[1, 2, 0, 1, 2],
    [1, 0, 2, 1, 2]}

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
private theorem candidates_three_exhaustive :
    ∀ a0 a1 a2 : Fin 3, WaveOrder [1, a0, a1, a2, 2] →
      [1, a0, a1, a2, 2] ∈ candidates_three := by
  decide +kernel

private theorem candidates_three_complete :
    ∀ w ∈ candidates_three, w.length = 2 * 3 - 1 ∧
      Complete (Fin.last 3) (initial 3) (w.map (pathEdge 3)) := by
  intro w hw
  simp only [candidates_three, Finset.mem_insert, Finset.mem_singleton] at hw
  rcases hw with rfl | rfl <;> constructor
  all_goals first | decide | skip
  all_goals
    intro p q h
    simp [pathEdge, run, advance, initial, initialState, pairAverage] at h
    apply Prod.ext <;> dsimp <;> rcases h with ⟨h0, h1⟩ <;> linarith

/-- The depth-three completing-word count is 2, using finite
 event-order exhaustion and exact retained-record reconstruction. -/
theorem shortest_card_three : Nat.card (ShortestWord 3) = 2 := by
  trans candidates_three.card
  · apply shortest_card_of_finset 3 candidates_three candidates_three_complete
    intro w
    obtain ⟨xs, hlen, hc⟩ := w
    have hl : xs.length = 5 := by simpa using hlen
    obtain ⟨a, rest1, rfl⟩ := List.exists_of_length_succ xs hl
    have hl : rest1.length = 4 := by simpa using hl
    obtain ⟨a0, rest2, rfl⟩ := List.exists_of_length_succ rest1 hl
    have hl : rest2.length = 3 := by simpa using hl
    obtain ⟨a1, rest3, rfl⟩ := List.exists_of_length_succ rest2 hl
    have hl : rest3.length = 2 := by simpa using hl
    obtain ⟨a2, rest4, rfl⟩ := List.exists_of_length_succ rest3 hl
    have hl : rest4.length = 1 := by simpa using hl
    obtain ⟨z, rfl⟩ := List.length_eq_one_iff.mp hl
    have ha : a = (1 : Fin 3) := Fin.ext (shortest_first 3 (by omega) a
      [a0, a1, a2, z] hlen hc)
    have hz : z = (2 : Fin 3) := Fin.ext (shortest_last 3 (by omega)
      [a, a0, a1, a2] z hlen hc)
    have ho := waveOrder_of_twoWave [a, a0, a1, a2, z]
      (twoWave_necessary 3 (by omega) [a, a0, a1, a2, z] hlen hc)
    subst a
    subst z
    exact candidates_three_exhaustive a0 a1 a2 ho
  · decide

private def candidates_four : Finset (List (Fin 4)) :=
  {[1, 2, 3, 0, 1, 2, 3],
    [1, 2, 0, 3, 1, 2, 3],
    [1, 2, 0, 1, 3, 2, 3],
    [1, 0, 2, 3, 1, 2, 3],
    [1, 0, 2, 1, 3, 2, 3]}

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
private theorem candidates_four_exhaustive :
    ∀ a0 a1 a2 a3 a4 : Fin 4, WaveOrder [1, a0, a1, a2, a3, a4, 3] →
      [1, a0, a1, a2, a3, a4, 3] ∈ candidates_four := by
  decide +kernel

private theorem candidates_four_complete :
    ∀ w ∈ candidates_four, w.length = 2 * 4 - 1 ∧
      Complete (Fin.last 4) (initial 4) (w.map (pathEdge 4)) := by
  intro w hw
  simp only [candidates_four, Finset.mem_insert, Finset.mem_singleton] at hw
  rcases hw with rfl | rfl | rfl | rfl | rfl <;> constructor
  all_goals first | decide | skip
  all_goals
    intro p q h
    simp [pathEdge, run, advance, initial, initialState, pairAverage] at h
    apply Prod.ext <;> dsimp <;> rcases h with ⟨h0, h1⟩ <;> linarith

/-- The depth-four completing-word count is 5, using finite
 event-order exhaustion and exact retained-record reconstruction. -/
theorem shortest_card_four : Nat.card (ShortestWord 4) = 5 := by
  trans candidates_four.card
  · apply shortest_card_of_finset 4 candidates_four candidates_four_complete
    intro w
    obtain ⟨xs, hlen, hc⟩ := w
    have hl : xs.length = 7 := by simpa using hlen
    obtain ⟨a, rest1, rfl⟩ := List.exists_of_length_succ xs hl
    have hl : rest1.length = 6 := by simpa using hl
    obtain ⟨a0, rest2, rfl⟩ := List.exists_of_length_succ rest1 hl
    have hl : rest2.length = 5 := by simpa using hl
    obtain ⟨a1, rest3, rfl⟩ := List.exists_of_length_succ rest2 hl
    have hl : rest3.length = 4 := by simpa using hl
    obtain ⟨a2, rest4, rfl⟩ := List.exists_of_length_succ rest3 hl
    have hl : rest4.length = 3 := by simpa using hl
    obtain ⟨a3, rest5, rfl⟩ := List.exists_of_length_succ rest4 hl
    have hl : rest5.length = 2 := by simpa using hl
    obtain ⟨a4, rest6, rfl⟩ := List.exists_of_length_succ rest5 hl
    have hl : rest6.length = 1 := by simpa using hl
    obtain ⟨z, rfl⟩ := List.length_eq_one_iff.mp hl
    have ha : a = (1 : Fin 4) := Fin.ext (shortest_first 4 (by omega) a
      [a0, a1, a2, a3, a4, z] hlen hc)
    have hz : z = (3 : Fin 4) := Fin.ext (shortest_last 4 (by omega)
      [a, a0, a1, a2, a3, a4] z hlen hc)
    have ho := waveOrder_of_twoWave [a, a0, a1, a2, a3, a4, z]
      (twoWave_necessary 4 (by omega) [a, a0, a1, a2, a3, a4, z] hlen hc)
    subst a
    subst z
    exact candidates_four_exhaustive a0 a1 a2 a3 a4 ho
  · decide

private def candidates_five : Finset (List (Fin 5)) :=
  {[1, 2, 3, 4, 0, 1, 2, 3, 4],
    [1, 2, 3, 0, 4, 1, 2, 3, 4],
    [1, 2, 3, 0, 1, 4, 2, 3, 4],
    [1, 2, 3, 0, 1, 2, 4, 3, 4],
    [1, 2, 0, 3, 4, 1, 2, 3, 4],
    [1, 2, 0, 3, 1, 4, 2, 3, 4],
    [1, 2, 0, 3, 1, 2, 4, 3, 4],
    [1, 2, 0, 1, 3, 4, 2, 3, 4],
    [1, 2, 0, 1, 3, 2, 4, 3, 4],
    [1, 0, 2, 3, 4, 1, 2, 3, 4],
    [1, 0, 2, 3, 1, 4, 2, 3, 4],
    [1, 0, 2, 3, 1, 2, 4, 3, 4],
    [1, 0, 2, 1, 3, 4, 2, 3, 4],
    [1, 0, 2, 1, 3, 2, 4, 3, 4]}

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
private theorem candidates_five_exhaustive :
    ∀ a0 a1 a2 a3 a4 a5 a6 : Fin 5, WaveOrder [1, a0, a1, a2, a3, a4, a5, a6, 4] →
      [1, a0, a1, a2, a3, a4, a5, a6, 4] ∈ candidates_five := by
  decide +kernel

set_option maxHeartbeats 1000000 in
private theorem candidates_five_complete :
    ∀ w ∈ candidates_five, w.length = 2 * 5 - 1 ∧
      Complete (Fin.last 5) (initial 5) (w.map (pathEdge 5)) := by
  intro w hw
  simp only [candidates_five, Finset.mem_insert, Finset.mem_singleton] at hw
  rcases hw with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl <;> constructor
  all_goals first | decide | skip
  all_goals
    intro p q h
    simp [pathEdge, run, advance, initial, initialState, pairAverage] at h
    apply Prod.ext <;> dsimp <;> rcases h with ⟨h0, h1⟩ <;> linarith

/-- The depth-five completing-word count is 14, using finite
 event-order exhaustion and exact retained-record reconstruction. -/
theorem shortest_card_five : Nat.card (ShortestWord 5) = 14 := by
  trans candidates_five.card
  · apply shortest_card_of_finset 5 candidates_five candidates_five_complete
    intro w
    obtain ⟨xs, hlen, hc⟩ := w
    have hl : xs.length = 9 := by simpa using hlen
    obtain ⟨a, rest1, rfl⟩ := List.exists_of_length_succ xs hl
    have hl : rest1.length = 8 := by simpa using hl
    obtain ⟨a0, rest2, rfl⟩ := List.exists_of_length_succ rest1 hl
    have hl : rest2.length = 7 := by simpa using hl
    obtain ⟨a1, rest3, rfl⟩ := List.exists_of_length_succ rest2 hl
    have hl : rest3.length = 6 := by simpa using hl
    obtain ⟨a2, rest4, rfl⟩ := List.exists_of_length_succ rest3 hl
    have hl : rest4.length = 5 := by simpa using hl
    obtain ⟨a3, rest5, rfl⟩ := List.exists_of_length_succ rest4 hl
    have hl : rest5.length = 4 := by simpa using hl
    obtain ⟨a4, rest6, rfl⟩ := List.exists_of_length_succ rest5 hl
    have hl : rest6.length = 3 := by simpa using hl
    obtain ⟨a5, rest7, rfl⟩ := List.exists_of_length_succ rest6 hl
    have hl : rest7.length = 2 := by simpa using hl
    obtain ⟨a6, rest8, rfl⟩ := List.exists_of_length_succ rest7 hl
    have hl : rest8.length = 1 := by simpa using hl
    obtain ⟨z, rfl⟩ := List.length_eq_one_iff.mp hl
    have ha : a = (1 : Fin 5) := Fin.ext (shortest_first 5 (by omega) a
      [a0, a1, a2, a3, a4, a5, a6, z] hlen hc)
    have hz : z = (4 : Fin 5) := Fin.ext (shortest_last 5 (by omega)
      [a, a0, a1, a2, a3, a4, a5, a6] z hlen hc)
    have ho := waveOrder_of_twoWave [a, a0, a1, a2, a3, a4, a5, a6, z]
      (twoWave_necessary 5 (by omega) [a, a0, a1, a2, a3, a4, a5, a6, z] hlen hc)
    subst a
    subst z
    exact candidates_five_exhaustive a0 a1 a2 a3 a4 a5 a6 ho
  · decide

/-- A concrete order control at depth three: its edge counts have the sharp
values, but the second use of edge one comes before edge zero. -/
def orderBadWord : List (Fin 3) := [1, 2, 1, 2, 0]

/-- Its tagged events expose the violated second-wave dependency. -/
def orderBadEvents : List (Event 3) :=
  [.first 1 (by decide), .first 2 (by decide), .second 1,
    .second 2, .second 0]

theorem orderBadEvents_edges : orderBadEvents.map Event.edge = orderBadWord := by
  rfl

theorem orderBadEvents_breaks_precedence :
    Before (Event.second (0 : Fin 3)) (Event.second (1 : Fin 3)) ∧
      orderBadEvents[2]? = some (Event.second 1) ∧
      orderBadEvents[4]? = some (Event.second 0) := by
  constructor
  · rfl
  constructor <;> rfl

theorem orderBadWord_length : orderBadWord.length = 2 * 3 - 1 := by decide

theorem orderBadWord_counts :
    orderBadWord.count 0 = 1 ∧ orderBadWord.count 1 = 2 ∧
      orderBadWord.count 2 = 2 := by decide

/-- The count-correct word never carries the source at port zero to the
receiver: its only use of edge zero occurs last. -/
theorem orderBadWord_not_complete :
    ¬ Complete (Fin.last 3) (initial 3)
      (orderBadWord.map (pathEdge 3)) := by
  intro h
  have hs :
      (run (Fin.last 3) (orderBadWord.map (pathEdge 3)) (initial 3)).record
          ((0, 0) : Pair) =
        (run (Fin.last 3) (orderBadWord.map (pathEdge 3)) (initial 3)).record
          ((1, 0) : Pair) := by
    rfl
  have hp := h hs
  norm_num at hp

/-- The serial witness obeys the event-poset predicate at every positive
depth, so the universal necessity statement has concrete completing models. -/
theorem serialWord_twoWave (d : ℕ) (hd : 1 ≤ d) : TwoWave (serialWord d) :=
  twoWave_necessary d hd (serialWord d) (serialWord_length d hd) (serialWord_complete d hd)

/-- The count-correct order control fails the occurrence-position poset. -/
theorem orderBadWord_not_twoWave : ¬ TwoWave orderBadWord := by
  intro h
  have hh := h.2 (Event.second (0 : Fin 3)) (Event.second (1 : Fin 3)) (by rfl)
  norm_num [Event.position, orderBadWord, List.idxOf_cons] at hh
  omega

/-- The first five Catalan values used by the finite verifier. -/
theorem small_catalan_values :
    catalan 0 = 1 ∧ catalan 1 = 1 ∧ catalan 2 = 2 ∧
      catalan 3 = 5 ∧ catalan 4 = 14 := by
  norm_num [catalan_eq_centralBinom_div, Nat.centralBinom, Nat.choose]

/-- A chord of the path at depth two admits a completing word shorter than the
path minimum, so its census has a different horizon and alphabet. -/
theorem chord_outside_path_horizon :
    Complete (Fin.last 2) (initial 2) chordWord ∧
      chordWord.length < 2 * 2 - 1 := chord_countermodel

#print axioms waveDecode_without_ballot_collision
#print axioms shortest_card_three
#print axioms shortest_card_four
#print axioms shortest_card_five
#print axioms dyckIndices_roundtrip
#print axioms dyckIndices_injective
#print axioms dyckPathWord_roundtrip
#print axioms dyckPathWord_injective
#print axioms dyckPathWord_length
#print axioms dyckPathWord_counts
#print axioms pathWordDyck_decode
#print axioms dyckPathWord_encode
#print axioms dyckPathWord_card
#print axioms serialWord_twoWave
#print axioms orderBadWord_not_twoWave
#print axioms twoWave_necessary
#print axioms shortest_second_precedence
#print axioms complete_cross_precedence
#print axioms shortest_first_precedence
#print axioms shortest_one_unique
#print axioms shortest_card_one
#print axioms depth_two_repeat_not_complete
#print axioms shortest_two_unique
#print axioms shortest_card_two
#print axioms shortest_no_idle
#print axioms complete_not_first_zero
#print axioms shortest_first
#print axioms shortest_counts
#print axioms orderBadWord_length
#print axioms orderBadWord_counts
#print axioms orderBadEvents_edges
#print axioms orderBadEvents_breaks_precedence
#print axioms orderBadWord_not_complete
#print axioms small_catalan_values
#print axioms chord_outside_path_horizon

end
end OPH.SourceCheckpointTwoWave
