"""Render versioned review-status diagrams from recorded findings; no math computation."""
from pathlib import Path
import json,textwrap
from reportlab.graphics.shapes import Drawing,Rect,String,Line,Polygon
from reportlab.graphics import renderSVG,renderPDF
from reportlab.lib import colors

records={
'crypto':(5,['Finite subgroup, additive maps, coprime degree + reverse identity','5 conditional transport/range statements: checked and independently reviewed','Open: constructed geometry/duality, costs and full historical coverage']),
'cryptanalysis':(4,['Field collision equations; prime-order injective scalar encoding','4 collision statements: checked and independently reviewed','Open: exact-order encoding, C refinement, composite enumeration and costs']),
'crypto-autoresearcher':(10,['Typed curve points, finite coefficients, scalar words and genuine free algebra','10 certificate/NCP statements: checked and independently reviewed','Open: parser/point bridges, reachability, onto/full kernel and history'])}
for repo,(count,boxes) in records.items():
 root=Path('/workspace')/repo/'research/lean_retrospective_20261018'
 data={'title':repo+': scoped independent review','boxes':boxes,'caption':'Review status of '+str(count)+' mapped declarations under their stated assumptions. Broader source/target claims remain open. No performance or security conclusion.','independent_math_review_revision':'aaccd2f5d0a801fd73209e2a51b587efbda3ee5e','workflow_closure_revision':'712435bf2ad76da941291ac960f68c59d17a708f','original_graph':'proof-chain.json (frozen producer snapshot; retained unchanged)'}
 (root/'proof-chain-reviewed.json').write_text(json.dumps(data,indent=2)+'\n')
 drawing=Drawing(540,350)
 drawing.add(String(12,326,data['title'],fontName='Helvetica-Bold',fontSize=14))
 for i,label in enumerate(boxes):
  y=246-i*76;drawing.add(Rect(12,y,516,56,rx=7,ry=7,fillColor=colors.HexColor('#eaf1fb' if i<2 else '#fff1db'),strokeColor=colors.HexColor('#274366')))
  for j,line in enumerate(textwrap.wrap(label,90)):drawing.add(String(24,y+35-j*14,line,fontName='Helvetica',fontSize=10))
  if i<2:
   drawing.add(Line(270,y,270,y-16));drawing.add(Polygon([266,y-12,274,y-12,270,y-18],fillColor=colors.black))
 for j,line in enumerate(textwrap.wrap(data['caption'],103)):drawing.add(String(12,50-j*13,line,fontName='Helvetica',fontSize=9))
 renderSVG.drawToFile(drawing,str(root/'proof-chain-reviewed.svg'))
 renderPDF.drawToFile(drawing,str(root/'proof-chain-reviewed.pdf'))
 print(repo+': rendered versioned JSON/SVG/PDF')
