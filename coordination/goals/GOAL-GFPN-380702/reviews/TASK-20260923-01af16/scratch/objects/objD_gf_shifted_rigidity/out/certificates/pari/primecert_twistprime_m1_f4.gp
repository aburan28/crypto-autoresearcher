default(parisizemax, 2000000000);
p = 18446744069414584321; z = ffgen(Mod(1,p)*(x^5-3), 'z);
N = 13198683916356018834932125395010487372292391748506171;
c = primecert(N);
print("VALID=", primecertisvalid(c));
print("APRCL=", isprime(N));
write("/home/user/crypto-autoresearcher/coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-01af16/scratch/objects/objD_gf_shifted_rigidity/out/certificates/ecpp/twistprime_m1_f4.cert", c);
