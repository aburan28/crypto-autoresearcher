import cypari2
pari = cypari2.Pari()
print(type(pari))
print(pari('2+2'))
r = pari('ellinit([0,0,0,-1,1])')
print(r)
print(pari('%s.c4' % r))
print(pari('iferr(alarm(3,ellrank(ellinit([0,0,0,-1,1]))),E,[-1,-1,0,[]])'))
