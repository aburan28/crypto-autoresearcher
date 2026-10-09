m=131; P=lift(Mod(-x,x^2-x+2)^m); X=polcoeff(P,0); l=146505763881528721;
c=Mod(X,l); o=znorder(c); h=if(o%2==0 && c^(o/2)==-1, o/2, o);
print("l = ",l,"  log2 l = ",log(l)/log(2)); print("ord(c) = ",o," = ",factor(o)); print("-1 in <c>: ",o%2==0 && c^(o/2)==-1,"  -> x-coordinates of kernel points live in F_2^(131*k), k = ",h);
print("extension degree 131k = ",131*h,"  (log2 = ",log(131*h)/log(2),")");
print("kernel polynomial degree (l-1)/2 = ",(l-1)/2,"  storage at 131 bits/coeff = ",(l-1)/2*131/8/1e18," EB");
print("Phi_l degree in Y: ",l+1,";  descending l-isogenies from crater: ",l+1,"  (l inert)");
print("class number of the l-floor: ",l+1, "  fraction of the whole isogeny class: ",(l+1.)/38531015900842054149);
print("isogeny class size / 2^131 (chance a random b is in the class at all): ",38531015900842054149./2^131, "  -> log2 ", log(38531015900842054149./2^131)/log(2));
print("l-floor curves / 2^131: log2 = ", log((l+1.)/2^131)/log(2));
print("for comparison: rho on ECC2K-130 with Frobenius ~ 2^",log(sqrt(Pi*680564733841876926932320129493409985129/(4*131)))/log(2));
\\ smallest extension containing a full kernel point (y too): order of c
print("smallest field containing E[l] points: F_2^(131*",o,")");
