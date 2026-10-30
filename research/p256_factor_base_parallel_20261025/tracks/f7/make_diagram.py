from pathlib import Path
import html,json
p=Path(__file__).parent;sid=json.loads((p/'source-identity.json').read_text())['curve_uid']
s=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="760" viewBox="0 0 1500 760">
<defs><marker id="a" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 Z" fill="#245975"/></marker></defs>
<rect width="1500" height="760" fill="white"/>
<g font-family="sans-serif" fill="#142d40">
<text x="30" y="36" font-size="25">F7: same-field covers and subgroup-compatible divisor maps</text>
<text x="30" y="65" font-size="15">TASK-20261025-7144c5; p is the published P-256 prime throughout</text>
<rect x="30" y="270" width="630" height="145" rx="12" fill="#edf5fa" stroke="#245975"/>
<text x="48" y="300" font-size="22">E: y²=x³−3x+b; #E(Fp)=r</text>
<text x="48" y="327" font-size="10">{html.escape(sid)}</text>
<text x="48" y="355" font-size="17">source divisor class [P−O], order r</text>
<text x="48" y="385" font-size="17">r odd: norm o pullback=[2] is invertible</text>
<rect x="875" y="110" width="590" height="215" rx="12" fill="#eaf6ef" stroke="#297b50"/>
<text x="895" y="140" font-size="22">C: U⁴=X³Z−3XZ³+bZ⁴</text>
<text x="895" y="171" font-size="19">smooth plane quartic; genus 3</text>
<text x="895" y="201" font-size="18">nonhyperelliptic; branch orbits [1,3]</text>
<text x="895" y="230" font-size="17">pi(x,u)=(x,u²); degree 2 over Fp</text>
<text x="895" y="261" font-size="16">J_C ~ E × Prym; target image has order r</text>
<text x="895" y="290" font-size="15">Frobenius: (T²−tT+p)(T⁴+A T²+p²); A unknown</text>
<rect x="875" y="405" width="590" height="215" rx="12" fill="#f9f0e5" stroke="#98632e"/>
<text x="895" y="436" font-size="22">C₂: w²=z⁶−3z²+b</text>
<text x="895" y="467" font-size="19">hyperelliptic; genus 2</text>
<text x="895" y="498" font-size="18">pi₂(z,w)=(z²,w); degree 2 over Fp</text>
<text x="895" y="528" font-size="17">branch at two points above x=0</text>
<text x="895" y="558" font-size="16">J_C₂ ~ E × B, B: Y²=X³−3X²+b²</text>
<text x="895" y="588" font-size="16">t_B=167631093631314538742209370567683050917</text>
<path d="M660 310 C745 310,780 215,870 215" stroke="#245975" stroke-width="2" fill="none" marker-end="url(#a)"/>
<text x="696" y="224" font-size="17">pi*: E → J_C</text>
<text x="696" y="247" font-size="14">fibre minus 2∞</text>
<path d="M660 375 C745 375,780 515,870 515" stroke="#245975" stroke-width="2" fill="none" marker-end="url(#a)"/>
<text x="690" y="455" font-size="17">pi₂*: E → J_C₂</text>
<text x="690" y="478" font-size="14">fibre minus ∞₊−∞₋</text>
<text x="30" y="675" font-size="20">14 exact fibre checks; Fp-stable divisors may have supports in Fp².</text>
<text x="30" y="707" font-size="18">A destination solver for the injected E component, relation rank and full costs remain open.</text>
<text x="30" y="737" font-size="16">Maps and genus do not establish a DLP speedup. Evidence: checks.json; elliptic-quotient-checks.json.</text>
</g></svg>'''
(p/'diagram.svg').write_text(s+'\n')
