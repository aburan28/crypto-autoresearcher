import CryptoResearch.Endosweep.NistCertificates
open CryptoResearch.Endosweep.Discriminant CryptoResearch.Endosweep.NistCertificates
-- P-224's smallest "large" prime (PARI isprime): try the repo's own trial-division route.
set_option maxRecDepth 1000000 in
example : IsPrimeNat 11549194661 :=
  isPrimeNat_of_noDivBelow (r := 107468) (by decide) (by decide) (by decide +kernel)
