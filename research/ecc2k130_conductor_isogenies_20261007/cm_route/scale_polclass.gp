\\ timing of polclass(-7 f^2, 1) (Weber f) for growing f, to extrapolate to f = 120871 (h = 120870)
{foreach([6473, 12011, 24019], f, my(D = -7*f^2, t = getabstime(), H = polclass(D, 1), dt = getabstime() - t);
  print("f=", f, " h=", poldegree(H), " |D|=", -D, "  polclass ", dt\1000, " s, max coeff 2^", round(log(normlp(Vec(H), oo))/log(2)),
        ", total size ", round(sum(i = 0, poldegree(H), if(polcoeff(H,i), log(abs(polcoeff(H,i)))/log(2), 0))/8/2^20), " MB"))}
