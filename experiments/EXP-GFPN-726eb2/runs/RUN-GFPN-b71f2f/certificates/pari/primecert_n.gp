default(parisizemax, 2000000000);
p = 18446744069414584321; z = ffgen(Mod(1,p)*(x^5-3), 'z);
N = 1067993516717146951041484916571792702745057740581727230159139685185762082554198619328292418486241;
c = primecert(N);
print("VALID=", primecertisvalid(c));
print("APRCL=", isprime(N));
write("/home/user/crypto-autoresearcher/experiments/EXP-GFPN-726eb2/runs/RUN-GFPN-b71f2f/certificates/ecpp/n.cert", c);
