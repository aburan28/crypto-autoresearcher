default(parisizemax, 2000000000);
p = 18446744069414584321; z = ffgen(Mod(1,p)*(x^5-3), 'z);
N = 198400523053184002814403536918162724916343842520561;
c = primecert(N);
print("VALID=", primecertisvalid(c));
print("APRCL=", isprime(N));
write("/home/user/crypto-autoresearcher/experiments/EXP-GFPN-726eb2/runs/RUN-GFPN-b71f2f/certificates/ecpp/nm1_f6.cert", c);
