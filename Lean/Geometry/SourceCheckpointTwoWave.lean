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

#print axioms orderBadWord_length
#print axioms orderBadWord_counts
#print axioms orderBadEvents_edges
#print axioms orderBadEvents_breaks_precedence
#print axioms orderBadWord_not_complete
#print axioms small_catalan_values
#print axioms chord_outside_path_horizon

end
end OPH.SourceCheckpointTwoWave
