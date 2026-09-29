default(parisizemax, 2000000000);
p = 18446744069414584321; z = ffgen(Mod(1,p)*(x^5-3), 'z);
N = 15681773581444271028521439790760295429825421693261780169927627118198022789929066801495901803187;
c = primecert(N);
print("VALID=", primecertisvalid(c));
print("APRCL=", isprime(N));
write("/home/user/crypto-autoresearcher/coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-01af16/scratch/objects/objD_gf_shifted_rigidity/out/certificates/ecpp/D_f3.cert", c);
