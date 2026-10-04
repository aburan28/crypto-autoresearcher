# Mathematical implementation notes

All formulas below implement the frozen `specification.yaml`; they are implementation deductions, not experimental observations.

For a monic polynomial `f(X)=X^k+a_{k-1}X^(k-1)+...+a_0` over `F_p`, `rabin_irreducibility_certificate` computes `X^(p^k) mod f` and, for each prime `ell | k`, computes `gcd(X^(p^(k/ell))-X,f)`. It accepts exactly when the first residue is `X` and every gcd is one. The certificate retains residues and gcds so review does not have to trust a boolean.

`PolynomialField` represents coefficients constant-first modulo the selected monic polynomial. `extension_sqrt` applies finite-field Tonelli--Shanks: with `p^k-1=2^s d`, it checks `a^((p^k-1)/2)=1`, obtains a bounded deterministic non-square, and performs the standard correction loop. It returns the lexicographically smaller of `y` and `-y`; a non-square produces no point rather than a substituted value.

For `E: y^2=x^3+Ax+B`, the affine group law uses `lambda=(3x_P^2+A)/(2y_P)` for doubling and `(y_Q-y_P)/(x_Q-x_P)` otherwise. The Miller routine evaluates `g_(P,Q)=ell_(P,Q)/v_(P+Q)` in the binary loop. A zero denominator raises `PairingPole`. For a public T and shift S, the code evaluates the quotient at `T+S` and `S`; it does not silently replace an exceptional value. The reduced Tate value is `f_(r,P)(T)^((p^k-1)/r)`.

The multiplicative and additive solvers use `m=ceil(sqrt(r))`, baby entries `0..m-1`, giant entries `0..m`, an exact candidate bound `<r`, and final verification. There is no library discrete-log call or full scalar table. The public timed request serializes Q and public fixture fields only; the label is constructed and retained by the verifier path.

The known-false controls are executable: a trivial character is labelled ambiguous rather than solved; serialized public input is rejected if label/scalar text appears; a k>1 base-field self argument is evaluated separately; coordinate transport uses `(x,y)->(u^2x,u^3y)` and transformed coefficients `(u^4A,u^6B)`; and the exact table compares each `chi([a]G)` with `chi(G)^a`.

Source provenance: the frozen specification and Sage Tate-pairing API citation are `retrieved` in the specification. The formulas here are ordinary implementation deductions from that frozen source and the predecessor’s explicitly bound local implementation; this note introduces no outside literature claim.
