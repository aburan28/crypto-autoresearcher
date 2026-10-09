\\ independent second 82153-descent from the same 45641-floor curve: a different PARI seed (setrand(2)) than the default
\\ seed used by down163.gp / down163b.gp, so a different random kernel point.
setrand(2);
MOD = x^163+x^7+x^6+x^3+1; m = 163; A2 = 1; BINT = 20183018253319052689704116247546275258431720285; lp = 82153; k = 63; twist = 1; NISO = 1; OUT = "down163c.txt";
read("vert_down.gp");
