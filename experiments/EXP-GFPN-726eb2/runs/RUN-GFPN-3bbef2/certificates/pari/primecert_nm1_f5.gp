default(parisizemax, 2000000000);
p = 18446744069414584321; z = ffgen(Mod(1,p)*(x^5-3), 'z);
N = 195493062820916885018330603;
c = primecert(N);
print("VALID=", primecertisvalid(c));
print("APRCL=", isprime(N));
write("/home/user/crypto-autoresearcher/experiments/EXP-GFPN-726eb2/runs/RUN-GFPN-3bbef2/certificates/ecpp/nm1_f5.cert", c);
