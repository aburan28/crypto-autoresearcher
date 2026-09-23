default(parisizemax, 2000000000);
p = 18446744069414584321; z = ffgen(Mod(1,p)*(x^5-3), 'z);
N = 981394945332765852739783890042638080022301387020925721;
c = primecert(N);
print("VALID=", primecertisvalid(c));
print("APRCL=", isprime(N));
write("/home/user/crypto-autoresearcher/coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-01af16/scratch/objects/objA_supersingular/out/certificates/ecpp/twist_f6.cert", c);
