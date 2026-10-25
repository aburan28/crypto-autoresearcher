import CryptoLean.Group.Torsion
import Mathlib.GroupTheory.OrderOfElement
import Mathlib.AlgebraicGeometry.EllipticCurve.Affine.Point

set_option autoImplicit false

namespace Retrospective.Transport

variable {A B : Type*} [AddCommGroup A] [AddCommGroup B]

/-- A certified reverse composition and coprime degree imply injectivity on
the specified finite subgroup. The homomorphisms are not geometric isogenies. -/
theorem injective_on_subgroup (S : AddSubgroup A) [Finite S]
    (f : A →+ B) (back : B →+ A) (d : ℕ)
    (hcoprime : (Nat.card S).Coprime d)
    (hdual : ∀ P : S, back (f P) = d • (P : A)) :
    Function.Injective (fun P : S => f P) := by
  intro P Q h
  have hscaled : d • P = d • Q := by
    apply Subtype.ext
    change d • (P : A) = d • (Q : A)
    rw [← hdual P, ← hdual Q]
    exact congrArg back h
  exact (Nat.Coprime.nsmul_right_bijective (G := S) hcoprime).1 hscaled

/-- Both directions of the DLP equivalence; injectivity is derived rather
than included as an unexplained property of a structure called Isogeny. -/
theorem dlog_transport_iff (S : AddSubgroup A) [Finite S]
    (f : A →+ B) (back : B →+ A) (d : ℕ)
    (hcoprime : (Nat.card S).Coprime d)
    (hdual : ∀ P : S, back (f P) = d • (P : A))
    (G Q : S) (k : ℤ) :
    k • f (G : A) = f (Q : A) ↔ k • G = Q := by
  constructor
  · intro h
    apply injective_on_subgroup S f back d hcoprime hdual
    simpa using h
  · intro h
    have := congrArg (fun P : S => f (P : A)) h
    simpa using this

/-- The same equivalence stated on Mathlib's actual elliptic-curve point
groups. Construction and duality of the maps remain explicit obligations. -/
theorem curve_dlog_transport_iff {K L : Type*} [Field K] [Field L]
    [DecidableEq K] [DecidableEq L]
    (E : WeierstrassCurve.Affine K) (E' : WeierstrassCurve.Affine L)
    (S : AddSubgroup E.Point) [Finite S]
    (f : E.Point →+ E'.Point) (back : E'.Point →+ E.Point) (d : ℕ)
    (hcoprime : (Nat.card S).Coprime d)
    (hdual : ∀ P : S, back (f P) = d • (P : E.Point))
    (G Q : S) (k : ℤ) :
    k • f (G : E.Point) = f (Q : E.Point) ↔ k • G = Q :=
  dlog_transport_iff S f back d hcoprime hdual G Q k

/-- A factor base in a homomorphism's range generates only elements in that
range, now using Mathlib's subgroup closure and actual group laws. -/
theorem closure_le_range (f : A →+ B) (base : Set B)
    (hbase : base ⊆ f.range) : AddSubgroup.closure base ≤ f.range :=
  (AddSubgroup.closure_le _).mpr hbase

theorem outside_range_not_in_closure (f : A →+ B) (base : Set B)
    (hbase : base ⊆ f.range) (Q : B) (hQ : Q ∉ f.range) :
    Q ∉ AddSubgroup.closure base :=
  fun h => hQ (closure_le_range f base hbase h)

end Retrospective.Transport
