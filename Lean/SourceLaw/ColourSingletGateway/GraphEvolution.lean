import SourceLaw.ColourSingletGateway.GeneratorNorm
import SourceLaw.ColourSingletGateway.UnitaryEvolution
import Mathlib.Tactic.FinCases

/-!
Exact finite graph evolution. The matrix is the complex embedding of the checked
real generator. Typed graph premises imply Hermiticity and the Euclidean norm
bound. Source contraction is a separate premise. Runtime byte binding, a carrier
pin, fixed graph data, a fixed source and physical identification are unproved.
-/

namespace SourceLaw.ColourSingletGateway.GraphEvolution

open scoped BigOperators Matrix.Norms.L2Operator
open GeneratorNorm

noncomputable section

/-- Complex embedding of the existing real generator, without a second entry formula. -/
def H (adj : Fin 240 → Fin 240 → Bool) : Matrix (Fin 240) (Fin 240) ℂ :=
  (generator adj).map (algebraMap ℝ ℂ)

/-- Graph symmetry implies symmetry of the real generator. -/
theorem generator_symmetric (adj : Fin 240 → Fin 240 → Bool)
    (hsymm : ∀ i j, adj i j = adj j i) :
    ∀ i j, generator adj i j = generator adj j i := by
  intro i j
  by_cases hij : i = j
  · subst j; rfl
  · simp only [generator, if_neg hij, if_neg (Ne.symm hij), hsymm i j]

/-- Conjugation fixes the embedded real entries; symmetry gives Hermiticity. -/
theorem hermitian_H (adj : Fin 240 → Fin 240 → Bool)
    (hsymm : ∀ i j, adj i j = adj j i) : (H adj).IsHermitian := by
  ext i j
  simp [H, Matrix.conjTranspose_apply, generator_symmetric adj hsymm j i]

/-- The scoped matrix norm equals the induced Euclidean continuous map norm. -/
theorem norm_H_eq (adj : Fin 240 → Fin 240 → Bool) :
    ‖H adj‖ = ‖Matrix.toEuclideanCLM (𝕜 := ℂ)
      ((generator adj).map (algebraMap ℝ ℂ))‖ := by
  exact (Matrix.l2_opNorm_toEuclideanCLM (H adj)).symm

/-- The checked generator bound transfers to the evolution norm interface. -/
theorem norm_H_le_three (adj : Fin 240 → Fin 240 → Bool)
    (hloop : ∀ i, adj i i = false) (hsymm : ∀ i j, adj i j = adj j i)
    (hdegree : ∀ i, degree adj i ≤ 6) : ‖H adj‖ ≤ 3 := by
  rw [norm_H_eq]
  exact (fin240_generator_norm_le_three adj hloop hsymm hdegree
    (generator adj) (fun _ _ => rfl)).2

/-- Exact evolution from the embedded graph generator, at every real time. -/
def U (adj : Fin 240 → Fin 240 → Bool) (t : ℝ) : Matrix (Fin 240) (Fin 240) ℂ :=
  UnitaryEvolution.U (H adj) t

/-- Graph premises supply both Taylor generator inputs and exact unitarity. -/
theorem graph_evolution (adj : Fin 240 → Fin 240 → Bool)
    (hloop : ∀ i, adj i i = false) (hsymm : ∀ i j, adj i j = adj j i)
    (hdegree : ∀ i, degree adj i ≤ 6) (t : ℝ) :
    (H adj).IsHermitian ∧ ‖H adj‖ ≤ 3 ∧
      U adj t ∈ unitary (Matrix (Fin 240) (Fin 240) ℂ) := by
  exact ⟨hermitian_H adj hsymm, norm_H_le_three adj hloop hsymm hdegree,
    UnitaryEvolution.unitary_exact (H adj) (hermitian_H adj hsymm) t⟩

/-- Exact graph evolution preserves every finite rectangular state norm. -/
theorem norm_U_mul {m : Type*} [Fintype m] [DecidableEq m]
    (adj : Fin 240 → Fin 240 → Bool)
    (hloop : ∀ i, adj i i = false) (hsymm : ∀ i j, adj i j = adj j i)
    (hdegree : ∀ i, degree adj i ≤ 6)
    (S : Matrix (Fin 240) m ℂ) (t : ℝ) : ‖U adj t * S‖ = ‖S‖ := by
  exact UnitaryEvolution.norm_U_mul (H adj) (graph_evolution adj hloop hsymm hdegree t).1 S t

/-- Source contraction is an explicit premise only for the bound by one. -/
theorem norm_U_mul_le_one {m : Type*} [Fintype m] [DecidableEq m]
    (adj : Fin 240 → Fin 240 → Bool)
    (hloop : ∀ i, adj i i = false) (hsymm : ∀ i j, adj i j = adj j i)
    (hdegree : ∀ i, degree adj i ≤ 6)
    (S : Matrix (Fin 240) m ℂ) (hS : ‖S‖ ≤ 1) (t : ℝ) : ‖U adj t * S‖ ≤ 1 := by
  rw [norm_U_mul adj hloop hsymm hdegree S t]
  exact hS

/-- The empty graph on all 240 vertices. -/
def emptyGraph : Fin 240 → Fin 240 → Bool := fun _ _ => false

theorem empty_graph_premises :
    (∀ i, emptyGraph i i = false) ∧
    (∀ i j, emptyGraph i j = emptyGraph j i) ∧
    (∀ i, degree emptyGraph i ≤ 6) := by
  simp [emptyGraph, degree]

theorem empty_graph_evolution (t : ℝ) :
    (H emptyGraph).IsHermitian ∧ ‖H emptyGraph‖ ≤ 3 ∧
      U emptyGraph t ∈ unitary (Matrix (Fin 240) (Fin 240) ℂ) :=
  graph_evolution emptyGraph empty_graph_premises.1 empty_graph_premises.2.1
    empty_graph_premises.2.2 t

/-- One undirected edge joins vertices zero and one. -/
def edgeGraph (i j : Fin 240) : Bool :=
  decide ((i = 0 ∧ j = 1) ∨ (i = 1 ∧ j = 0))

theorem edge_graph_nonempty : edgeGraph 0 1 = true := by decide

theorem edge_graph_premises :
    (∀ i, edgeGraph i i = false) ∧
    (∀ i j, edgeGraph i j = edgeGraph j i) ∧
    (∀ i, degree edgeGraph i ≤ 6) := by
  refine ⟨?_, ?_, ?_⟩
  · intro i
    simp only [edgeGraph, decide_eq_false_iff_not]
    omega
  · intro i j
    simp only [edgeGraph]
    congr 1
    apply propext
    tauto
  · intro i
    by_cases h0 : i = 0
    · subst i; norm_num [degree, edgeGraph]
    · by_cases h1 : i = 1
      · subst i; norm_num [degree, edgeGraph]
      · simp [degree, edgeGraph, h0, h1]

theorem edge_graph_evolution (t : ℝ) :
    (H edgeGraph).IsHermitian ∧ ‖H edgeGraph‖ ≤ 3 ∧
      U edgeGraph t ∈ unitary (Matrix (Fin 240) (Fin 240) ℂ) :=
  graph_evolution edgeGraph edge_graph_premises.1 edge_graph_premises.2.1
    edge_graph_premises.2.2 t

/-- An unequal directed edge, with no reverse edge. -/
def directedGraph (i j : Fin 240) : Bool := decide (i = 0 ∧ j = 1)

theorem directed_graph_loop_free : ∀ i, directedGraph i i = false := by
  intro i
  simp only [directedGraph, decide_eq_false_iff_not]
  omega

theorem directed_graph_degree : ∀ i, degree directedGraph i ≤ 6 := by
  intro i
  by_cases hi : i = 0
  · subst i; norm_num [degree, directedGraph]
  · simp [degree, directedGraph, hi]

theorem directed_graph_not_symmetric :
    ¬ (∀ i j, directedGraph i j = directedGraph j i) := by
  intro h
  have hf := h 0 1
  norm_num [directedGraph] at hf

/-- The off-diagonal unequal entries contradict conjugate symmetry. -/
theorem directed_graph_not_hermitian : ¬ (H directedGraph).IsHermitian := by
  intro h
  have he := h.apply 0 1
  change star ((generator directedGraph 1 0 : ℝ) : ℂ) =
    ((generator directedGraph 0 1 : ℝ) : ℂ) at he
  have h10 : generator directedGraph 1 0 = 0 := by
    rw [generator, if_neg (by decide : (1 : Fin 240) ≠ 0)]
    norm_num [directedGraph]
  have h01 : generator directedGraph 0 1 = -(1 / 2 : ℝ) := by
    rw [generator, if_neg (by decide : (0 : Fin 240) ≠ 1)]
    norm_num [directedGraph]
  rw [h10, h01] at he
  norm_num at he

/-- A loop-free symmetric star with 239 neighbours at vertex zero. -/
def excessiveGraph (i j : Fin 240) : Bool :=
  decide ((i = 0 ∧ j ≠ 0) ∨ (j = 0 ∧ i ≠ 0))

theorem excessive_graph_loop_free : ∀ i, excessiveGraph i i = false := by
  intro i
  simp [excessiveGraph]

theorem excessive_graph_symmetric :
    ∀ i j, excessiveGraph i j = excessiveGraph j i := by
  intro i j
  simp only [excessiveGraph, or_comm]

theorem excessive_graph_degree_zero : degree excessiveGraph 0 = 239 := by
  have he : degree excessiveGraph 0 = ∑ j : Fin 240, if j = 0 then 0 else 1 := by
    apply Finset.sum_congr rfl
    intro j _
    by_cases hj : j = 0 <;> simp [excessiveGraph, hj]
  rw [he]
  have hf : (Finset.univ.filter (fun j : Fin 240 => ¬ j = 0)) =
      Finset.univ.erase 0 := by ext j; simp [and_comm]
  simp only [Finset.sum_ite, Finset.sum_const_zero, zero_add, Finset.sum_const,
    smul_eq_mul, mul_one]
  rw [hf]
  norm_num

theorem excessive_graph_degree_fails : ¬ (∀ i, degree excessiveGraph i ≤ 6) := by
  intro h
  have h0 := h 0
  rw [excessive_graph_degree_zero] at h0
  norm_num at h0

#print axioms generator_symmetric
#print axioms hermitian_H
#print axioms norm_H_eq
#print axioms norm_H_le_three
#print axioms graph_evolution
#print axioms norm_U_mul
#print axioms norm_U_mul_le_one
#print axioms empty_graph_premises
#print axioms empty_graph_evolution
#print axioms edge_graph_nonempty
#print axioms edge_graph_premises
#print axioms edge_graph_evolution
#print axioms directed_graph_loop_free
#print axioms directed_graph_degree
#print axioms directed_graph_not_symmetric
#print axioms directed_graph_not_hermitian
#print axioms excessive_graph_loop_free
#print axioms excessive_graph_symmetric
#print axioms excessive_graph_degree_zero
#print axioms excessive_graph_degree_fails

end

end SourceLaw.ColourSingletGateway.GraphEvolution
