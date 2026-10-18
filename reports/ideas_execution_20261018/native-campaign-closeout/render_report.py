from pathlib import Path
import json,hashlib,subprocess,html
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont("CampaignSans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("CampaignSansBold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
p=Path('reports/ideas_execution_20261018/native-campaign-closeout');d=json.loads((p/'actual-native-inventory.json').read_text());styles=getSampleStyleSheet();story=[]
for style in styles.byName.values():style.fontName='CampaignSans'
for key in ['Title','Heading1','Heading2']:styles[key].fontName='CampaignSansBold'
def para(s,style='BodyText'):story.append(Paragraph(html.escape(s),styles[style]));story.append(Spacer(1,6))
para('ECDLP worksheet execution: actual native closeout','Title');para('Descriptive operational record; no scientific interpretation or hypothesis/goal promotion.')
para('Published source snapshot: '+d['snapshot_commit']);para('Every retained attempt is counted, including invalid outputs and pre-scientific infrastructure failures. Independently recomputed checks do not replace either separately allocated primary route.')
counts=d['native_status_counts'];data=[['Native status','Actual RUNs']]+[[k,str(v)] for k,v in sorted(counts.items())];t=Table(data,colWidths=[300,100]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dde8ed')),('GRID',(0,0),(-1,-1),.4,colors.grey),('FONTNAME',(0,0),(-1,-1),'CampaignSans'),('FONTNAME',(0,0),(-1,0),'CampaignSansBold'),('PADDING',(0,0),(-1,-1),7)]));story.append(t);story.append(Spacer(1,10))
para(f'Total actual attempts: {d["attempt_count"]}. Verified receipt-bound artifact digests: {d["verified_bound_artifact_count"]}. Complete native reproductions in conditional18 mapping: {d["conditional18_scopes_with_complete_native_reproduction"]}/18.')
para('Scope and limits','Heading2');para('The historical audit did not name its eighteen contracts. The reproducible candidate set is conditional, not an authenticated reconstruction of audit membership. Six entries are unchanged legacy metadata reproductions; twelve finite scopes use two distinct primary routes. The explicit c9 descriptive successor retains both truncation conventions and the old definition gap. The adjacent nineteenth instrument is separate and retains its weak vocabulary/file-presence checker without independent arithmetic certification.')
para('Preserved scientific boundaries','Heading2');para('The original square-bias strict prediction misses; the slope scanner remains unscored. The finite chord-sign prediction is false although measurement controls and independent arithmetic agree. A control-valid negative observation is not discarded. No repeated deterministic value becomes a new proof, security estimate or general ECDLP advantage.')
para('Whole-ledger checks retain historical and intentionally preserved invalid-manifest errors. Exact current gate logs and their baseline delta accompany this report. Honest deterministic null seeds retain the separate integer-only schema discrepancy. No unavailable model, runbook, inference binding, or execution-proof certification is asserted.')
story.append(PageBreak());para('Conditional eighteen: exact original-to-execution mapping','Title');data=[['Original EXP suffix','Execution EXP suffix','Accepted / expected']]
for row in d['conditional18_mapping']:
 accepted=sum(s=='output_validated' for s in row['native_statuses']);data.append([row['original_experiment'].removeprefix('EXP-ECDLP-'),row['execution_experiment'].removeprefix('EXP-ECDLP-'),f'{accepted} / {row["expected_primary_runs"]}'])
t=Table(data,colWidths=[135,150,140]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dde8ed')),('GRID',(0,0),(-1,-1),.3,colors.grey),('FONTNAME',(0,0),(-1,-1),'CampaignSans'),('FONTNAME',(0,0),(-1,0),'CampaignSansBold'),('FONTSIZE',(0,0),(-1,-1),9),('PADDING',(0,0),(-1,-1),5)]));story.append(t);story.append(Spacer(1,8));a=d['adjacent19th'];para('Adjacent nineteenth: '+a['original_experiment']+' → '+a['execution_experiment']+'; actual stages '+str(a['actual_stage_runs'])+'; statuses '+', '.join(a['native_statuses'])+'.');para('Full exact commands, source/plan/environment hashes, metrics, prediction comparisons, raw files and actual failure details are in actual-native-inventory.json and the individual inspected reports. Dated earlier reports are preserved.');para('This grouped document summarizes native operational records; it does not perform independent claim-tier scientific review.')
SimpleDocTemplate(str(p/'report.pdf'),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=36,bottomMargin=36).build(story)
# Editable descriptive custody diagram, not an arithmetic proof graph.
dot='digraph custody { rankdir=LR; node [shape=box]; old [label="Frozen scientific fixtures\\nand criteria"]; source [label="Source-bound native plans\\nactual prospective approvals"]; runs [label="Fresh separate RUNs\\nall actual outcomes retained"]; raw [label="Exact isolated raw archives\\nGit/hash/queue checks"]; reports [label="Published raw → inspected reports\\ncontrols and predictions separate"]; old -> source -> runs -> raw -> reports; }\n';(p/'pipeline.dot').write_text(dot)
for fmt in ['svg','png']:subprocess.run(['dot','-T'+fmt,str(p/'pipeline.dot'),'-o',str(p/('pipeline.'+fmt))],check=True)
(p/'report-rendering.json').write_text(json.dumps({'report_pdf_sha256':hashlib.sha256((p/'report.pdf').read_bytes()).hexdigest(),'generator':'reportlab descriptive-only; editable Graphviz custody diagram','scientific_trials':0,'requires_visual_inspection':True},indent=2)+'\n')
print(p/'report.pdf')
