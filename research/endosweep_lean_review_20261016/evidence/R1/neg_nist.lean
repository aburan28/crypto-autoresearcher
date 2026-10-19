/-
Exact CM discriminants of the NIST / SP 800-186 curves, and B-571's bound.

Source:  research/endosweep_nist_20261006/README.md ("What is checked on every
         curve" item 2, the Results table, findings 3 and 4, and the "Lean
         verification" section); harness/endosweep/nist.py.
Targets: formal/targets/endosweep-nist-exact-discriminants.yaml
         formal/targets/endosweep-nist-finding3-bounds.yaml
         formal/targets/endosweep-nist-koblitz-discriminants.yaml
         formal/targets/endosweep-nist-b571-bound.yaml

GENERATED: the data blocks were written by a script from
research/endosweep_nist_20261006/nist.json and factorizations.jsonl (the
script re-derives every number and refuses to write on any mismatch).  The
definitions and proofs around them are hand-written.

WHAT IS CERTIFIED (unconditionally, by kernel arithmetic):
  * t² − 4q = D_K·f² for every curve with an exact D_K;
  * 4q − t² = ∏ pᵢ^eᵢ, the factorisation certificate, multiplied back;
  * D_K = −core or −4·core with core = ∏ of the odd-exponent pᵢ, and the
    congruence that makes it a discriminant (exactly `nist.exact_discriminant`);
  * min_nonscalar_degree(D_K) equals the value nist.json reports;
  * every odd-exponent factor below 10^8 is prime (trial division in Lean).
CONDITIONAL on the primality of the odd-exponent factors above 10^8 (listed
per curve in `largePrimes`; proven by PARI `isprime`, NOT by Lean): D_K is a
fundamental discriminant.
B-571: CONDITIONAL on the primality of its two large known factors and on the
harness's trial division of the cofactor C below 10^7 (both explicit
hypotheses): |D_K| ≥ 4.11·10^49 and every non-scalar norm ≥ that / 4.

NOT CERTIFIED: primality of any factor above 10^8; that C has no factor below
10^7; any elliptic-curve fact (that t is the trace of the curve, that End(E)
sits in the order of discriminant D_K, deg = norm); uniqueness of the
fundamental discriminant in a square class.
-/
import CryptoResearch.Endosweep.Discriminant

namespace R1Neg.NistCertificates

open CryptoResearch.Endosweep.Discriminant

/-- `noDivBelow p r` is true when no `d` with `2 ≤ d < r` divides `p`. -/
def noDivBelow (p : Nat) : Nat → Bool
  | 0 => true
  | d + 1 => (d < 2 || p % d != 0) && noDivBelow p d

theorem noDivBelow_spec {p : Nat} : ∀ r, noDivBelow p r = true → ∀ d, d < r → 2 ≤ d → p % d ≠ 0
  | 0, _, d, hd, _ => absurd hd (Nat.not_lt_zero d)
  | r + 1, h, d, hd, h2 => by
    simp only [noDivBelow, Bool.and_eq_true, Bool.or_eq_true, decide_eq_true_eq,
      bne_iff_ne, ne_eq] at h
    by_cases hdr : d = r
    · subst hdr
      rcases h.1 with h1 | h1
      · omega
      · exact h1
    · exact noDivBelow_spec r h.2 d (by omega) h2

/-- A prime proved by trial division: `p < r²` and no `d ∈ [2, r)` divides `p`. -/
theorem isPrimeNat_of_noDivBelow {p r : Nat} (h2 : 2 ≤ p) (hr : p < r * r)
    (h : noDivBelow p r = true) : IsPrimeNat p :=
  isPrimeNat_of_trial r h2 hr (noDivBelow_spec r h)

/-- One curve whose `4q − t²` is completely factored. -/
structure FactoredCert where
  q : Int
  t : Int
  DK : Int
  f : Int
  /-- nist.json `exact.min_nonscalar_degree` -/
  deg : Int
  /-- the factorisation certificate `[(p, e)]` of `4q − t²` -/
  factors : List (Nat × Nat)
  /-- the odd-exponent primes below 10^8, each with a trial-division bound `r`, `p < r²` -/
  smallPrimes : List (Nat × Nat)
  /-- the odd-exponent primes above 10^8 (primality from PARI, a hypothesis here) -/
  largePrimes : List Nat

/-- The odd-exponent primes, small then large (ascending, as in the certificate). -/
def FactoredCert.oddPrimes (c : FactoredCert) : List Nat :=
  c.smallPrimes.map (·.1) ++ c.largePrimes

/-- The closed arithmetic checked for one factored curve. -/
abbrev FactoredCert.Holds (c : FactoredCert) : Prop :=
  c.t ^ 2 - 4 * c.q = c.DK * c.f ^ 2 ∧
  4 * c.q - c.t ^ 2 = ((c.factors.map (fun pe => pe.1 ^ pe.2)).prod : Nat) ∧
  (c.factors.filter (fun pe => pe.2 % 2 == 1)).map (·.1) = c.oddPrimes ∧
  c.oddPrimes.Nodup ∧
  ((c.DK = -(c.oddPrimes.prod : Int) ∧ c.DK % 4 = 1) ∨
    (c.DK = -4 * (c.oddPrimes.prod : Int) ∧
      ((-(c.oddPrimes.prod : Int)) % 4 = 2 ∨ (-(c.oddPrimes.prod : Int)) % 4 = 3))) ∧
  IsDisc c.DK ∧
  minNonscalarDegree c.DK = c.deg ∧
  (∀ pr ∈ c.smallPrimes, 2 ≤ pr.1 ∧ pr.1 < pr.2 * pr.2 ∧ noDivBelow pr.1 pr.2 = true)

/-- One Koblitz curve, whose `D_K` the scan found without factoring. -/
structure ScanCert where
  q : Int
  t : Int
  DK : Int
  f : Int
  deg : Int

abbrev ScanCert.Holds (c : ScanCert) : Prop :=
  c.t ^ 2 - 4 * c.q = c.DK * c.f ^ 2 ∧ c.DK = -7 ∧ minNonscalarDegree c.DK = c.deg

/-- nist/P-192: `D_K = −core`, `f = 1`. -/
def P192 : FactoredCert where
  q := 6277101735386680763835789423207666416083908700390324961279
  t := 31607402316713927207482677199
  DK := -24109379060336110122544161233113975664949272517896865359515
  f := 1
  deg := 6027344765084027530636040308278493916237318129474216339879
  factors := [(5, 1), (11, 1), (31, 1), (14140398275856956083603613626459809774163796198179979683, 1)]
  smallPrimes := [(5, 3), (11, 4), (31, 6)]
  largePrimes := [14140398275856956083603613626459809774163796198179979683]

/-- nist/P-224: `D_K = −core`, `f = 3`. -/
def P224 : FactoredCert where
  q := 26959946667150639794667015087019630673557916260026308143510066298881
  t := 4733100108545601916421827343930821
  DK := -9493061114565352281698673660738078664961855212656825491744070162387
  f := 3
  deg := 2373265278641338070424668415184519666240463803164206372936017540598
  factors := [(3, 3), (29, 1), (79, 1), (7523, 1), (40927, 1), (11549194661, 1), (388425074903852603481408727235725774844022299, 1)]
  smallPrimes := [(3, 2), (29, 6), (79, 9), (7523, 87), (40927, 203)]
  largePrimes := [11549194661, 388425074903852603481408727235725774844022299]

/-- nist/P-256: `D_K = −core`, `f = 1`. -/
def P256 : FactoredCert where
  q := 115792089210356248762697446949407573530086143415290314195533631308867097853951
  t := 89188191154553853111372247798585809583
  DK := -455213823400003756884736869668539463648899917731097708475249543966132856781915
  f := 1
  deg := 113803455850000939221184217417134865912224979432774427118812385991533214195479
  factors := [(3, 1), (5, 1), (456597257999, 1), (1428624589419343516204097, 1), (46523541035814968339936406074986559003387, 1)]
  smallPrimes := [(3, 2), (5, 3)]
  largePrimes := [456597257999, 1428624589419343516204097, 46523541035814968339936406074986559003387]

/-- nist/P-384: `D_K = −core`, `f = 1`. -/
def P384 : FactoredCert where
  q := 39402006196394479212279040100143613805079739270465446667948293404245721771496870329047266088258938001861606973112319
  t := 1388124618062372383606759648309780106643088307173319169677
  DK := -155681134830307109642776504688282010728208281558659670869973287018687614232295158412465272949685257139190903176164947
  f := 1
  deg := 38920283707576777410694126172070502682052070389664917717493321754671903558073789603116318237421314284797725794041237
  factors := [(17299349, 1), (295429921339288635355502201959, 1), (30461532566489734432033897907025322605647670983785646081730729521647935009277217, 1)]
  smallPrimes := [(17299349, 4160)]
  largePrimes := [295429921339288635355502201959, 30461532566489734432033897907025322605647670983785646081730729521647935009277217]

/-- nist/P-521: `D_K = −core`, `f = 1`. -/
def P521 : FactoredCert where
  q := 6864797660130609714981900799081393217269435300143305409394463459185543183397656052122559640661454554977296311391480858037121987999716643812574028291115057151
  t := 657877501894328237357444332315020117536923257219387276263472201219398408051703
  DK := -27026387833023717006394879558010661621480271913819890964334078415620839627602227167727248383966407215164608200560037642817351611358118291378068537384139028395
  f := 1
  deg := 6756596958255929251598719889502665405370067978454972741083519603905209906900556791931812095991601803791152050140009410704337902839529572844517134346034757099
  factors := [(5, 1), (8000067766243453, 1), (1173758523082355533, 1), (41556388089068586871, 1), (100158966103874728681, 1), (138298652747358842965743345485413771865912754372429546592626819314973080829589786121, 1)]
  smallPrimes := [(5, 3)]
  largePrimes := [8000067766243453, 1173758523082355533, 41556388089068586871, 100158966103874728681, 138298652747358842965743345485413771865912754372429546592626819314973080829589786121]

/-- nist/B-163: `D_K = −core`, `f = 1`. -/
def B163 : FactoredCert where
  q := 11692013098647223345629478661730264157247460343808
  t := -6224022517221266226059365
  DK := -8029596099711546146978756026683092613973337172007
  f := 1
  deg := 2007399024927886536744689006670773153493334293002
  factors := [(1433, 1), (1922119, 1), (961548010411020239, 1), (3031770092835576249319, 1)]
  smallPrimes := [(1433, 38), (1922119, 1387)]
  largePrimes := [961548010411020239, 3031770092835576249319]

/-- nist/B-233: `D_K = −core`, `f = 1`. -/
def B233 : FactoredCert where
  q := 13803492693581127574869511724554050904902217944340773110325048447598592
  t := -206777407530349254000433718821372333
  DK := -12457074509352373925019593172898708314326469539767915835599496372531479
  f := 1
  deg := 3114268627338093481254898293224677078581617384941978958899874093132870
  factors := [(7, 1), (607, 1), (221912282681, 1), (706663193591, 1), (18695432581586757253171803892087928378926801, 1)]
  smallPrimes := [(7, 3), (607, 25)]
  largePrimes := [221912282681, 706663193591, 18695432581586757253171803892087928378926801]

/-- nist/B-283: `D_K = −core`, `f = 1`. -/
def B283 : FactoredCert where
  q := 15541351137805832567355695254588151253139254712417116170014499277911234281641667985408
  t := 2863663306391796106224371145726066910599667
  DK := -53964837018848536367612457123618193214948115634659033415381700110159762294769131430743
  f := 1
  deg := 13491209254712134091903114280904548303737028908664758353845425027539940573692282857686
  factors := [(1261652919337, 1), (448233496785705607, 1), (24441947552501608232432737, 1), (3904189206249251432380340703721, 1)]
  smallPrimes := []
  largePrimes := [1261652919337, 448233496785705607, 24441947552501608232432737, 3904189206249251432380340703721]

/-- nist/B-409: `D_K = −core`, `f = 1`. -/
def B409 : FactoredCert where
  q := 1322111937580497197903830616065542079656809365928562438569297590548811582472622691650378420879430569695182424050046716608512
  t := -6059503967182126918765909026644927652236777310526686418445029
  DK := -5251730161993692856952770269064997058983354908897019759241341697753910111464686436404493840542615167498371264016156571623207
  f := 1
  deg := 1312932540498423214238192567266249264745838727224254939810335424438477527866171609101123460135653791874592816004039142905802
  factors := [(274463242236170470633, 1), (19134548288527020978282691313128589290087578301686289306255632930154349088913119355866632515473568430479, 1)]
  smallPrimes := []
  largePrimes := [274463242236170470633, 19134548288527020978282691313128589290087578301686289306255632930154349088913119355866632515473568430479]

/-- other/Curve25519: `D_K = −4·core`, `f = 2`. -/
def Curve25519 : FactoredCert where
  q := 57896044618658097711785492504343953926634992332820282019728792003956564819949
  t := -221938542218978828286815502327069187962
  DK := -45581865488086735760375465490143625275457651809622790057958535113426043391588
  f := 2
  deg := 11395466372021683940093866372535906318864412952405697514489633778356510847897
  factors := [(2, 4), (16451, 1), (8312956054562778877481, 1), (83326725728999296701078628838522133333655224556987, 1)]
  smallPrimes := [(16451, 129)]
  largePrimes := [8312956054562778877481, 83326725728999296701078628838522133333655224556987]

/-- other/Ed25519 (same q and t as other/Curve25519): `D_K = −4·core`, `f = 2`. -/
def Ed25519 : FactoredCert where
  q := 57896044618658097711785492504343953926634992332820282019728792003956564819949
  t := -221938542218978828286815502327069187962
  DK := -45581865488086735760375465490143625275457651809622790057958535113426043391588
  f := 2
  deg := 11395466372021683940093866372535906318864412952405697514489633778356510847897
  factors := [(2, 4), (16451, 1), (8312956054562778877481, 1), (83326725728999296701078628838522133333655224556987, 1)]
  smallPrimes := [(16451, 129)]
  largePrimes := [8312956054562778877481, 83326725728999296701078628838522133333655224556987]

/-- other/Curve448: `D_K = −core`, `f = 2`. -/
def Curve448 : FactoredCert where
  q := 726838724295606890549323807888004534353641360687318060281490199180612328166730772686396383698676545930088884461843637361053498018365439
  t := 28312320572429821613362531907042076847709625476988141958474579766324
  DK := -526441850246598665100130500130299249884327037339362573644758821004312655096754090084837687027570936497061571295914040961206462407247195
  f := 2
  deg := 131610462561649666275032625032574812471081759334840643411189705251078163774188522521209421756892734124265392823978510240301615601811799
  factors := [(2, 2), (5, 1), (7, 1), (15041195721331390431432300003722835710980772495410359246993109171551790145621545430995362486502026757058902037026115456034470354492777, 1)]
  smallPrimes := [(5, 3), (7, 3)]
  largePrimes := [15041195721331390431432300003722835710980772495410359246993109171551790145621545430995362486502026757058902037026115456034470354492777]

/-- other/Ed448 (same q and t as other/Curve448): `D_K = −core`, `f = 2`. -/
def Ed448 : FactoredCert where
  q := 726838724295606890549323807888004534353641360687318060281490199180612328166730772686396383698676545930088884461843637361053498018365439
  t := 28312320572429821613362531907042076847709625476988141958474579766324
  DK := -526441850246598665100130500130299249884327037339362573644758821004312655096754090084837687027570936497061571295914040961206462407247195
  f := 2
  deg := 131610462561649666275032625032574812471081759334840643411189705251078163774188522521209421756892734124265392823978510240301615601811799
  factors := [(2, 2), (5, 1), (7, 1), (15041195721331390431432300003722835710980772495410359246993109171551790145621545430995362486502026757058902037026115456034470354492777, 1)]
  smallPrimes := [(5, 3), (7, 3)]
  largePrimes := [15041195721331390431432300003722835710980772495410359246993109171551790145621545430995362486502026757058902037026115456034470354492777]

/-- other/Ed448-Goldilocks: `D_K = −core`, `f = 2`. -/
def Ed448Goldilocks : FactoredCert where
  q := 726838724295606890549323807888004534353641360687318060281490199180612328166730772686396383698676545930088884461843637361053498018365439
  t := 28312320572429821613362531907042076847709625476988141958474579766324
  DK := -526441850246598665100130500130299249884327037339362573644758821004312655096754090084837687027570936497061571295914040961206462407247195
  f := 2
  deg := 131610462561649666275032625032574812471081759334840643411189705251078163774188522521209421756892734124265392823978510240301615601811799
  factors := [(2, 2), (5, 1), (7, 1), (15041195721331390431432300003722835710980772495410359246993109171551790145621545430995362486502026757058902037026115456034470354492777, 1)]
  smallPrimes := [(5, 3), (7, 3)]
  largePrimes := [15041195721331390431432300003722835710980772495410359246993109171551790145621545430995362486502026757058902037026115456034470354492777]

/-- Every curve whose `4q − t²` is completely factored (nist.json `exact.how`
= "complete factorisation of 4q - t^2 into primes"). -/
def factoredCerts : List FactoredCert :=
  [P192, P224, P256, P384, P521, B163, B233, B283, B409, Curve25519, Ed25519, Curve448, Ed448, Ed448Goldilocks]

/-- nist/K-163: found by the scan, `t² − 4q = −7·f²`. -/
def K163 : ScanCert where
  q := 11692013098647223345629478661730264157247460343808
  t := -4845466632539410776804317
  DK := -7
  f := 1824026374634505274957943
  deg := 2

/-- nist/K-233: found by the scan, `t² − 4q = −7·f²`. -/
def K233 : ScanCert where
  q := 13803492693581127574869511724554050904902217944340773110325048447598592
  t := -137381546011108235394987299651366779
  DK := -7
  f := 72051847988516734697809995873370769
  deg := 2

/-- nist/K-283: found by the scan, `t² − 4q = −7·f²`. -/
def K283 : ScanCert where
  q := 15541351137805832567355695254588151253139254712417116170014499277911234281641667985408
  t := 7777244870872830999287791970962823977569917
  DK := -7
  f := 489878522800087734083485536590018444665943
  deg := 2

/-- nist/K-409: found by the scan, `t² − 4q = −7·f²`. -/
def K409 : ScanCert where
  q := 1322111937580497197903830616065542079656809365928562438569297590548811582472622691650378420879430569695182424050046716608512
  t := 10457288737315625927447685387048320737638796957687575791173829
  DK := -7
  f := 27200558982140686235006970440600674058217108588553475783236049
  deg := 2

/-- nist/K-571: found by the scan, `t² − 4q = −7·f²`. -/
def K571 : ScanCert where
  q := 7729075046034516689390703781863974688597854659412869997314470502903038284579120849072387533163845155924927232063004354354730157322085975311485817346934161497393961629646848
  t := -148380926981691413899619140297051490364542574180493936232912339534208516828973111459843
  DK := -7
  f := 35655896511340624687810845487372082980344185179452596885179918179218090432562595510057
  deg := 2

/-- The Koblitz curves, whose `D_K = −7` the small-discriminant scan found. -/
def scanCerts : List ScanCert :=
  [K163, K233, K283, K409, K571]

/-- The closed arithmetic of every factored curve, checked by the kernel. -/
theorem factored_holds : ∀ c ∈ factoredCerts, c.Holds := by decide +kernel

/-- The closed arithmetic of every Koblitz curve, checked by the kernel. -/
theorem scan_holds : ∀ c ∈ scanCerts, c.Holds := by decide +kernel

/-- **Exact discriminants of the NIST curves** (README "What is checked" item 2
and finding 3).  For P-192, P-224, P-256, P-384, P-521, B-163, B-233, B-283,
B-409, Curve25519 = Ed25519 and Curve448 = Ed448 = Ed448-Goldilocks:
`t² − 4q = D_K·f²`; `4q − t²` is the product of the certificate's prime
powers; `D_K` is a discriminant built from the odd-exponent primes exactly as
`nist.exact_discriminant` builds it; `min_nonscalar_degree(D_K)` is the value
nist.json reports; and, IF the listed factors above 10^8 are prime (PARI
`isprime`; not proved here), `D_K` is a fundamental discriminant. -/
theorem exact_discriminants :
    ∀ c ∈ factoredCerts,
      c.t ^ 2 - 4 * c.q = c.DK * c.f ^ 2 ∧
      4 * c.q - c.t ^ 2 = ((c.factors.map (fun pe => pe.1 ^ pe.2)).prod : Nat) ∧
      IsDisc c.DK ∧
      minNonscalarDegree c.DK = c.deg ∧
      ((∀ p ∈ c.largePrimes, IsPrimeNat p) → IsFundamental c.DK) := by
  intro c hc
  obtain ⟨h1, h2, _, hnd, hD, hdisc, hdeg, hsmall⟩ := factored_holds c hc
  refine ⟨h1, h2, hdisc, hdeg, fun hlarge => isFundamental_of_primes c.oddPrimes hnd ?_ c.DK hD⟩
  intro p hp
  simp only [FactoredCert.oddPrimes, List.mem_append, List.mem_map] at hp
  rcases hp with ⟨pr, hpr, rfl⟩ | hp
  · obtain ⟨a, b, c'⟩ := hsmall pr hpr
    exact isPrimeNat_of_noDivBelow a b c'
  · exact hlarge p hp

/-- **The Koblitz curves' exact discriminant** (Results table, finding 1).  For
K-163 … K-571: `t² − 4q = −7·f²` with the nist.json `t` and `f`, `−7` is a
fundamental discriminant (unconditionally: 7 is prime), and
`min_nonscalar_degree(−7) = 2`. -/
theorem koblitz_discriminants :
    ∀ c ∈ scanCerts,
      c.t ^ 2 - 4 * c.q = c.DK * c.f ^ 2 ∧ IsFundamental c.DK ∧ minNonscalarDegree c.DK = 2 := by
  intro c hc
  obtain ⟨h1, h2, h3⟩ := scan_holds c hc
  refine ⟨h1, ?_, by rw [h2]; decide⟩
  rw [h2]
  exact isFundamental_of_primes [7] (by decide)
    (fun p hp => by
      simp only [List.mem_singleton] at hp
      subst hp
      exact isPrimeNat_of_noDivBelow (r := 3) (by decide) (by decide) (by decide))
    (-7) (.inl ⟨by decide, by decide⟩)

/-- **The sizes in finding 3.**  On P-192 … P-521, B-163 … B-409, Curve25519
(= Ed25519) and Curve448 (= Ed448, Ed448-Goldilocks): `2^162 ≤ |D_K| < 2^523`;
`min_nonscalar_degree(D_K) ≥ 2^160`, and `≥ 2^220` whenever `q ≥ 2^223` (a
field of 224 bits or more); the conductor is 1 on P-192, P-256, P-384, P-521
and B-163 … B-409, 3 on P-224 and 2 on Curve25519 and Curve448.  With
`exact_discriminants` (`deg = min_nonscalar_degree(D_K)`) and
`Discriminant.minNonscalarDegree_isLeast`, every element of the order of
discriminant `D_K` outside `Z` has norm at least these bounds. -/
theorem finding3_bounds :
    (∀ c ∈ factoredCerts,
      2 ^ 162 ≤ c.DK.natAbs ∧ c.DK.natAbs < 2 ^ 523 ∧ 2 ^ 160 ≤ c.deg ∧
        (2 ^ 223 ≤ c.q → 2 ^ 220 ≤ c.deg)) ∧
    [P192.f, P256.f, P384.f, P521.f, B163.f, B233.f, B283.f, B409.f] = [1, 1, 1, 1, 1, 1, 1, 1] ∧
    P224.f = 3 ∧ Curve25519.f = 2 ∧ Curve448.f = 2 := by
  decide +kernel

/-! ## B-571: bounded, not settled (README finding 4) -/

namespace B571

/-- B-571: `q = 2^571`. -/
def q : Int := 7729075046034516689390703781863974688597854659412869997314470502903038284579120849072387533163845155924927232063004354354730157322085975311485817346934161497393961629646848
/-- B-571: the trace of Frobenius. -/
def t : Int := 99534385013609758659469819150465382236412396452349171016760770327496674607579419075443
/-- The four primes the partial certificate proves (PARI `isprime`), each to exponent 1. -/
def knownPrimes : List Nat := [137, 1502689, 5608493523058319, 3563521804312876303]
/-- Their product. -/
def P : Nat := 4114483429456871116530091442859524338336201
/-- The 130-digit composite cofactor. -/
def C : Nat := 5106158949064929458195825244013686251303650244512648497717558074254289649451324237901292834252800885477933556954015766654535584543
/-- `⌊√C⌋`. -/
def rootC : Nat := 71457392543143704175424859184703064995806755028152289742573776115
/-- The trial-division bound. -/
def B : Nat := 10000000
/-- nist.json `bound.abs_D_K_at_least` (`= P·B`). -/
def absDKAtLeast : Nat := 41144834294568711165300914428595243383362010000000
/-- nist.json `bound.min_nonscalar_degree_at_least` (`= absDKAtLeast / 4`). -/
def degAtLeast : Nat := 10286208573642177791325228607148810845840502500000

/-- The partial certificate multiplies back: `4q − t² = P·C`, `P = ∏ knownPrimes`. -/
theorem product : 4 * q - t ^ 2 = ((P * C : Nat) : Int) ∧ knownPrimes.prod = P := by
  decide +kernel

/-- `gcd(P, C) = 1`: the known primes were divided out completely. -/
theorem coprime : Nat.Coprime P C := by decide +kernel

/-- `C` has 130 digits. -/
theorem C_digits : 10 ^ 129 ≤ C ∧ C < 10 ^ 130 := by decide +kernel

/-- `C` is not a perfect square: `⌊√C⌋² < C < (⌊√C⌋ + 1)²`. -/
theorem C_not_square : ∀ r, r * r ≠ C :=
  not_square_of_between (r := rootC) (by decide +kernel) (by decide +kernel)

/-- 137 and 1 502 689 are prime (trial division in Lean). -/
theorem small_known_primes : ∀ pr ∈ [(137, 12), (1502689, 1226)], IsPrimeNat pr.1 := by
  intro pr hpr
  have h : 2 ≤ pr.1 ∧ pr.1 < pr.2 * pr.2 ∧ noDivBelow pr.1 pr.2 = true := by
    revert pr; decide +kernel
  exact isPrimeNat_of_noDivBelow h.1 h.2.1 h.2.2

/-- The arithmetic facts behind the bound: `P·B` is nist.json's
`abs_D_K_at_least`, its quarter is `min_nonscalar_degree_at_least`, and they
exceed `2^164` and `2^162`. -/
theorem bound_values :
    knownPrimes.prod * B = absDKAtLeast ∧ absDKAtLeast = 4 * degAtLeast ∧
    2 ^ 164 < absDKAtLeast ∧ 2 ^ 162 < degAtLeast := by decide +kernel

/-- **B-571's discriminant bound.**  Assume (i) the two large known factors
`[5608493523058319, 3563521804312876303]` are prime (PARI `isprime`), and (ii) the cofactor `C` has no
divisor `d` with `1 < d < 10^7` (the harness's trial division).  Then for
EVERY factorisation `t² − 4q = D·f²` over the integers, `|D| ≥ P·10^7 =
41144834294568711165300914428595243383362010000000 > 2^164`, and if `D` is a
discriminant every non-scalar element of its order has norm at least
`10286208573642177791325228607148810845840502500000 > 2^162`.  This holds for
`D = D_K` and for the discriminant of every order containing `Z[π]`. -/
theorem abs_DK_lower_bound
    (hlarge : ∀ p ∈ [5608493523058319, 3563521804312876303], IsPrimeNat p)
    (htrial : ∀ d, 1 < d → d < B → ¬ d ∣ C)
    (D f : Int) (hDf : t ^ 2 - 4 * q = D * f ^ 2) :
    absDKAtLeast ≤ D.natAbs ∧ (IsDisc D → (degAtLeast : Int) ≤ minNonscalarDegree D) := by
  have hprime : ∀ p ∈ knownPrimes, IsPrimeNat p := by
    intro p hp
    have hs := small_known_primes
    have hsplit : p ∈ ([(137, 12), (1502689, 1226)] : List (Nat × Nat)).map (·.1) ∨ p ∈ [5608493523058319, 3563521804312876303] := by
      revert p; decide +kernel
    rcases hsplit with h | h
    · simp only [List.mem_map] at h
      obtain ⟨pr, hpr, rfl⟩ := h
      exact hs pr hpr
    · exact hlarge p h
  have hodd : ∀ p ∈ knownPrimes, ∃ e M, P = p ^ e * M ∧ ¬ p ∣ M ∧ e % 2 = 1 := by
    intro p hp
    have h : P = p ^ 1 * (P / p) ∧ ¬ p ∣ P / p := by revert p; decide +kernel
    exact ⟨1, P / p, h.1, h.2, rfl⟩
  have hnd : knownPrimes.Nodup := by decide +kernel
  obtain ⟨hb1, hb2⟩ := disc_bound_of_partial_factorisation q t D f P C B knownPrimes
    coprime (by decide +kernel) C_not_square htrial hnd hprime hodd product.1 hDf
  obtain ⟨hv1, hv2, _, _⟩ := bound_values
  refine ⟨hv1 ▸ hb1, fun hD => ?_⟩
  have := hb2 hD
  rw [hv1, hv2] at this
  have h4 : ((4 * degAtLeast : Nat) : Int) = 4 * (degAtLeast : Int) := by
    rw [Int.natCast_mul]; rfl
  omega

end B571

end R1Neg.NistCertificates
