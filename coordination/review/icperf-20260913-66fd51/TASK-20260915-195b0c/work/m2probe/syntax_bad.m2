R = ZZ/2[a,b];
G = ideal(a+b);
gens_ = flatten entries gens G;
<< "REACHED " << #gens_ << endl;
exit 0;
