import CryptoResearch.Endosweep.SubgroupIndex
import CryptoResearch.Endosweep.ChainEigen
import CryptoResearch.Endosweep.AlphaAdic
import CryptoResearch.Endosweep.FrobeniusSplit
import CryptoResearch.Endosweep.Blinding

/-! R3 review scratch: satisfiability witnesses, Python cross-checks, axioms. -/

namespace R3

open CryptoResearch.Endosweep

-- (1) index_eq_minorGcd: hypothesis satisfiable
example : SubgroupIndex.minorGcd [((2 : Int), (0 : Int)), (0, 3)] ≠ 0 := by decide
example : SubgroupIndex.minorGcd [((2 : Int), (0 : Int)), (0, 3)] = 6 := by decide
#check SubgroupIndex.index_eq_minorGcd [((2 : Int), (0 : Int)), (0, 3)] (by decide)
-- a lattice where the gcd is not the abs det of any single pair: [(4,0),(0,6),(2,3)] -> 12? (index check)
#eval SubgroupIndex.minorGcd [((4 : Int), (0 : Int)), (0, 6), (2, 3)]

-- (2) ideal_index_eq_elementIndex: hypothesis satisfiable (CP6 data)
#check SubgroupIndex.ideal_index_eq_elementIndex 1 85 SubgroupIndex.CP6.βmem SubgroupIndex.CP6.πm1 (by decide)

-- elementIndex vs subgroup.py element_index on 36 random inputs (6 discriminants)
def eiCases : List (Int × Int × SubgroupIndex.V × SubgroupIndex.V × Nat) := [
  ((1 : Int), (1 : Int), ((-37 : Int), (386 : Int)), ((73 : Int), (377 : Int)), (1 : Nat)),
  ((1 : Int), (1 : Int), ((446 : Int), (299 : Int)), ((-24 : Int), (-38 : Int)), (1 : Nat)),
  ((1 : Int), (1 : Int), ((20 : Int), (375 : Int)), ((101 : Int), (-306 : Int)), (1 : Nat)),
  ((1 : Int), (1 : Int), ((-311 : Int), (323 : Int)), ((24 : Int), (-13 : Int)), (1 : Nat)),
  ((1 : Int), (1 : Int), ((144 : Int), (128 : Int)), ((312 : Int), (-310 : Int)), (4 : Nat)),
  ((1 : Int), (1 : Int), ((-404 : Int), (-43 : Int)), ((-190 : Int), (-355 : Int)), (1 : Nat)),
  ((0 : Int), (1 : Int), ((-408 : Int), (51 : Int)), ((329 : Int), (411 : Int)), (1 : Nat)),
  ((0 : Int), (1 : Int), ((210 : Int), (149 : Int)), ((-458 : Int), (109 : Int)), (1 : Nat)),
  ((0 : Int), (1 : Int), ((-95 : Int), (487 : Int)), ((-37 : Int), (169 : Int)), (2 : Nat)),
  ((0 : Int), (1 : Int), ((256 : Int), (130 : Int)), ((165 : Int), (-339 : Int)), (2 : Nat)),
  ((0 : Int), (1 : Int), ((138 : Int), (-485 : Int)), ((351 : Int), (41 : Int)), (1 : Nat)),
  ((0 : Int), (1 : Int), ((-436 : Int), (-440 : Int)), ((-464 : Int), (-306 : Int)), (4 : Nat)),
  ((1 : Int), (85 : Int), ((400 : Int), (-253 : Int)), ((114 : Int), (-470 : Int)), (1 : Nat)),
  ((1 : Int), (85 : Int), ((296 : Int), (-25 : Int)), ((-166 : Int), (-49 : Int)), (3 : Nat)),
  ((1 : Int), (85 : Int), ((105 : Int), (362 : Int)), ((-300 : Int), (31 : Int)), (5 : Nat)),
  ((1 : Int), (85 : Int), ((-261 : Int), (155 : Int)), ((-199 : Int), (11 : Int)), (1 : Nat)),
  ((1 : Int), (85 : Int), ((-496 : Int), (178 : Int)), ((-413 : Int), (-32 : Int)), (1 : Nat)),
  ((1 : Int), (85 : Int), ((170 : Int), (-216 : Int)), ((-84 : Int), (64 : Int)), (4 : Nat)),
  ((1 : Int), (155 : Int), ((454 : Int), (360 : Int)), ((-415 : Int), (224 : Int)), (1 : Nat)),
  ((1 : Int), (155 : Int), ((-240 : Int), (-178 : Int)), ((276 : Int), (-265 : Int)), (1 : Nat)),
  ((1 : Int), (155 : Int), ((25 : Int), (-205 : Int)), ((-470 : Int), (-429 : Int)), (5 : Nat)),
  ((1 : Int), (155 : Int), ((76 : Int), (284 : Int)), ((-390 : Int), (-90 : Int)), (20 : Nat)),
  ((1 : Int), (155 : Int), ((-390 : Int), (366 : Int)), ((-203 : Int), (-105 : Int)), (1 : Nat)),
  ((1 : Int), (155 : Int), ((-432 : Int), (481 : Int)), ((-483 : Int), (367 : Int)), (1 : Nat)),
  ((1 : Int), (6 : Int), ((201 : Int), (-500 : Int)), ((-282 : Int), (-286 : Int)), (9 : Nat)),
  ((1 : Int), (6 : Int), ((449 : Int), (432 : Int)), ((-447 : Int), (-19 : Int)), (1 : Nat)),
  ((1 : Int), (6 : Int), ((-116 : Int), (225 : Int)), ((-94 : Int), (-71 : Int)), (2 : Nat)),
  ((1 : Int), (6 : Int), ((-426 : Int), (79 : Int)), ((144 : Int), (-297 : Int)), (6 : Nat)),
  ((1 : Int), (6 : Int), ((297 : Int), (191 : Int)), ((-224 : Int), (-156 : Int)), (2 : Nat)),
  ((1 : Int), (6 : Int), ((-411 : Int), (-182 : Int)), ((-160 : Int), (-485 : Int)), (1 : Nat)),
  ((0 : Int), (2 : Int), ((487 : Int), (-81 : Int)), ((276 : Int), (444 : Int)), (1 : Nat)),
  ((0 : Int), (2 : Int), ((-380 : Int), (-363 : Int)), ((-248 : Int), (223 : Int)), (2 : Nat)),
  ((0 : Int), (2 : Int), ((-397 : Int), (-489 : Int)), ((-439 : Int), (-24 : Int)), (1 : Nat)),
  ((0 : Int), (2 : Int), ((316 : Int), (-2 : Int)), ((-319 : Int), (198 : Int)), (1 : Nat)),
  ((0 : Int), (2 : Int), ((72 : Int), (-308 : Int)), ((-42 : Int), (21 : Int)), (2 : Nat)),
  ((0 : Int), (2 : Int), ((-305 : Int), (249 : Int)), ((287 : Int), (-366 : Int)), (1 : Nat))]
#eval eiCases.all fun (τ, n, b, g, r) => SubgroupIndex.elementIndex τ n [b, g] == r
#eval eiCases.length

end R3
