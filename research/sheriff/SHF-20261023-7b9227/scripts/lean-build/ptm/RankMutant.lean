import CryptoResearch.Semaev.BooleanParityFiniteCertificate
open CryptoResearch.Semaev.BooleanParityFiniteCertificate
-- Proves-too-much control: the same `decide` proof of a wrong rank must fail.
theorem rank_three_mutant : rank (rows 3) = 54 := by decide
theorem projected_rank_three_mutant : projectedRank 3 = 40 := by decide
