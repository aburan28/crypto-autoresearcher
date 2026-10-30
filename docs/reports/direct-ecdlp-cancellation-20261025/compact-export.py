#!/usr/bin/env python3
"""Re-export four unsealed ECDLP PDFs; never runs a scientific experiment.

Read all Markdown/figures from --repo-root. Write only --out-dir. The historical
rebuilt-programme PDF is an explicitly marked derivative, not its old run file.
Requires pandoc, XeLaTeX, newunicodechar, seqsplit, Graphviz, Ghostscript, PyMuPDF,
and the installed URW NimbusRoman OTF. Original report sources are unchanged.
"""
from pathlib import Path
import argparse, json, shutil, subprocess, tempfile, zlib
import fitz

BASE = 'docs/reports/direct-ecdlp-cancellation-20261025'
PILOT = 'experiments/EXP-ECDLP-fe3337/reports/run-20261025T0526Z'
PATHS = [BASE+'/report.pdf', BASE+'/programme/report.pdf',
         BASE+'/programme/executions/20261025T040202Z/rebuilt-programme.pdf',
         PILOT+'/report.pdf']
HEADER = r'''\setmainfont[Path=/usr/share/fonts/opentype/urw-base35/,BoldFont=NimbusRoman-Regular.otf,ItalicFont=NimbusRoman-Regular.otf,BoldItalicFont=NimbusRoman-Regular.otf,RawFeature={-kern,-liga,-clig}]{NimbusRoman-Regular.otf}
\setsansfont[Path=/usr/share/fonts/opentype/urw-base35/,BoldFont=NimbusRoman-Regular.otf,ItalicFont=NimbusRoman-Regular.otf,BoldItalicFont=NimbusRoman-Regular.otf,RawFeature={-kern,-liga,-clig}]{NimbusRoman-Regular.otf}
\setmonofont[Path=/usr/share/fonts/opentype/urw-base35/,BoldFont=NimbusRoman-Regular.otf,ItalicFont=NimbusRoman-Regular.otf,BoldItalicFont=NimbusRoman-Regular.otf,RawFeature={-kern,-liga,-clig}]{NimbusRoman-Regular.otf}
\usepackage{newunicodechar}
\newunicodechar{₂}{\textsubscript{2}}
\newunicodechar{⁻}{\textsuperscript{-}}
'''
PLANNING_EXTRA = r'''\usepackage{seqsplit}
\let\originaltexttt\texttt
\renewcommand{\texttt}[1]{\originaltexttt{\seqsplit{#1}}}
'''

def encode_content(data):
    """Replace actual PDF hex-string tokens by equivalent binary literals.

    Skip nested literal strings, comments and dictionary delimiters. Glyph codes
    and all text/position/font operators remain unchanged. No text is rebuilt.
    """
    out=bytearray();i=0
    while i<len(data):
        c=data[i]
        if c==37:  # comment
            end=data.find(b'\n',i)
            if end<0:out.extend(data[i:]);break
            out.extend(data[i:end+1]);i=end+1;continue
        if c==40:  # existing literal string
            start=i;i+=1;depth=1
            while i<len(data) and depth:
                if data[i]==92:i+=2;continue
                if data[i]==40:depth+=1
                elif data[i]==41:depth-=1
                i+=1
            out.extend(data[start:i]);continue
        if c==60 and i+1<len(data) and data[i+1]!=60:
            end=data.find(b'>',i+1)
            if end>=0:
                raw=b''.join(data[i+1:end].split())
                if all(x in b'0123456789abcdefABCDEF' for x in raw):
                    if len(raw)%2:raw+=b'0'
                    v=bytes.fromhex(raw.decode('ascii'))
                    v=v.replace(b'\\',b'\\\\').replace(b'(',b'\\(').replace(b')',b'\\)').replace(b'\r',b'\\r').replace(b'\n',b'\\n')
                    out.extend(b'('+v+b')');i=end+1;continue
        if c==60 and i+1<len(data) and data[i+1]==60:
            out.extend(b'<<');i+=2;continue
        out.append(c);i+=1
    return bytes(out)

def packed(src,dst):
    d=fitz.open(src);contents={x for p in d for x in p.get_contents()}
    for x in range(1,d.xref_length()):
        if not d.xref_is_stream(x):continue
        if x not in contents and '/Subtype /Form' not in d.xref_object(x):continue
        before=d.xref_stream(x);after=encode_content(before)
        if after!=before:
            d.update_stream(x,zlib.compress(after,9),compress=False)
            d.xref_set_key(x,'Filter','/FlateDecode')
    interim=dst.with_suffix('.packing.pdf')
    d.save(interim,garbage=4,deflate=False,use_objstms=1)
    d=fitz.open(interim)
    d.save(dst,garbage=4,deflate=True,use_objstms=1,compression_effort=100)
    interim.unlink()
    # A content-representation change must preserve every rendered page exactly.
    a=fitz.open(src);b=fitz.open(dst);assert len(a)==len(b)
    for pa,pb in zip(a,b):
        xa=pa.get_pixmap(alpha=False);xb=pb.get_pixmap(alpha=False)
        assert (xa.width,xa.height,xa.samples)==(xb.width,xb.height,xb.samples)
    assert dst.stat().st_size<=65536,(dst,dst.stat().st_size)

def run(cmd,cwd,log):
    p=subprocess.run(cmd,cwd=cwd,text=True,capture_output=True)
    log.write_text(p.stdout+p.stderr)
    if p.returncode:raise RuntimeError(log)
    if 'Missing character:'in p.stderr:raise RuntimeError('Missing glyph: '+str(log))

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--repo-root',type=Path,required=True)
p.add_argument('--out-dir',type=Path,required=True)
a=p.parse_args();repo=a.repo_root.resolve();out=a.out_dir.resolve();out.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='compact-exports-',dir=out) as td:
    work=Path(td);header=work/'header.tex';header.write_text(HEADER)
    plan_header=work/'planning-header.tex';plan_header.write_text(HEADER+PLANNING_EXTRA)
    dot=(repo/BASE/'programme/programme.dot').read_text().replace('DejaVu Sans','Times-Roman')
    (work/'programme.dot').write_text(dot)
    run(['dot','-Teps',str(work/'programme.dot'),'-o',str(work/'programme.eps')],work,out/'diagram-dot.log')
    run(['gs','-q','-dNOPAUSE','-dBATCH','-sDEVICE=pdfwrite','-dEPSCrop','-dEmbedAllFonts=false','-sOutputFile='+str(work/'programme.pdf'),str(work/'programme.eps')],work,out/'diagram-gs.log')
    d=fitz.open(work/'programme.pdf');seen=set()
    for pg in d:
        for f in pg.get_fonts(full=True):
            if f[0] in seen:continue
            seen.add(f[0]);assert f[3].split('+')[-1]=='Times-Roman' and f[2]=='Type1',f
            # Standard PDF Base14 Times-Roman, not a custom unembedded font.
            d.xref_set_key(f[0],'BaseFont','/Times-Roman')
            d.xref_set_key(f[0],'FontDescriptor','null')
    d.save(work/'programme-base14.pdf',garbage=4,deflate=True,use_objstms=1)
    for i,folder,margin in [(0,BASE,20),(1,BASE+'/programme',18),(3,PILOT,18)]:
        source=(repo/folder/'report-source.md').read_text()
        if i==1:source=source.replace('(programme.pdf)','('+str(work/'programme-base14.pdf')+')')
        md=work/(str(i)+'-source.md');md.write_text(source)
        raw=work/(str(i)+'-typeset.pdf')
        run(['pandoc',str(md),'--standalone','--from=markdown+tex_math_dollars','--pdf-engine=xelatex','-H',str(plan_header if i==0 else header),'-V',f'geometry:margin={margin}mm','-V','fontsize=10pt','-V','colorlinks=true','-V','urlcolor=blue','-o',str(raw)],repo/folder,out/(str(i)+'-build.log'))
        target=out/PATHS[i];target.parent.mkdir(parents=True,exist_ok=True);packed(raw,target)
    target=out/PATHS[2];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/PATHS[1],target)
print(json.dumps({'exports':[{'path':x,'bytes':(out/x).stat().st_size}for x in PATHS]},indent=2))
