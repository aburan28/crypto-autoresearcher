import CryptoResearch.Endosweep.AlphaAdic
open CryptoResearch.Endosweep.AlphaAdic

def pts : List O := [((0 : Int), (0 : Int)), ((1 : Int), (0 : Int)), ((-1 : Int), (0 : Int)), ((7 : Int), (0 : Int)), ((-7 : Int), (0 : Int)), ((88 : Int), (0 : Int)), ((-88 : Int), (0 : Int)), ((87 : Int), (0 : Int)), ((-2 : Int), (2 : Int)), ((3 : Int), (-5 : Int)), ((100 : Int), (1 : Int)), ((-1000 : Int), (37 : Int)), ((123456 : Int), (-7890 : Int)), ((-98765 : Int), (4321 : Int)), ((5 : Int), (1 : Int)), ((-50 : Int), (-50 : Int)), ((175 : Int), (0 : Int)), ((52 : Int), (0 : Int)), ((53 : Int), (0 : Int)), ((-53 : Int), (0 : Int)), ((-320874 : Int), (-5057 : Int)), ((-171996 : Int), (-8418 : Int)), ((-848091 : Int), (7559 : Int)), ((-802595 : Int), (1982 : Int)), ((222195 : Int), (-8100 : Int)), ((907787 : Int), (6627 : Int)), ((-549746 : Int), (-8772 : Int)), ((-819756 : Int), (4209 : Int)), ((-123030 : Int), (-7711 : Int)), ((-495294 : Int), (-7028 : Int)), ((155629 : Int), (3910 : Int)), ((-876037 : Int), (8528 : Int)), ((-740369 : Int), (-2685 : Int)), ((322518 : Int), (9103 : Int)), ((987489 : Int), (-7973 : Int)), ((210272 : Int), (9187 : Int)), ((-168101 : Int), (-8376 : Int)), ((-536358 : Int), (-8474 : Int)), ((167410 : Int), (-5637 : Int)), ((-392646 : Int), (3734 : Int)), ((-697476 : Int), (7717 : Int)), ((-752972 : Int), (8707 : Int)), ((-353067 : Int), (8358 : Int)), ((711541 : Int), (-4078 : Int)), ((-783877 : Int), (9057 : Int)), ((197902 : Int), (-3844 : Int)), ((-219026 : Int), (-6808 : Int)), ((148703 : Int), (-7943 : Int)), ((183566 : Int), (-8047 : Int)), ((298157 : Int), (-3252 : Int))]

-- Python-equivalent output lines: "D alpha z digit quotient"
def fmt (D : Int) (al : O) (z d q : O) : String :=
  s!"{D} ({al.1}, {al.2}) ({z.1}, {z.2}) ({d.1}, {d.2}) ({q.1}, {q.2})"

#eval IO.println (String.intercalate "\n" (pts.map fun z => fmt (-619) (4,1) z (digit1 1 155 4 z) (step1 1 155 4 z)))
#eval IO.println (String.intercalate "\n" (pts.map fun z => fmt (-339) (4,1) z (digit1 1 85 4 z) (step1 1 85 4 z)))
#eval IO.println (String.intercalate "\n" (pts.map fun z => fmt (-339) (1,4) z (digitInt 1365 341 z) (stepInt 1 85 (1,4) 1365 341 z)))

-- Orbit lengths (k with T^[k] z = 0) for the first 12 points
def orbitLen (T : O → O) : Nat → O → Option Nat
  | 0, _ => none
  | f + 1, z => if z = (0, 0) then some 0 else (orbitLen T f (T z)).map (· + 1)
#eval (pts.take 12).map (orbitLen (step1 1 155 4) 100)
#eval (pts.take 12).map (orbitLen (step1 1 85 4) 100)
#eval orbitLen (stepInt 1 85 (1,4) 1365 341) 50 (-2, 2)
