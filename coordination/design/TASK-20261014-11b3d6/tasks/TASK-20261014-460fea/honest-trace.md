# Honest trace and exact stopping point

`blocked_by: O1/CompleteBasisAtEndpoint`. No executable PKE trace exists.

Symbolic hand trace for one supported chain: `pp=(p,ell,L,E0,W0)`; choose actual outgoing kernels `K1,...,KL`, excluding the preceding dual after the first; form `phi_i` and `phi=phi_L o ... o phi_1`; put `E=canonical(E_L)` and `d=ell^L`. For `W0=(1,alpha2,alpha3,alpha4)`, compute `beta_i=phi alpha_i hat(phi)` for `i=2,3,4`. Each call is typed and integral, and `S=Z*1+Z*beta_2+Z*beta_3+Z*beta_4`. The next pseudocode line would be `W_E <- CompleteBasisAtEndpoint(pp,phi,W0)`. It has no supplied implementation or polynomial cost certificate; returning `(1,beta_2,beta_3,beta_4)` is incorrect because `S` has index `d^3`.

There is no next honest `Encrypt` line: `EdgeLabel` and `RingPotential` have no formulas. Consequently no message encoding, pad, ciphertext parser, `Decrypt`, actual-message equality, rejection or failure probability is defined. This trace records the first halted call, not a successful example. KeyGen's ephemeral path must be erased and cannot be silently added to `sk`.
