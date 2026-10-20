import CryptoResearch.NCP.PointAction
import CryptoLean.Group.CyclicEncoding

set_option autoImplicit false
namespace CryptoResearch.NCP
variable {B n : ℕ} {A : Type*} [AddCommGroup A]

/-- The scalar model executes the actual point operations in the generated
subgroup, using the canonical encoding, with no unexplained embedding. -/
theorem word_action_canonical_encode (P : A) (hn : n • P = 0)
    (s : Fin B → ZMod n) (w : List (Letter B)) (x : ZMod n) :
    wordPointAction (fun i => CryptoLean.Cyclic.encode P hn (s i)) w
      (CryptoLean.Cyclic.encode P hn x) =
      CryptoLean.Cyclic.encode P hn (wordAction s w x) :=
  word_action_encode (CryptoLean.Cyclic.encode P hn) s w x

theorem canonical_word_action_iff (P : A) (ho : addOrderOf P = n)
    (s : Fin B → ZMod n) (w : List (Letter B)) (x y : ZMod n) :
    wordPointAction
      (fun i => CryptoLean.Cyclic.encode (n := n) P
        (by rw [← ho]; exact addOrderOf_nsmul_eq_zero P) (s i)) w
      (CryptoLean.Cyclic.encode (n := n) P
        (by rw [← ho]; exact addOrderOf_nsmul_eq_zero P) x) =
      CryptoLean.Cyclic.encode (n := n) P
        (by rw [← ho]; exact addOrderOf_nsmul_eq_zero P) y ↔ wordAction s w x = y := by
  rw [word_action_canonical_encode]
  exact (CryptoLean.Cyclic.encode_injective P ho).eq_iff
end CryptoResearch.NCP
