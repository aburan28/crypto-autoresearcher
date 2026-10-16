/-
The NIST Koblitz curves K-163 ... K-571 and their Frobenius ring Z[τ].

Source:  research/endosweep_nist_20261006/README.md, finding 1 and "What is
         checked on every curve" items 1 and 3; harness/endosweep/binary.py
         (`lucas_trace`, `Ztau`, `koblitz`).
Targets: formal/targets/endosweep-koblitz-ztau-order.yaml
         formal/targets/endosweep-koblitz-min-norm.yaml
         formal/targets/endosweep-koblitz-lucas-norm.yaml
         formal/targets/endosweep-koblitz-delta-norm.yaml
         formal/targets/endosweep-koblitz-curve-certificates.yaml

GENERATED in part: the per-curve constants at the end of this file were
written by a script from research/endosweep_nist_20261006/nist.json (t, f,
δ, λ) and std-curves commit 77fe6e3585ca2c2225b59d7df24b7c775437276f
(n, h; the commit nist.json records).  Everything above the data block is
hand-written.

WHAT IS PROVED.  Ring arithmetic in Z[τ] = Z[x]/(x² − μx + 2), modelled as
pairs `a + bτ`, and closed-form integer identities:
  * μ = ±1 gives discriminant μ² − 8 = −7, a fundamental discriminant, and
    Z[τ] is the order of discriminant −7 (an explicit ring isomorphism with
    Z[ω], ω² = ω − 2, the order `quadorder` uses for D = −7);
  * every a + bτ with b ≠ 0 has norm ≥ 2 = N(τ);
  * for every m, Tr(τ^m) = V_m (the Lucas sequence of `binary.lucas_trace`),
    N(τ^m) = 2^m and N(1 − τ^m) = 2^m + 1 − V_m;
  * if δ(τ − 1) = τ^m − 1 then N(δ)·N(τ − 1) = 2^m + 1 − V_m, N(τ − 1) = 3 − μ;
  * for the five published curves: h·n = 2^m + 1 − V_m, h = 3 − μ, t = V_m,
    δ(τ − 1) = τ^m − 1, N(δ) = n, t² − 4·2^m = −7 f² with f = |B| where
    τ^m = A + Bτ, and λ² − μλ + 2 ≡ 0 (mod n).

WHAT IS NOT PROVED.  That the Frobenius endomorphism of the curve satisfies
τ² − μτ + 2 = 0 and that #E(F_{2^m}) = N(1 − τ^m) (Weil / Hasse theory, and
the harness's point checks), that End(E) = Z[τ], that the order of a
fundamental discriminant is maximal, that n is prime, and that τ(G) = [λ]G.
These are elliptic-curve facts outside this file; what is certified is that
the published constants are consistent with them exactly.
-/
import CryptoResearch.Endosweep.Discriminant

namespace CryptoResearch.Endosweep.R1NegKoblitz

open CryptoResearch.Endosweep.Discriminant (IsFundamental isFundamental_of_primes
  isPrimeNat_of_trial minNonscalarDegree)

/-- An element `a + bτ` of `Z[τ]`. -/
structure Zt where
  a : Int
  b : Int
  deriving DecidableEq

namespace Zt

/-- `(a + bτ)(c + dτ)` with `τ² = μτ − 2` (`binary.Ztau.mul`). -/
def mul (μ : Int) (x y : Zt) : Zt :=
  ⟨x.a * y.a - 2 * x.b * y.b, x.a * y.b + x.b * y.a + μ * x.b * y.b⟩

/-- `a + bτ̄ = (a + μb) − bτ` (`binary.Ztau.conj`). -/
def conj (μ : Int) (x : Zt) : Zt := ⟨x.a + μ * x.b, -x.b⟩

/-- `N(a + bτ) = a² + μab + 2b²` (`binary.Ztau.norm`). -/
def norm (μ : Int) (x : Zt) : Int := x.a * x.a + μ * x.a * x.b + 2 * x.b * x.b

/-- `Tr(a + bτ) = 2a + μb`. -/
def trace (μ : Int) (x : Zt) : Int := 2 * x.a + μ * x.b

def sub (x y : Zt) : Zt := ⟨x.a - y.a, x.b - y.b⟩
def one : Zt := ⟨1, 0⟩
def tau : Zt := ⟨0, 1⟩

/-- `x^k`, by repeated multiplication. -/
def pow (μ : Int) (x : Zt) : Nat → Zt
  | 0 => one
  | k + 1 => mul μ (pow μ x k) x

end Zt

open Zt

/-- `(V_k, V_{k+1})` with `V_0 = 2`, `V_1 = μ`, `V_{k+1} = μV_k − 2V_{k−1}`. -/
def lucasPair (μ : Int) : Nat → Int × Int
  | 0 => (2, μ)
  | k + 1 => ((lucasPair μ k).2, μ * (lucasPair μ k).2 - 2 * (lucasPair μ k).1)

/-- The Lucas sequence `V_k = τ^k + τ̄^k` of `binary.lucas_trace`. -/
def lucasV (μ : Int) (k : Nat) : Int := (lucasPair μ k).1

theorem lucasV_zero (μ : Int) : lucasV μ 0 = 2 := rfl
theorem lucasV_one (μ : Int) : lucasV μ 1 = μ := rfl
theorem lucasV_succ_succ (μ : Int) (k : Nat) :
    lucasV μ (k + 2) = μ * lucasV μ (k + 1) - 2 * lucasV μ k := rfl

/-! ## The ring Z[τ] -/

/-- The norm is `x·x̄`. -/
theorem mul_conj (μ : Int) (x : Zt) : mul μ x (conj μ x) = ⟨norm μ x, 0⟩ := by
  simp only [mul, conj, norm, Zt.mk.injEq]; constructor <;> grind

/-- The norm is multiplicative. -/
theorem norm_mul (μ : Int) (x y : Zt) : norm μ (mul μ x y) = norm μ x * norm μ y := by
  simp only [norm, mul]; grind

/-- Discriminant of an element: `Tr(x)² − 4N(x) = (μ² − 8)·b²`.  For `x = τ`
this is the discriminant `μ² − 8` of `Z[τ]`; for `x = π = A + Bτ` it says
`Z[π]` has discriminant `(μ² − 8)·B²`, i.e. conductor `|B|` in `Z[τ]`. -/
theorem trace_sq_sub_four_norm (μ : Int) (x : Zt) :
    trace μ x * trace μ x - 4 * norm μ x = (μ * μ - 8) * (x.b * x.b) := by
  simp only [trace, norm]; grind

/-- **Z[τ] has discriminant −7** for both Koblitz signs `μ = ±1`. -/
theorem disc_tau (μ : Int) (hμ : μ = 1 ∨ μ = -1) :
    trace μ tau * trace μ tau - 4 * norm μ tau = -7 := by
  rcases hμ with rfl | rfl <;> decide

/-- −7 is a fundamental discriminant (7 is prime, by trial division). -/
theorem isFundamental_neg_seven : IsFundamental (-7) :=
  isFundamental_of_primes [7] (by decide)
    (fun p hp => by
      simp only [List.mem_singleton] at hp
      subst hp
      exact isPrimeNat_of_trial 3 (by decide) (by decide) (by decide))
    (-7) (.inl ⟨by decide, by decide⟩)

/-- The quadorder multiplication for `D = −7`: `ω² = ω − 2` (`quadorder.multiply`). -/
def mulOmega7 (x y : Zt) : Zt :=
  ⟨x.a * y.a - x.b * y.b * 2, x.a * y.b + y.a * x.b + x.b * y.b * 1⟩

/-- The change of basis `a + bτ ↦ (a + cb) + bω` with `τ = ω + c`, `c = (μ − 1)/2`. -/
def toOmega (μ : Int) (x : Zt) : Zt := ⟨x.a + (μ - 1) / 2 * x.b, x.b⟩

/-- **Z[τ] is the order of discriminant −7.**  For `μ = ±1` the change of
basis `τ ↦ ω + (μ − 1)/2` is a bijection `Z² → Z²` that carries the
multiplication of `Z[τ]` to that of `Z[ω]`, `ω² = ω − 2`, and the norm of
`Z[τ]` to `quadorder.norm (−7)`.  Since −7 is fundamental (above) that order
is the maximal order of Q(√−7); the maximality of the order of a fundamental
discriminant is classical and not formalised here. -/
theorem ztau_iso_order_neg_seven (μ : Int) (hμ : μ = 1 ∨ μ = -1) :
    (∀ x y : Zt, toOmega μ (mul μ x y) = mulOmega7 (toOmega μ x) (toOmega μ y)) ∧
    (∀ y : Zt, ∃ x, toOmega μ x = y) ∧
    (∀ x y : Zt, toOmega μ x = toOmega μ y → x = y) ∧
    (∀ x : Zt, norm μ x = Discriminant.norm (-7) (toOmega μ x).a (toOmega μ x).b) := by
  have h7 : Discriminant.omegaTrace (-7) = 1 ∧ Discriminant.omegaNorm (-7) = 2 := by decide
  rcases hμ with rfl | rfl
  · refine ⟨fun x y => ?_, fun y => ⟨y, ?_⟩, fun x y h => ?_, fun x => ?_⟩
    · simp only [toOmega, mul, mulOmega7, Zt.mk.injEq]; constructor <;> grind
    · obtain ⟨ya, yb⟩ := y; simp [toOmega]
    · obtain ⟨xa, xb⟩ := x; obtain ⟨ya, yb⟩ := y
      simp only [toOmega, Zt.mk.injEq] at h ⊢; omega
    · simp only [norm, Discriminant.norm, h7.1, h7.2, toOmega]; grind
  · refine ⟨fun x y => ?_, fun y => ⟨⟨y.a + y.b, y.b⟩, ?_⟩, fun x y h => ?_, fun x => ?_⟩
    · simp only [toOmega, mul, mulOmega7, Zt.mk.injEq]; constructor <;> grind
    · obtain ⟨ya, yb⟩ := y; simp only [toOmega, Zt.mk.injEq]; constructor <;> grind
    · obtain ⟨xa, xb⟩ := x; obtain ⟨ya, yb⟩ := y
      simp only [toOmega, Zt.mk.injEq] at h ⊢; omega
    · simp only [norm, Discriminant.norm, h7.1, h7.2, toOmega]; grind

/-- **The cheapest non-scalar element of Z[τ] has norm 2, attained by τ.**
For `μ = ±1` every `a + bτ` with `b ≠ 0` has norm at least 2, and `N(τ) = 2`;
this agrees with `min_nonscalar_degree(−7) = 2`. -/
theorem min_norm_nonscalar (μ : Int) (hμ : μ = 1 ∨ μ = -1) :
    (∀ x : Zt, x.b ≠ 0 → 2 ≤ norm μ x) ∧ norm μ tau = 2 ∧ minNonscalarDegree (-7) = 2 := by
  refine ⟨fun x hb => ?_, by rcases hμ with rfl | rfl <;> decide, by decide⟩
  obtain ⟨_, _, _, hn⟩ := ztau_iso_order_neg_seven μ hμ
  rw [hn x]
  have := (Discriminant.minNonscalarDegree_isLeast (D := -7) (by decide)).1
    (toOmega μ x).a (toOmega μ x).b (by simpa [toOmega] using hb)
  have h2 : minNonscalarDegree (-7) = 2 := by decide
  omega

/-! ## The Lucas sequence and the group order -/

/-- `τ^{k+2} = μτ^{k+1} − 2τ^k`, componentwise. -/
theorem pow_succ_succ (μ : Int) (k : Nat) :
    pow μ tau (k + 2) =
      ⟨μ * (pow μ tau (k + 1)).a - 2 * (pow μ tau k).a,
       μ * (pow μ tau (k + 1)).b - 2 * (pow μ tau k).b⟩ := by
  simp only [pow, mul, tau, Zt.mk.injEq]; constructor <;> grind

/-- `Tr(τ^k) = V_k`. -/
theorem trace_pow_tau (μ : Int) : ∀ k, trace μ (pow μ tau k) = lucasV μ k
  | 0 => by simp [trace, pow, one, lucasV, lucasPair]
  | 1 => by simp [trace, pow, one, tau, mul, lucasV, lucasPair]
  | k + 2 => by
    rw [lucasV_succ_succ, ← trace_pow_tau μ (k + 1), ← trace_pow_tau μ k, pow_succ_succ]
    simp only [trace]; grind

/-- `N(τ^k) = 2^k`. -/
theorem norm_pow_tau (μ : Int) : ∀ k, norm μ (pow μ tau k) = 2 ^ k
  | 0 => by simp [norm, pow, one]
  | k + 1 => by
    rw [pow, norm_mul, norm_pow_tau μ k, Int.pow_succ]
    simp [norm, tau]

/-- `N(1 − x) = 1 − Tr(x) + N(x)`. -/
theorem norm_one_sub (μ : Int) (x : Zt) : norm μ (sub one x) = 1 - trace μ x + norm μ x := by
  simp only [norm, sub, one, trace]; grind

/-- **The group-order formula.**  For every `m`,
`N(1 − τ^m) = 2^m + 1 − V_m`: the number `binary.koblitz` compares with
`h·n` is the norm of `1 − τ^m` in `Z[τ]`. -/
theorem norm_one_sub_tau_pow (μ : Int) (m : Nat) :
    norm μ (sub one (pow μ tau m)) = 2 ^ m + 1 - lucasV μ m := by
  rw [norm_one_sub, trace_pow_tau, norm_pow_tau]; omega

/-- `N(τ − 1) = 3 − μ`, which is `#E(F_2) = 2 + 1 − V_1`. -/
theorem norm_tau_sub_one (μ : Int) : norm μ (sub tau one) = 3 - μ := by
  simp only [norm, sub, tau, one]; grind

/-- **N(δ)·N(τ − 1) = #E.**  If `δ·(τ − 1) = τ^m − 1` then
`N(δ)·(3 − μ) = 2^m + 1 − V_m`. -/
theorem norm_delta (μ : Int) (m : Nat) (δ : Zt)
    (h : mul μ δ (sub tau one) = sub (pow μ tau m) one) :
    norm μ δ * (3 - μ) = 2 ^ m + 1 - lucasV μ m := by
  rw [← norm_tau_sub_one, ← norm_mul, h, ← norm_one_sub_tau_pow]
  simp only [norm, sub, one]; grind

/-! ## The five NIST Koblitz curves -/

/-- One Koblitz curve's published and derived constants. -/
structure KCert where
  m : Nat
  μ : Int
  /-- the prime order of the base point (std-curves `order`) -/
  n : Int
  /-- the cofactor (std-curves `cofactor`) -/
  h : Int
  /-- the trace of Frobenius, `#E = 2^m + 1 − t` (nist.json `t`) -/
  t : Int
  /-- the conductor of `Z[π]` in `Z[τ]` (nist.json `exact.f`) -/
  f : Int
  /-- `δ = (τ^m − 1)/(τ − 1)` (nist.json `tau.delta`) -/
  δ : Zt
  /-- the eigenvalue of `τ` on `⟨G⟩` (nist.json `tau.eigenvalue`) -/
  lam : Int

/-- Everything checked about one curve; closed integer arithmetic. -/
abbrev KCert.Holds (c : KCert) : Prop :=
  (c.μ = 1 ∨ c.μ = -1) ∧
  c.h = 3 - c.μ ∧
  c.h * c.n = 2 ^ c.m + 1 - lucasV c.μ c.m ∧
  c.t = lucasV c.μ c.m ∧
  mul c.μ c.δ (sub tau one) = sub (pow c.μ tau c.m) one ∧
  norm c.μ c.δ = c.n ∧
  c.f = (pow c.μ tau c.m).b.natAbs ∧
  c.t ^ 2 - 4 * 2 ^ c.m = -7 * c.f ^ 2 ∧
  (c.lam * c.lam - c.μ * c.lam + 2) % c.n = 0

/-- K-163: `m = 163`, `μ = 1`. -/
def K163 : KCert where
  m := 163
  μ := 1
  n := 5846006549323611672814741753598448348329118574063
  h := 2
  t := -4845466632539410776804317
  f := 1824026374634505274957943
  δ := ⟨1824026374634505274957943, 755360064476226375461594⟩
  lam := 5124886332546225921918603466361262992169187649242

/-- K-233: `m = 233`, `μ = -1`. -/
def K233 : KCert where
  m := 233
  μ := -1
  n := 3450873173395281893717377931138512760570940988862252126328087024741343
  h := 4
  t := -137381546011108235394987299651366779
  f := 72051847988516734697809995873370769
  δ := ⟨16332424505647875174294325944499003, 44192136247082304936052160908934886⟩
  lam := 2598851043790259083579160746211533789223151387669521214510026908255781

/-- K-283: `m = 283`, `μ = -1`. -/
def K283 : KCert where
  m := 283
  μ := -1
  n := 3885337784451458141838923813647037813284811733793061324295874997529815829704422603871
  h := 4
  t := 7777244870872830999287791970962823977569917
  f := 489878522800087734083485536590018444665943
  δ := ⟨-1821841587018185816301076608593201383225993, -1155860054909136775192281072591609913945968⟩
  lam := 1622537357594321742305829784866063775146998334908836481845747957062258441461142295062

/-- K-409: `m = 409`, `μ = -1`. -/
def K409 : KCert where
  m := 409
  μ := -1
  n := 330527984395124299475957654016385519914202341482140609642324395022880711289249191050673258457777458014096366590617731358671
  h := 4
  t := 10457288737315625927447685387048320737638796957687575791173829
  f := 27200558982140686235006970440600674058217108588553475783236049
  δ := ⟨-9414461929864078040613663956912248698963976386560262893602469, 8893048526138304097196653241844212679626566100996606444816790⟩
  lam := 95377454917350009852088261107010868232002917283647585598560304000289932291317179548226087991151495035569641628246841874340

/-- K-571: `m = 571`, `μ = -1`. -/
def K571 : KCert where
  m := 571
  μ := -1
  n := 1932268761508629172347675945465993672149463664853217499328617625725759571144780212268133978522706711834706712800825351461273674974066617311929682421617092503555733685276673
  h := 4
  t := -148380926981691413899619140297051490364542574180493936232912339534208516828973111459843
  f := 35655896511340624687810845487372082980344185179452596885179918179218090432562595510057
  δ := ⟨28181257617587697302952073702419851846049597250260334836933105338747606599102628987447, 31918577064464160995381459594895967413196891214856465861056511758982848515832612248752⟩
  lam := 1737617153452667100450620654361010136575696214949435748424058322350852003406707707278390660980311506772309793318508751262778482693856154191237912594889446307146732063445937

/-- K-163, K-233, K-283, K-409, K-571. -/
def koblitzCerts : List KCert := [K163, K233, K283, K409, K571]

/-- The closed arithmetic, checked by the kernel (GMP-backed `Nat`). -/
theorem koblitz_holds : ∀ c ∈ koblitzCerts, c.Holds := by decide +kernel

/-- **The Koblitz checks of README finding 1, as arithmetic.**  For each of
K-163, K-233, K-283, K-409 and K-571 with its published `n`, `h`:
`μ = ±1`; `h = 3 − μ = #E(F_2)`; `h·n = 2^m + 1 − V_m`; the trace `t` of
nist.json is `V_m`; `δ·(τ − 1) = τ^m − 1` and `N(δ) = n`;
`t² − 4·2^m = −7·f²` with `f = |B|`, `τ^m = A + Bτ`; and
`λ² − μλ + 2 ≡ 0 (mod n)`.  Consequently `N(1 − τ^m) = h·n` and
`N(δ)·N(τ − 1) = h·n`. -/
theorem koblitz_certificates :
    ∀ c ∈ koblitzCerts, c.Holds ∧
      norm c.μ (sub one (pow c.μ tau c.m)) = c.h * c.n ∧
      norm c.μ c.δ * norm c.μ (sub tau one) = c.h * c.n := by
  intro c hc
  have hh : c.Holds := koblitz_holds c hc
  refine ⟨hh, ?_, ?_⟩
  · rw [norm_one_sub_tau_pow, hh.2.2.1]
  · rw [norm_tau_sub_one, norm_delta c.μ c.m c.δ hh.2.2.2.2.1, hh.2.2.1]

end CryptoResearch.Endosweep.R1NegKoblitz
