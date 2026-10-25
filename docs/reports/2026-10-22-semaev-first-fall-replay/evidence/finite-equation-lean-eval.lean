import CryptoResearch.Semaev.FiniteEquationSemantics
open CryptoResearch.Semaev.FiniteEquationSemantics
#eval (List.range 16).flatMap fun a => (List.range 16).map fun b => fieldMul a b
#eval (List.range 256).map semaevS3
