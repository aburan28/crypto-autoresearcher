import CryptoResearch.Endosweep.SubgroupIndex
import CryptoResearch.Endosweep.ChainEigen
import CryptoResearch.Endosweep.AlphaAdic
import CryptoResearch.Endosweep.FrobeniusSplit
import CryptoResearch.Endosweep.Blinding

/-! R3 review scratch: satisfiability witnesses, Python cross-checks, axioms. -/

namespace R3

open CryptoResearch.Endosweep

-- (6) babai_unreduced_erases: hypotheses satisfiable on the secp256k1 lattice (blinding.py data)
def secpN : Int := 115792089237316195423570985008687907852837564279074904382605163141518161494337
def secpB : Fin 2 → Fin 2 → Int := fun i j =>
  match i.val, j.val with
  | 0, 0 => -64502973549206556628585045361533709077 | 0, _ => 303414439467246543595250775667605759171
  | _, 0 => 367917413016453100223835821029139468248 | _, _ => 64502973549206556628585045361533709077
def secpNum : Fin 2 → Int := fun i => if i.val = 0 then -64502973549206556628585045361533709077 else 303414439467246543595250775667605759171
def secpDen : Fin 2 → Int := fun i => if i.val = 0 then 115792089237316195423570985008687907852837564279074904382605163141518161494337 else 115792089237316195423570985008687907852837564279074904382605163141518161494337
def secpZ : Fin 2 → Int := fun i => secpN * secpNum i / secpDen i
example : ∀ i, 0 < secpDen i := by decide
example : ∀ i, secpN * secpNum i = secpDen i * secpZ i := by decide
example : ∀ j, Blinding.vsum (fun i => secpZ i * secpB i j) = if j = 0 then secpN else 0 := by decide
#check @Blinding.babai_unreduced_erases 1 secpNum secpDen secpZ secpB secpN (by decide) (by decide) (by decide)
-- decomposeUnreduced vs blinding.py decompose_unreduced on 8 K values
def decCases : List (Int × (Int × Int)) := [((-99975351838618605344563408231431084290384170793747231365789517683322007153626995 : Int), ((117489488081082368655562152841913267630 : Int), (127684169196001432051425593164899264194 : Int))), ((36824776880682116879277586197216215352470330716960089363490671348443112695825599 : Int), ((-2141968276875763062682589057224229663 : Int), (29594977528273186398107222137276621057 : Int))), ((83184193909902013759492328790433158032971117175617037434844855015998668774795357 : Int), ((-129988388339844690310145648212020826976 : Int), (-142369009896300259211089031969085872641 : Int))), ((-50546343039490558727144200454802578748055905854872087548560106772117672234661036 : Int), ((-105505246254534966540667560845773421141 : Int), (-53894615683831053805375632666596987434 : Int))), ((7527098771477218423998514128945355522186882581854963158103460451872906391985035 : Int), ((67126571806712698702149571067539421259 : Int), (58709431683854861160519775674742570673 : Int))), ((12345 : Int), ((12345 : Int), (0 : Int))), ((115792089237316195423570985008687907852837564279074904382605163141518161494336 : Int), ((-1 : Int), (0 : Int))), ((0 : Int), ((0 : Int), (0 : Int)))]
#eval decCases.all fun (K, (v0, v1)) =>
  Blinding.decomposeUnreduced secpNum secpDen secpB K 0 == v0 && Blinding.decomposeUnreduced secpNum secpDen secpB K 1 == v1

-- (7) blind_reconstructs: hypotheses satisfiable (n = 7, lambda = (1, 3), k = 1)
#check @Blinding.blind_reconstructs 2 2 7 1 (fun i => if i.val = 0 then 1 else 0) (fun i => if i.val = 0 then 1 else 3)
  (fun _ => 5) (fun j i => if j.val = 0 then (if i.val = 0 then 7 else 0) else (if i.val = 0 then -3 else 1))
  (by decide) (by decide)


end R3
