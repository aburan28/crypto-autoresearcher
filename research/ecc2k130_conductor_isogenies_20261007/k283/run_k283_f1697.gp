\\ Complete CM census of the conductor-1697 floor below NIST K-283.
\\ Standard curve: y^2 + x*y = x^3 + 1 over the NIST polynomial basis.
\\ This produces candidates; verify37.gp independently checks the exact census.
m = 283;
a = 0;
F = 1697;
S = 37;
NSAMP = 1;
FIELD_MODULUS = x^283+x^12+x^7+x^5+1;
OUT = "floor_k283_f1697.txt";

read("../survey/cm_floor.gp");
