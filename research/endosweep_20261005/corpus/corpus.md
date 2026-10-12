# Standardized-curve corpus scan

Source: std-curves database. Certificate bound |D_K| <= 2000000. Costs are operation counts under the sweep's model.

- curves in corpus: 248; prime-field and verified: 171; certified |D_K| > 2000000: 113; small CM discriminant: 58; skipped (binary/extension/tower/unparsed): 77; failed verification: 0
- cross-check against the database's own cm_disc: 117 agree, 0 disagree, 54 without database data

## Curves with a small CM discriminant

| curve | bits | form | D_K | h(D) | min degree | cheapest chain | chain M | modelled best | total M | generic M | speedup | explicit chain |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bls/BLS12-377 | 377 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 1433 | 2162 | 1.51x | verified on points |
| bls/BLS12-381 | 381 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 1453 | 2185 | 1.50x | verified on points |
| bls/BLS12-446 | 446 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 1662 | 2524 | 1.52x | verified on points |
| bls/BLS12-455 | 455 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 1680 | 2562 | 1.52x | verified on points |
| bls/BLS12-638 | 638 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 2263 | 3509 | 1.55x | verified on points |
| bls/BLS24-477 | 477 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 2056 | 3170 | 1.54x | verified on points |
| bls/BLS48-581-G1 | 581 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 2686 | 4210 | 1.57x | verified on points |
| bn/bn158 | 158 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 959 | 1419 | 1.48x | verified on points |
| bn/bn190 | 190 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 1121 | 1677 | 1.50x | verified on points |
| bn/bn222 | 222 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 1282 | 1931 | 1.51x | verified on points |
| bn/bn254 | 254 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 1443 | 2169 | 1.50x | verified on points |
| bn/bn286 | 286 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 1596 | 2416 | 1.51x | verified on points |
| bn/bn318 | 318 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 1746 | 2670 | 1.53x | verified on points |
| bn/bn350 | 350 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 1897 | 2909 | 1.53x | verified on points |
| bn/bn382 | 382 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 2047 | 3163 | 1.55x | verified on points |
| bn/bn414 | 414 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 2197 | 3401 | 1.55x | verified on points |
| bn/bn446 | 446 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 2348 | 3656 | 1.56x | verified on points |
| bn/bn478 | 478 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 2498 | 3902 | 1.56x | verified on points |
| bn/bn510 | 510 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 2649 | 4148 | 1.57x | verified on points |
| bn/bn542 | 542 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 2799 | 4395 | 1.57x | verified on points |
| bn/bn574 | 574 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 2949 | 4633 | 1.57x | verified on points |
| bn/bn606 | 606 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 3100 | 4877 | 1.57x | verified on points |
| bn/bn638 | 638 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 3250 | 5116 | 1.57x | verified on points |
| gost/gost256 | 256 | Weierstrass | -915 | 8 | 229 | 3*7*11 | 61 | GLV-2 [endo[1+1w] deg 3*7*11] | 1740 | 2540 | 1.46x | verified on points |
| gost/id-GostR3410-2001-CryptoPro-B-ParamSet | 256 | Weierstrass | -619 | 5 | 155 | 5^2*7 | 53 | GLV-2 [endo[4+1w] deg 5^2*7] | 1681 | 2439 | 1.45x | verified on points |
| mnt/mnt1 | 170 | Weierstrass | -19 | 1 | 5 | 5 | 30 | GLV-2 [endo[0+1w] deg 5] | 1135 | 1620 | 1.43x | verified on points |
| mnt/mnt2/1 | 159 | Weierstrass | -91 | 2 | 23 | 5^2 | 39 | GLV-2 [endo[3+1w] deg 5*7] | 1172 | 1649 | 1.41x | verified on points |
| mnt/mnt2/2 | 159 | Weierstrass | -91 | 2 | 23 | 5^2 | 39 | GLV-2 [endo[3+1w] deg 5*7] | 1172 | 1649 | 1.41x | verified on points |
| mnt/mnt3/1 | 160 | Weierstrass | -139 | 3 | 35 | 5*7 | 43 | GLV-2 [endo[4+1w] deg 5*11] | 1180 | 1658 | 1.41x | verified on points |
| mnt/mnt3/2 | 160 | Weierstrass | -139 | 3 | 35 | 5*7 | 43 | GLV-2 [endo[4+1w] deg 5*11] | 1180 | 1658 | 1.41x | verified on points |
| mnt/mnt3/3 | 160 | Weierstrass | -139 | 3 | 35 | 5*7 | 43 | GLV-2 [endo[4+1w] deg 5*11] | 1180 | 1658 | 1.41x | verified on points |
| mnt/mnt4 | 240 | Weierstrass | -163 | 1 | 41 | 41 | 102 | GLV-2 [endo[0+1w] deg 41] | 1712 | 2395 | 1.40x | verified on points |
| mnt/mnt5/1 | 240 | Weierstrass | -211 | 3 | 53 | 5^3 | 49 | GLV-2 [endo[8+1w] deg 5^3] | 1648 | 2395 | 1.45x | verified on points |
| mnt/mnt5/2 | 240 | Weierstrass | -211 | 3 | 53 | 5^3 | 49 | GLV-2 [endo[8+1w] deg 5^3] | 1648 | 2395 | 1.45x | verified on points |
| mnt/mnt5/3 | 240 | Weierstrass | -211 | 3 | 53 | 5^3 | 49 | GLV-2 [endo[8+1w] deg 5^3] | 1648 | 2395 | 1.45x | verified on points |
| other/Fp224BN | 224 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 1292 | 1946 | 1.51x | verified on points |
| other/Fp254BNa | 254 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 1443 | 2169 | 1.50x | verified on points |
| other/Fp254BNb | 254 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 1443 | 2169 | 1.50x | verified on points |
| other/Fp256BN | 256 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 1453 | 2192 | 1.51x | verified on points |
| other/Fp384BN | 384 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 2056 | 3178 | 1.55x | verified on points |
| other/Fp512BN | 512 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 2658 | 4164 | 1.57x | verified on points |
| other/Pallas | 255 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 1453 | 2177 | 1.50x | verified on points |
| other/Tom-256 | 256 | Weierstrass | -4155 | 12 | 1039 | 5*11*19 | 89 | GLV-2 [endo[49+2w] deg 5*11^3] | 1723 | 2448 | 1.42x | verified on points |
| other/Tom-384 | 384 | Weierstrass | -619 | 5 | 155 | 5^2*7 | 53 | GLV-2 [endo[4+1w] deg 5^2*7] | 2478 | 3714 | 1.50x | verified on points |
| other/Tom-521 | 521 | Weierstrass | -28243 | 24 | 7061 | 7*11^3 | 98 | GLV-2 [endo[47+1w] deg 7*11^3] | 3272 | 4961 | 1.52x | verified on points |
| other/Tweedledee | 255 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 1453 | 2177 | 1.50x | verified on points |
| other/Tweedledum | 255 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 1453 | 2177 | 1.50x | verified on points |
| other/Vesta | 255 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 1453 | 2177 | 1.50x | verified on points |
| secg/secp160k1 | 160 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 969 | 1435 | 1.48x | verified on points |
| secg/secp192k1 | 192 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 1141 | 1693 | 1.48x | verified on points |
| secg/secp224k1 | 224 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 1302 | 1946 | 1.49x | verified on points |
| secg/secp256k1 | 256 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 1463 | 2192 | 1.50x | verified on points |
| wtls/wap-wsg-idm-ecid-wtls8 | 112 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 737 | 1049 | 1.42x | verified on points |
| wtls/wap-wsg-idm-ecid-wtls9 | 160 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 979 | 1435 | 1.47x | verified on points |
| x963/ansip160k1 | 160 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 969 | 1435 | 1.48x | verified on points |
| x963/ansip192k1 | 192 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 1141 | 1693 | 1.48x | verified on points |
| x963/ansip224k1 | 224 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 1302 | 1946 | 1.49x | verified on points |
| x963/ansip256k1 | 256 | Weierstrass | -3 | 1 | 1 | 3 | 26 | GLV-2 [zeta_3] | 1463 | 2192 | 1.50x | verified on points |

## Every prime-field curve

| curve | bits | form | verified | certificate | database cm_disc | agreement |
|---|---|---|---|---|---|---|
| anssi/FRP256v1 | 256 | Weierstrass | True | |D_K| > 2000000 | -436579445005972888745654076483329727173807379171830662730632433775066880362307 | agree: database |cm_disc| is above the scan bound |
| bls/BLS12-377 | 377 | Weierstrass | True | D_K = -3, conductor 587269870971281361444171168277668240640243801025419411456 | -3 | agree |
| bls/BLS12-381 | 381 | Weierstrass | True | D_K = -3, conductor 2310096550715768212670172227226928237551693238409523516757 | -3 | agree |
| bls/BLS12-446 | 446 | Weierstrass | True | D_K = -3, conductor 15180017722556942872710858686172241542425226563119817904740305163606 |  | database has no cm_disc |
| bls/BLS12-455 | 455 | Weierstrass | True | D_K = -3, conductor 287572867293678436974519977531226436303080379672880577582937484382891 | -3 | agree |
| bls/BLS12-638 | 638 | Weierstrass | True | D_K = -3, conductor 1201199398395787546723127300641679086142518436131015165481254517460567318887250290819436851298997 | -3 | agree |
| bls/BLS24-477 | 477 | Weierstrass | True | D_K = -3, conductor 604128092931004996153900356638872198640435149234420528912987303159267285 | -3 | agree |
| bls/BLS48-581-G1 | 581 | Weierstrass | True | D_K = -3, conductor 2470234952045228861226479692223628411074049366373861109485273675792210673668036995939286 | -3 | agree |
| bls/BLS48-581-G2 | 0 | Weierstrass | skipped | field type Tower: outside the prime-field pipeline | | |
| bls/Bandersnatch | 255 | TwistedEdwards | skipped | could not parse: invalid literal for int() with base 10: '-0x05' | | |
| bn/bn158 | 158 | Weierstrass | True | D_K = -3, conductor 454233058418789397299203 | -3 | agree |
| bn/bn190 | 190 | Weierstrass | True | D_K = -3, conductor 29710571568175225982381195267 | -3 | agree |
| bn/bn222 | 222 | Weierstrass | True | D_K = -3, conductor 1943310227059934888513759537528843 | -3 | agree |
| bn/bn254 | 254 | Weierstrass | True | D_K = -3, conductor 129607518034317099886745702645398241283 | -3 | agree |
| bn/bn286 | 286 | Weierstrass | True | D_K = -3, conductor 8366863340207706741294993301075392630620163 | -3 | agree |
| bn/bn318 | 318 | Weierstrass | True | D_K = -3, conductor 548079839685593379889101977298739683457859846211 | -3 | agree |
| bn/bn350 | 350 | Weierstrass | True | D_K = -3, conductor 35917316178020966140770026339278758006907024019816451 | -3 | agree |
| bn/bn382 | 382 | Weierstrass | True | D_K = -3, conductor 2353932232174051770881173201697930752584630523839501041667 | -3 | agree |
| bn/bn414 | 414 | Weierstrass | True | D_K = -3, conductor 154267229207681125708793071161632042239063797942298639324938243 | -3 | agree |
| bn/bn446 | 446 | Weierstrass | True | D_K = -3, conductor 10109980000181489923001201093401911741712157040574514822068840693771 | -3 | agree |
| bn/bn478 | 478 | Weierstrass | True | D_K = -3, conductor 662567649291894123450065105820326670768093618471357310296643630025146371 | -3 | agree |
| bn/bn510 | 510 | Weierstrass | True | D_K = -3, conductor 43422033463993573283847164979847511362163190678038904032036848688647949516803 | -3 | agree |
| bn/bn542 | 542 | Weierstrass | True | D_K = -3, conductor 2845711812853053972806387468884004947678148350198662474752430713551973652753285123 | -3 | agree |
| bn/bn574 | 574 | Weierstrass | True | D_K = -3, conductor 186496302581962721809830439849867378820456242583880530431255347119471774686354153144323 | -3 | agree |
| bn/bn606 | 606 | Weierstrass | True | D_K = -3, conductor 12222215858006915839141401255556695821975177552658946714103472755538745970781531637962639363 |  | database has no cm_disc |
| bn/bn638 | 638 | Weierstrass | True | D_K = -3, conductor 800995136978371572363525747477255032258950408690575773003799464919714074125184154404652534726667 | -3 | agree |
| brainpool/brainpoolP160r1 | 160 | Weierstrass | True | |D_K| > 2000000 | -4645380339943745084523443872838008326722778443 | agree: database |cm_disc| is above the scan bound |
| brainpool/brainpoolP160t1 | 160 | Weierstrass | True | |D_K| > 2000000 | -4645380339943745084523443872838008326722778443 | agree: database |cm_disc| is above the scan bound |
| brainpool/brainpoolP192r1 | 192 | Weierstrass | True | |D_K| > 2000000 | -13368072116223427911218896962387160374571840032632508108747 | agree: database |cm_disc| is above the scan bound |
| brainpool/brainpoolP192t1 | 192 | Weierstrass | True | |D_K| > 2000000 | -13368072116223427911218896962387160374571840032632508108747 | agree: database |cm_disc| is above the scan bound |
| brainpool/brainpoolP224r1 | 224 | Weierstrass | True | |D_K| > 2000000 | -70987994314632885262411297299970290552009893845341623260563782354235 | agree: database |cm_disc| is above the scan bound |
| brainpool/brainpoolP224t1 | 224 | Weierstrass | True | |D_K| > 2000000 | -70987994314632885262411297299970290552009893845341623260563782354235 | agree: database |cm_disc| is above the scan bound |
| brainpool/brainpoolP256r1 | 256 | Weierstrass | True | |D_K| > 2000000 | -8691544023946985377062942659708535371791103179088907241627919875068758335603 | agree: database |cm_disc| is above the scan bound |
| brainpool/brainpoolP256t1 | 256 | Weierstrass | True | |D_K| > 2000000 | -8691544023946985377062942659708535371791103179088907241627919875068758335603 | agree: database |cm_disc| is above the scan bound |
| brainpool/brainpoolP320r1 | 320 | Weierstrass | True | |D_K| > 2000000 | -3708660345413141026391719161592280591076138596512790759610265222571636079687307055058681975659659 | agree: database |cm_disc| is above the scan bound |
| brainpool/brainpoolP320t1 | 320 | Weierstrass | True | |D_K| > 2000000 | -3708660345413141026391719161592280591076138596512790759610265222571636079687307055058681975659659 | agree: database |cm_disc| is above the scan bound |
| brainpool/brainpoolP384r1 | 384 | Weierstrass | True | |D_K| > 2000000 |  | database has no cm_disc |
| brainpool/brainpoolP384t1 | 384 | Weierstrass | True | |D_K| > 2000000 |  | database has no cm_disc |
| brainpool/brainpoolP512r1 | 512 | Weierstrass | True | |D_K| > 2000000 |  | database has no cm_disc |
| brainpool/brainpoolP512t1 | 512 | Weierstrass | True | |D_K| > 2000000 |  | database has no cm_disc |
| gost/gost256 | 256 | Weierstrass | True | D_K = -915, conductor 5814239006315534931045933045806333847 | -915 | agree |
| gost/gost512 | 512 | Weierstrass | True | |D_K| > 2000000 |  | database has no cm_disc |
| gost/id-GostR3410-2001-CryptoPro-A-ParamSet | 256 | Weierstrass | True | |D_K| > 2000000 | -424665378973637295795640888511775743925042728546036986688706749501354362291267 | agree: database |cm_disc| is above the scan bound |
| gost/id-GostR3410-2001-CryptoPro-B-ParamSet | 256 | Weierstrass | True | D_K = -619, conductor 4646402506017662432554672533504826433 | -619 | agree |
| gost/id-GostR3410-2001-CryptoPro-C-ParamSet | 256 | Weierstrass | True | |D_K| > 2000000 | -256395600883612271892723315726519844445629930397733683085773745599364563982115 | agree: database |cm_disc| is above the scan bound |
| gost/id-tc26-gost-3410-12-512-paramSetA | 512 | Weierstrass | True | |D_K| > 2000000 | -44077247648723775457953059908923017372609510022789812783428832775239723883696748826627613109761565587375856967126319214595429328501251794033479398868138547 | agree: database |cm_disc| is above the scan bound |
| gost/id-tc26-gost-3410-12-512-paramSetB | 512 | Weierstrass | True | |D_K| > 2000000 | -183427792402739290758997034024870935740311148471045270938930870289190695480341554506776817122182826505221724743450519754049331850431306583272275935941515 | agree: database |cm_disc| is above the scan bound |
| gost/id-tc26-gost-3410-2012-256-paramSetA | 256 | TwistedEdwards | True | |D_K| > 2000000 |  | database has no cm_disc |
| gost/id-tc26-gost-3410-2012-512-paramSetC | 512 | TwistedEdwards | True | |D_K| > 2000000 |  | database has no cm_disc |
| mnt/mnt1 | 170 | Weierstrass | True | D_K = -19, conductor 6915889423298038776451801 | -19 | agree |
| mnt/mnt2/1 | 159 | Weierstrass | True | D_K = -91, conductor 151115727451828644755795 | -91 | agree |
| mnt/mnt2/2 | 159 | Weierstrass | True | D_K = -91, conductor 151115727451828644755795 | -91 | agree |
| mnt/mnt3/1 | 160 | Weierstrass | True | D_K = -139, conductor 151115727451828644749125 | -139 | agree |
| mnt/mnt3/2 | 160 | Weierstrass | True | D_K = -139, conductor 151115727451828644749125 | -139 | agree |
| mnt/mnt3/3 | 160 | Weierstrass | True | D_K = -139, conductor 151115727451828644749125 | -139 | agree |
| mnt/mnt4 | 240 | Weierstrass | True | D_K = -163, conductor 166153499473114484112975882535041529 | -163 | agree |
| mnt/mnt5/1 | 240 | Weierstrass | True | D_K = -211, conductor 166153499473114484112975882535035935 | -211 | agree |
| mnt/mnt5/2 | 240 | Weierstrass | True | D_K = -211, conductor 166153499473114484112975882535035935 | -211 | agree |
| mnt/mnt5/3 | 240 | Weierstrass | True | D_K = -211, conductor 166153499473114484112975882535035935 | -211 | agree |
| nist/B-163 | 163 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| nist/B-233 | 233 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| nist/B-283 | 283 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| nist/B-409 | 409 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| nist/B-571 | 571 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| nist/K-163 | 163 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| nist/K-233 | 233 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| nist/K-283 | 283 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| nist/K-409 | 409 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| nist/K-571 | 571 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| nist/P-192 | 192 | Weierstrass | True | |D_K| > 2000000 | -24109379060336110122544161233113975664949272517896865359515 | agree: database |cm_disc| is above the scan bound |
| nist/P-224 | 224 | Weierstrass | True | |D_K| > 2000000 | -9493061114565352281698673660738078664961855212656825491744070162387 | agree: database |cm_disc| is above the scan bound |
| nist/P-256 | 256 | Weierstrass | True | |D_K| > 2000000 | -455213823400003756884736869668539463648899917731097708475249543966132856781915 | agree: database |cm_disc| is above the scan bound |
| nist/P-384 | 384 | Weierstrass | True | |D_K| > 2000000 |  | database has no cm_disc |
| nist/P-521 | 521 | Weierstrass | True | |D_K| > 2000000 |  | database has no cm_disc |
| nums/ed-254-mont | 254 | TwistedEdwards | True | |D_K| > 2000000 |  | database has no cm_disc |
| nums/ed-255-mers | 255 | TwistedEdwards | True | |D_K| > 2000000 |  | database has no cm_disc |
| nums/ed-256-mont | 256 | TwistedEdwards | True | |D_K| > 2000000 |  | database has no cm_disc |
| nums/ed-382-mont | 382 | TwistedEdwards | True | |D_K| > 2000000 |  | database has no cm_disc |
| nums/ed-383-mers | 383 | TwistedEdwards | True | |D_K| > 2000000 |  | database has no cm_disc |
| nums/ed-384-mont | 384 | TwistedEdwards | True | |D_K| > 2000000 |  | database has no cm_disc |
| nums/ed-510-mont | 510 | TwistedEdwards | True | |D_K| > 2000000 |  | database has no cm_disc |
| nums/ed-511-mers | 511 | TwistedEdwards | True | |D_K| > 2000000 |  | database has no cm_disc |
| nums/ed-512-mont | 512 | TwistedEdwards | True | |D_K| > 2000000 |  | database has no cm_disc |
| nums/numsp256d1 | 256 | Weierstrass | True | |D_K| > 2000000 | -461806436970513507795776071208962019617834464011805499237102336028251098834763 | agree: database |cm_disc| is above the scan bound |
| nums/numsp256t1 | 256 | TwistedEdwards | True | |D_K| > 2000000 |  | database has no cm_disc |
| nums/numsp384d1 | 384 | Weierstrass | True | |D_K| > 2000000 |  | database has no cm_disc |
| nums/numsp384t1 | 384 | TwistedEdwards | True | |D_K| > 2000000 |  | database has no cm_disc |
| nums/numsp512d1 | 512 | Weierstrass | True | |D_K| > 2000000 |  | database has no cm_disc |
| nums/numsp512t1 | 512 | TwistedEdwards | True | |D_K| > 2000000 |  | database has no cm_disc |
| nums/w-254-mont | 254 | Weierstrass | skipped | could not parse: invalid literal for int() with base 10: '-0x2f72' | | |
| nums/w-255-mers | 255 | Weierstrass | skipped | could not parse: invalid literal for int() with base 10: '-0x51bd' | | |
| nums/w-256-mont | 256 | Weierstrass | True | |D_K| > 2000000 | -462522475925072085027879645099841527608786562102829859723871355201056468266563 | agree: database |cm_disc| is above the scan bound |
| nums/w-382-mont | 382 | Weierstrass | skipped | could not parse: invalid literal for int() with base 10: '-0x20a72' | | |
| nums/w-383-mers | 383 | Weierstrass | True | |D_K| > 2000000 | -74335890621480155989754748787396375367320169623343827664223445845656783833349619164859155948472241645542524819261923 | agree: database |cm_disc| is above the scan bound |
| nums/w-384-mont | 384 | Weierstrass | True | |D_K| > 2000000 |  | database has no cm_disc |
| nums/w-510-mont | 510 | Weierstrass | True | |D_K| > 2000000 |  | database has no cm_disc |
| nums/w-511-mers | 511 | Weierstrass | True | |D_K| > 2000000 |  | database has no cm_disc |
| nums/w-512-mont | 512 | Weierstrass | True | |D_K| > 2000000 |  | database has no cm_disc |
| oakley/192-bit Random ECP Group | 192 | Weierstrass | True | |D_K| > 2000000 | -24109379060336110122544161233113975664949272517896865359515 | agree: database |cm_disc| is above the scan bound |
| oakley/224-bit Random ECP Group | 224 | Weierstrass | True | |D_K| > 2000000 | -9493061114565352281698673660738078664961855212656825491744070162387 | agree: database |cm_disc| is above the scan bound |
| oakley/256-bit Random ECP Group | 256 | Weierstrass | True | |D_K| > 2000000 | -455213823400003756884736869668539463648899917731097708475249543966132856781915 | agree: database |cm_disc| is above the scan bound |
| oakley/384-bit Random ECP Group | 384 | Weierstrass | True | |D_K| > 2000000 |  | database has no cm_disc |
| oakley/521-bit Random ECP Group | 521 | Weierstrass | True | |D_K| > 2000000 |  | database has no cm_disc |
| oakley/Oakley Group 3 | 155 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| oakley/Oakley Group 4 | 185 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| oscaa/SM2 | 256 | Weierstrass | True | |D_K| > 2000000 |  | database has no cm_disc |
| other/BADA55-R-256 | 256 | Weierstrass | True | |D_K| > 2000000 | -11698450377829753151182841061045172603605934816251805048442847406795581220411 | agree: database |cm_disc| is above the scan bound |
| other/BADA55-VPR-224 | 224 | Weierstrass | True | |D_K| > 2000000 | -93798849498425056487645609391472088921124359957609087271436345059499 | agree: database |cm_disc| is above the scan bound |
| other/BADA55-VPR2-224 | 224 | Weierstrass | True | |D_K| > 2000000 | -107401608418668923735108959339263260485069539573549549469677727550299 | agree: database |cm_disc| is above the scan bound |
| other/BADA55-VR-224 | 224 | Weierstrass | True | |D_K| > 2000000 | -83603022686129646234941616899021932478780905385709345662522537683123 | agree: database |cm_disc| is above the scan bound |
| other/BADA55-VR-256 | 256 | Weierstrass | True | |D_K| > 2000000 | -2321915750431602639951745777848759230392148833334080756496923484040850443763 | agree: database |cm_disc| is above the scan bound |
| other/BADA55-VR-384 | 384 | Weierstrass | True | |D_K| > 2000000 |  | database has no cm_disc |
| other/Curve1174 | 251 | Weierstrass | True | |D_K| > 2000000 | -3104780625450999362585819446753918118449992865572619605369411600236483762515 | agree: database |cm_disc| is above the scan bound |
| other/Curve22103 | 221 | Weierstrass | True | |D_K| > 2000000 | -2685314091542274230334182065126357176037265034207186753290839435588 | agree: database |cm_disc| is above the scan bound |
| other/Curve25519 | 255 | Montgomery | True | |D_K| > 2000000 |  | database has no cm_disc |
| other/Curve383187 | 283 | Montgomery | True | |D_K| > 2000000 |  | database has no cm_disc |
| other/Curve41417 | 414 | TwistedEdwards | True | |D_K| > 2000000 |  | database has no cm_disc |
| other/Curve4417 | 226 | Weierstrass | True | |D_K| > 2000000 | -88013998525868146970191166912191547453398359252925306734643974307 | agree: database |cm_disc| is above the scan bound |
| other/Curve448 | 448 | Montgomery | True | |D_K| > 2000000 |  | database has no cm_disc |
| other/Curve67254 | 382 | Weierstrass | True | |D_K| > 2000000 |  | database has no cm_disc |
| other/E-222 | 222 | Edwards | True | |D_K| > 2000000 |  | database has no cm_disc |
| other/E-382 | 382 | Edwards | True | |D_K| > 2000000 |  | database has no cm_disc |
| other/E-521 | 521 | Edwards | True | |D_K| > 2000000 |  | database has no cm_disc |
| other/Ed25519 | 255 | TwistedEdwards | True | |D_K| > 2000000 |  | database has no cm_disc |
| other/Ed448 | 448 | TwistedEdwards | True | |D_K| > 2000000 |  | database has no cm_disc |
| other/Ed448-Goldilocks | 448 | TwistedEdwards | True | |D_K| > 2000000 |  | database has no cm_disc |
| other/FourQ | 127 | TwistedEdwards | skipped | field type Extension: outside the prime-field pipeline | | |
| other/Fp224BN | 224 | Weierstrass | True | D_K = -3, conductor 5192296858534689506442115857736067 | -3 | agree |
| other/Fp254BNa | 254 | Weierstrass | True | D_K = -3, conductor 126611883464401272127243293666542878721 | -3 | agree |
| other/Fp254BNb | 254 | Weierstrass | True | D_K = -3, conductor 129607518034317099886745702645398241283 | -3 | agree |
| other/Fp254n2BNa | 508 | Weierstrass | skipped | field type Extension: outside the prime-field pipeline | | |
| other/Fp256BN | 256 | Weierstrass | True | D_K = -3, conductor 340282366920936614181528116269263699971 | -3 | agree |
| other/Fp384BN | 384 | Weierstrass | True | D_K = -3, conductor 6277101735386680763835754795151022476645729035004851856003 | -3 | agree |
| other/Fp512BN | 512 | Weierstrass | True | D_K = -3, conductor 115792089237316195423570985008687840101659558519570290085463645789117669918083 | -3 | agree |
| other/JubJub | 255 | TwistedEdwards | True | |D_K| > 2000000 |  | database has no cm_disc |
| other/M-221 | 221 | Montgomery | True | |D_K| > 2000000 |  | database has no cm_disc |
| other/M-383 | 383 | Montgomery | True | |D_K| > 2000000 |  | database has no cm_disc |
| other/M-511 | 511 | Montgomery | True | |D_K| > 2000000 |  | database has no cm_disc |
| other/MDC201601 | 256 | Edwards | True | |D_K| > 2000000 |  | database has no cm_disc |
| other/Pallas | 255 | Weierstrass | True | D_K = -3, conductor 196462116142286827589391630752301449217 | -3 | agree |
| other/Tom-256 | 256 | Weierstrass | True | D_K = -4155, conductor 7019618127640898221939468283479924503 | -4155 | agree |
| other/Tom-384 | 384 | Weierstrass | True | D_K = -619, conductor 380201093441490505678902542719199835054253522446560116525 | -619 | agree |
| other/Tom-521 | 521 | Weierstrass | True | D_K = -28243, conductor 6268055400574841440667156810254912726834973227558374885183820779126439865891 | -28243 | agree |
| other/Tweedledee | 255 | Weierstrass | True | D_K = -3, conductor 196462116142286827589390971285842952193 | -3 | agree |
| other/Tweedledum | 255 | Weierstrass | True | D_K = -3, conductor 196462116142286827589390971285842952193 | -3 | agree |
| other/Vesta | 255 | Weierstrass | True | D_K = -3, conductor 196462116142286827589391630752301449217 | -3 | agree |
| other/ssc-160 | 160 | Weierstrass | True | |D_K| > 2000000 | -4167223475908033630914947676870079338908713720299 | agree: database |cm_disc| is above the scan bound |
| other/ssc-192 | 192 | Weierstrass | True | |D_K| > 2000000 | -15045036778406218234967275420770217256389969312108541204587 | agree: database |cm_disc| is above the scan bound |
| other/ssc-224 | 224 | Weierstrass | True | |D_K| > 2000000 | -56154226505913530382335709527037150072202594880026357475224494130195 | agree: database |cm_disc| is above the scan bound |
| other/ssc-256 | 256 | Weierstrass | True | |D_K| > 2000000 | -40020000671191509263673608690492641910104408280738782855468068664198113540123 | agree: database |cm_disc| is above the scan bound |
| other/ssc-288 | 288 | Weierstrass | True | |D_K| > 2000000 | -556400873659257239436335452850017612643167293605403970991823708262633707837974028266587 | agree: database |cm_disc| is above the scan bound |
| other/ssc-320 | 320 | Weierstrass | True | |D_K| > 2000000 | -24583513908120940535393951773433057494153140751760772520791113373580804392885557750143467820707 | agree: database |cm_disc| is above the scan bound |
| other/ssc-384 | 384 | Weierstrass | True | |D_K| > 2000000 | -13381674613993644881458548904489259606699050675502629537079635738695590079972665519276150159843151618131690069980235 | agree: database |cm_disc| is above the scan bound |
| other/ssc-512 | 512 | Weierstrass | True | |D_K| > 2000000 |  | database has no cm_disc |
| secg/secp112r1 | 112 | Weierstrass | True | |D_K| > 2000000 | -17787316666415881930611191403938683 | agree: database |cm_disc| is above the scan bound |
| secg/secp112r2 | 112 | Weierstrass | True | |D_K| > 2000000 | -3147981784734289480448435252561803 | agree: database |cm_disc| is above the scan bound |
| secg/secp128r1 | 128 | Weierstrass | True | |D_K| > 2000000 | -1289276154342429602004523748928498472003 | agree: database |cm_disc| is above the scan bound |
| secg/secp128r2 | 128 | Weierstrass | True | |D_K| > 2000000 | -249813310894261997230170354175517944027 | agree: database |cm_disc| is above the scan bound |
| secg/secp160k1 | 160 | Weierstrass | True | D_K = -3, conductor 709316441754974472566021 | -3 | agree |
| secg/secp160r1 | 160 | Weierstrass | True | |D_K| > 2000000 | -253299265357051288026316368812641220149079098987 | agree: database |cm_disc| is above the scan bound |
| secg/secp160r2 | 160 | Weierstrass | True | |D_K| > 2000000 | -5783078062867254786698681388093463102802039991163 | agree: database |cm_disc| is above the scan bound |
| secg/secp192k1 | 192 | Weierstrass | True | D_K = -3, conductor 34999138709524326971400529393 | -3 | agree |
| secg/secp192r1 | 192 | Weierstrass | True | |D_K| > 2000000 | -24109379060336110122544161233113975664949272517896865359515 | agree: database |cm_disc| is above the scan bound |
| secg/secp224k1 | 224 | Weierstrass | True | D_K = -3, conductor 2181384198222797443972610423981457 | -3 | agree |
| secg/secp224r1 | 224 | Weierstrass | True | |D_K| > 2000000 | -9493061114565352281698673660738078664961855212656825491744070162387 | agree: database |cm_disc| is above the scan bound |
| secg/secp256k1 | 256 | Weierstrass | True | D_K = -3, conductor 303414439467246543595250775667605759171 | -3 | agree |
| secg/secp256r1 | 256 | Weierstrass | True | |D_K| > 2000000 | -455213823400003756884736869668539463648899917731097708475249543966132856781915 | agree: database |cm_disc| is above the scan bound |
| secg/secp384r1 | 384 | Weierstrass | True | |D_K| > 2000000 |  | database has no cm_disc |
| secg/secp521r1 | 521 | Weierstrass | True | |D_K| > 2000000 |  | database has no cm_disc |
| secg/sect113r1 | 113 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| secg/sect113r2 | 113 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| secg/sect131r1 | 131 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| secg/sect131r2 | 131 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| secg/sect163k1 | 163 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| secg/sect163r1 | 163 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| secg/sect163r2 | 163 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| secg/sect193r1 | 193 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| secg/sect193r2 | 193 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| secg/sect233k1 | 233 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| secg/sect233r1 | 233 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| secg/sect239k1 | 239 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| secg/sect283k1 | 283 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| secg/sect283r1 | 283 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| secg/sect409k1 | 409 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| secg/sect409r1 | 409 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| secg/sect571k1 | 571 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| secg/sect571r1 | 571 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| wtls/wap-wsg-idm-ecid-wtls1 | 113 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| wtls/wap-wsg-idm-ecid-wtls10 | 233 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| wtls/wap-wsg-idm-ecid-wtls11 | 233 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| wtls/wap-wsg-idm-ecid-wtls12 | 224 | Weierstrass | True | |D_K| > 2000000 | -9493061114565352281698673660738078664961855212656825491744070162387 | agree: database |cm_disc| is above the scan bound |
| wtls/wap-wsg-idm-ecid-wtls3 | 163 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| wtls/wap-wsg-idm-ecid-wtls4 | 113 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| wtls/wap-wsg-idm-ecid-wtls5 | 163 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| wtls/wap-wsg-idm-ecid-wtls6 | 112 | Weierstrass | True | |D_K| > 2000000 | -17787316666415881930611191403938683 | agree: database |cm_disc| is above the scan bound |
| wtls/wap-wsg-idm-ecid-wtls7 | 160 | Weierstrass | True | |D_K| > 2000000 | -253299265357051288026316368812641220149079098987 | agree: database |cm_disc| is above the scan bound |
| wtls/wap-wsg-idm-ecid-wtls8 | 112 | Weierstrass | True | D_K = -3, conductor 22505355654482883 | -3 | agree |
| wtls/wap-wsg-idm-ecid-wtls9 | 160 | Weierstrass | True | D_K = -3, conductor 602889891024722752429129 | -3 | agree |
| x962/c2onb191v4 | 191 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x962/c2onb191v5 | 191 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x962/c2onb239v4 | 239 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x962/c2onb239v5 | 239 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x962/c2pnb163v1 | 163 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x962/c2pnb163v2 | 163 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x962/c2pnb163v3 | 163 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x962/c2pnb176w1 | 176 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x962/c2pnb208w1 | 208 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x962/c2pnb272w1 | 272 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x962/c2pnb304w1 | 304 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x962/c2pnb368w1 | 368 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x962/c2tnb191v1 | 191 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x962/c2tnb191v2 | 191 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x962/c2tnb191v3 | 191 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x962/c2tnb239v1 | 239 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x962/c2tnb239v2 | 239 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x962/c2tnb239v3 | 239 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x962/c2tnb359v1 | 359 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x962/c2tnb431r1 | 431 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x962/prime192v1 | 192 | Weierstrass | True | |D_K| > 2000000 | -24109379060336110122544161233113975664949272517896865359515 | agree: database |cm_disc| is above the scan bound |
| x962/prime192v2 | 192 | Weierstrass | True | |D_K| > 2000000 | -8508537682795299515966795575171558583771913113808038681755 | agree: database |cm_disc| is above the scan bound |
| x962/prime192v3 | 192 | Weierstrass | True | |D_K| > 2000000 | -23398457627284768072498712732199139750912039893615971726995 | agree: database |cm_disc| is above the scan bound |
| x962/prime239v1 | 239 | Weierstrass | True | |D_K| > 2000000 | -3276719900979335157733880957682440032142593122090581849796915666027643267 | agree: database |cm_disc| is above the scan bound |
| x962/prime239v2 | 239 | Weierstrass | True | |D_K| > 2000000 | -94846201560655389285771496704415635167710528988786515152953085998690731 | agree: database |cm_disc| is above the scan bound |
| x962/prime239v3 | 239 | Weierstrass | True | |D_K| > 2000000 | -3238534204579671259055512106716992615534505004818537644697468102519225435 | agree: database |cm_disc| is above the scan bound |
| x962/prime256v1 | 256 | Weierstrass | True | |D_K| > 2000000 | -455213823400003756884736869668539463648899917731097708475249543966132856781915 | agree: database |cm_disc| is above the scan bound |
| x963/ansip160k1 | 160 | Weierstrass | True | D_K = -3, conductor 709316441754974472566021 | -3 | agree |
| x963/ansip160r1 | 160 | Weierstrass | True | |D_K| > 2000000 | -253299265357051288026316368812641220149079098987 | agree: database |cm_disc| is above the scan bound |
| x963/ansip160r2 | 160 | Weierstrass | True | |D_K| > 2000000 | -5783078062867254786698681388093463102802039991163 | agree: database |cm_disc| is above the scan bound |
| x963/ansip192k1 | 192 | Weierstrass | True | D_K = -3, conductor 34999138709524326971400529393 | -3 | agree |
| x963/ansip224k1 | 224 | Weierstrass | True | D_K = -3, conductor 2181384198222797443972610423981457 | -3 | agree |
| x963/ansip224r1 | 224 | Weierstrass | True | |D_K| > 2000000 | -9493061114565352281698673660738078664961855212656825491744070162387 | agree: database |cm_disc| is above the scan bound |
| x963/ansip256k1 | 256 | Weierstrass | True | D_K = -3, conductor 303414439467246543595250775667605759171 | -3 | agree |
| x963/ansip384r1 | 384 | Weierstrass | True | |D_K| > 2000000 |  | database has no cm_disc |
| x963/ansip521r1 | 521 | Weierstrass | True | |D_K| > 2000000 |  | database has no cm_disc |
| x963/ansit163k1 | 163 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x963/ansit163r1 | 163 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x963/ansit163r2 | 163 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x963/ansit193r1 | 193 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x963/ansit193r2 | 193 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x963/ansit233k1 | 233 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x963/ansit233r1 | 233 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x963/ansit239k1 | 239 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x963/ansit283k1 | 283 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x963/ansit283r1 | 283 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x963/ansit409k1 | 409 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x963/ansit409r1 | 409 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x963/ansit571k1 | 571 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
| x963/ansit571r1 | 571 | Weierstrass | skipped | field type Binary: outside the prime-field pipeline | | |
