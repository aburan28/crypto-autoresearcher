default(parisizemax, 2000000000);
p = 18446744069414584321; z = ffgen(Mod(1,p)*(x^5-3), 'z);
N = 13198683916356018834932125395010487372292391748506171;
c = primecert(N);
print("VALID=", primecertisvalid(c));
print("APRCL=", isprime(N));
write("/home/user/crypto-autoresearcher/experiments/EXP-GFPN-726eb2/runs/RUN-GFPN-b71f2f/certificates/ecpp/twistprime_m1_f4.cert", c);
