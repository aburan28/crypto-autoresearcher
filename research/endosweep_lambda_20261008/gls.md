# Binary GLS curve with lambda coordinates (counted)

F_q = F_2[x]/(x^127 + x^63 + 1), F_q2 = F_q[u]/(u^2 + u + 1); E~: y^2 + xy = x^3 + u x^2 + b, b = 0x5f23a6ac3d9b2dea0a4daed45ce6b2e9.

* trace of E: y^2 + xy = x^3 + b over F_q (AGM): t = 20251382237556413037
* #E~(F_q2) = (q - 1)^2 + t^2 = 2 r, r prime, log2 r = 253.0 (found after 30 candidate b)
* psi(x, y) = (x^q, y^q + u x^q) acts on <G> as delta, delta^2 = -1 (mod r), delta t = -(q - 1) (mod r)
* checks: E(F_q)_order_q+1-t_and_twist_q+1+t_kill_points: True, trace_of_a'=u_is_1: True, order_2r_proven: True, order_equals_(q-1)^2+t^2: True, psi^2=-1_on_points: True, psi_is_additive: True, psi_lambda_forms_agree_with_affine: True, psi(G)=[delta]G,delta^2=-1: True, delta*t=+-(q-1)_mod_r: True
* 2-GLV lattice: Babai bound 127 bits, empirical max 126 bits over 256 scalars (balanced: 126.5)

## Per-operation counts on E~ (measured)

| formula | F_q2 operations | F_q operations |
|:--|:--|:--|
| lambda doubling_main | 4M + 1m_c + 4S | 12M + 8S |
| lambda doubling_alt | 3M + 3m_c + 4S | 11M + 8S |
| lambda full_addition | 11M + 0m_c + 2S | 33M + 4S |
| lambda mixed_addition | 8M + 0m_c + 2S | 24M + 4S |
| lambda doubling_and_addition | 10M + 1m_c + 6S | 30M + 12S |
| lambda psi | 0M + 0m_c + 0S | 0M + 0S |
| LD doubling | 3M + 2m_c + 5S | 11M + 10S |
| LD mixed_addition | 8M + 1m_c + 5S | 24M + 10S |

## k*G, mean F_q operations over 32 scalars (best width), input in the method's own form

| method | S free (M) | per bit of r | S = M (M + S) | per bit of r |
|:--|--:|--:|--:|--:|
| ld/1d | 4124 (w5) | 16.3 | 7452 (w5) | 29.456 |
| lambda/1d | 4127 (w5) | 16.312 | 6634 (w5) | 26.221 |
| lambda/1d-da | 3891 (w4) | 15.379 | 6389 (w4) | 25.254 |
| ld/glv | 2740 (w5) | 10.831 | 4807 (w5) | 19.002 |
| lambda/glv | 2743 (w5) | 10.843 | 4235 (w4) | 16.741 |
| lambda/glv-da | 2531 (w4) | 10.003 | 4015 (w4) | 15.869 |

## Against the Koblitz curves' TNAF (per bit of group order, each in its own field's multiplications)

| curve | field | log2 order | S free per bit | S = M per bit | modelled F_2^127-mult-equivalents per bit (S = M) |
|:--|--:|--:|--:|--:|--:|
| GLS-lambda 2-GLV (this curve) | 2^127 (F_q ops) | 253.0 | 10.003 | 15.869 | 15.87 |
| K-163 lambda TNAF | 2^163 | 162.0 | 1.938 | 7.4 | 14.07 |
| K-163 LD TNAF | 2^163 | 162.0 | 1.932 | 8.109 | 15.42 |
| K-233 lambda TNAF | 2^233 | 231.0 | 1.852 | 7.331 | 21.99 |
| K-233 LD TNAF | 2^233 | 231.0 | 1.848 | 7.982 | 23.95 |
| K-283 lambda TNAF | 2^283 | 281.0 | 1.777 | 7.237 | 30.92 |
| K-283 LD TNAF | 2^283 | 281.0 | 1.773 | 7.865 | 33.61 |
| K-409 lambda TNAF | 2^409 | 407.0 | 1.654 | 7.175 | 52.26 |
| K-409 LD TNAF | 2^409 | 407.0 | 1.652 | 7.779 | 56.66 |
| K-571 lambda TNAF | 2^571 | 569.0 | 1.571 | 7.049 | 76.46 |
| K-571 LD TNAF | 2^571 | 569.0 | 1.569 | 7.61 | 82.55 |

The last column is MODELLED: a multiplication in F_2^n is weighted (ceil(n/64))^log2(3) relative to
F_2^127 (Karatsuba on 64-bit words), and a squaring like a multiplication.  It is an assumption, not
a measurement; the per-bit columns before it are measured counts in each curve's own field.

## Every configuration (F_q operations; main loop also in F_q2 operations)

| config | S free | S = M | S free, conv. incl. | S = M, conv. incl. | main loop m~ + s~ |
|:--|--:|--:|--:|--:|:--|
| ld/1d/w2 | 4807.8 | 8295.8 | 4807.8 | 8295.8 | 1595.9 m~ + 1679.53 s~ |
| lambda/1d/w2 | 4810.8 | 7288.8 | 4827.8 | 7432.8 | 1595.9 m~ + 1175.5 s~ |
| lambda/1d-da/w2 | 4390.5 | 6868.5 | 4407.5 | 7012.5 | 1455.8 m~ + 1175.5 s~ |
| ld/glv/w2 | 3428.0 | 5653.5 | 3428.0 | 5653.5 | 1136.0 m~ + 1048.28 s~ |
| lambda/glv/w2 | 3431.0 | 4896.2 | 3448.0 | 5040.2 | 1136.0 m~ + 669.12 s~ |
| lambda/glv-da/w2 | 3082.1 | 4547.3 | 3099.1 | 4691.3 | 1019.7 m~ + 669.12 s~ |
| ld/1d/w3 | 4345.2 | 7763.2 | 4345.2 | 7763.2 | 1423.4 m~ + 1570.0 s~ |
| lambda/1d/w3 | 4348.2 | 6875.0 | 4365.2 | 7019.0 | 1423.4 m~ + 1130.44 s~ |
| lambda/1d-da/w3 | 4034.2 | 6561.1 | 4051.2 | 6705.1 | 1318.7 m~ + 1130.44 s~ |
| ld/glv/w3 | 2973.7 | 5134.2 | 2973.7 | 5134.2 | 966.2 m~ + 941.25 s~ |
| lambda/glv/w3 | 2976.7 | 4493.9 | 2993.7 | 4637.9 | 966.2 m~ + 625.62 s~ |
| lambda/glv-da/w3 | 2701.1 | 4218.3 | 2718.1 | 4362.3 | 874.4 m~ + 625.62 s~ |
| ld/1d/w4 | 4138.2 | 7471.2 | 4138.2 | 7471.2 | 1321.1 m~ + 1505.47 s~ |
| lambda/1d/w4 | 4141.2 | 6639.6 | 4158.2 | 6783.6 | 1321.1 m~ + 1104.19 s~ |
| lambda/1d-da/w4 | 3890.8 | 6389.2 | 3907.8 | 6533.2 | 1237.6 m~ + 1104.19 s~ |
| ld/glv/w4 | 2748.3 | 4814.7 | 2748.3 | 4814.7 | 857.8 m~ + 872.19 s~ |
| lambda/glv/w4 | 2751.3 | 4235.4 | 2768.3 | 4379.4 | 857.8 m~ + 597.06 s~ |
| lambda/glv-da/w4 | 2530.7 | 4014.8 | 2547.7 | 4158.8 | 784.2 m~ + 597.06 s~ |
| ld/1d/w5 | 4124.0 | 7452.4 | 4124.0 | 7452.4 | 1249.7 m~ + 1459.22 s~ |
| lambda/1d/w5 | 4127.0 | 6634.0 | 4144.0 | 6778.0 | 1249.7 m~ + 1084.5 s~ |
| lambda/1d-da/w5 | 3919.8 | 6426.8 | 3936.8 | 6570.8 | 1180.6 m~ + 1084.5 s~ |
| ld/glv/w5 | 2740.2 | 4807.4 | 2740.2 | 4807.4 | 788.4 m~ + 828.59 s~ |
| lambda/glv/w5 | 2743.2 | 4240.1 | 2760.2 | 4384.1 | 788.4 m~ + 579.44 s~ |
| lambda/glv-da/w5 | 2556.2 | 4053.1 | 2573.2 | 4197.1 | 726.1 m~ + 579.44 s~ |
| ld/1d/w6 | 4377.1 | 7817.8 | 4377.1 | 7817.8 | 1200.7 m~ + 1427.34 s~ |
| lambda/1d/w6 | 4380.1 | 6955.7 | 4397.1 | 7099.7 | 1200.7 m~ + 1070.81 s~ |
| lambda/1d-da/w6 | 4202.4 | 6778.0 | 4219.4 | 6922.0 | 1141.5 m~ + 1070.81 s~ |
| ld/glv/w6 | 3005.6 | 5190.9 | 3005.6 | 5190.9 | 743.5 m~ + 799.69 s~ |
| lambda/glv/w6 | 3008.6 | 4577.1 | 3025.6 | 4721.1 | 743.5 m~ + 567.25 s~ |
| lambda/glv-da/w6 | 2842.2 | 4410.7 | 2859.2 | 4554.7 | 688.0 m~ + 567.25 s~ |
| ld/1d/w7 | 5062.5 | 8804.5 | 5062.5 | 8804.5 | 1162.5 m~ + 1402.03 s~ |
| lambda/1d/w7 | 5065.5 | 7810.7 | 5082.5 | 7954.7 | 1162.5 m~ + 1059.62 s~ |
| lambda/1d-da/w7 | 4910.5 | 7655.7 | 4927.5 | 7799.7 | 1110.8 m~ + 1059.62 s~ |
| ld/glv/w7 | 3683.7 | 6166.4 | 3683.7 | 6166.4 | 702.9 m~ + 772.34 s~ |
| lambda/glv/w7 | 3686.7 | 5422.4 | 3703.7 | 5566.4 | 702.9 m~ + 554.88 s~ |
| lambda/glv-da/w7 | 3545.6 | 5281.3 | 3562.6 | 5425.3 | 655.9 m~ + 554.88 s~ |
