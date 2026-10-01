default(parisizemax, 2000000000);
p = 18446744069414584321; z = ffgen(Mod(1,p)*(x^5-3), 'z);
N = 2135987033434293902082969833143585405490115481161334371115336632973732695611872711359481303666403;
c = primecert(N);
print("VALID=", primecertisvalid(c));
print("APRCL=", isprime(N));
write("/home/user/crypto-autoresearcher/experiments/EXP-GFPN-726eb2/runs/RUN-GFPN-3bbef2/certificates/ecpp/n.cert", c);
