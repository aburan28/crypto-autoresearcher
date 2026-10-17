"""Check that every number in a .tex source appears in the committed PDF's pdftotext output.

Usage: python3 -I -B tex_pdf_numbers.py <tex> <pdftotext.txt> [<tex> <txt> ...]
Numbers: digit runs with LaTeX thin-space/{,} grouping collapsed; PDF text has
spaces/commas between digit groups collapsed the same way. Comment lines skipped.
"""
import re
import sys


def norm_tex(s):
    s = "\n".join(l for l in s.splitlines() if not l.lstrip().startswith("%"))
    s = re.sub(r"(\d)\\,(\d)", r"\1\2", s)
    s = re.sub(r"(\d)\{,\}(\d)", r"\1\2", s)
    return s


def norm_pdf(s):
    s = re.sub(r"(\d)[   ](?=\d{3}\b)", r"\1", s)
    s = re.sub(r"(\d),(?=\d{3}\b)", r"\1", s)
    s = re.sub(r"\s+", " ", s)
    return s


args = sys.argv[1:]
for tex, txt in zip(args[0::2], args[1::2]):
    t = norm_tex(open(tex, encoding="utf-8").read())
    body = t.split("\\begin{document}", 1)[-1]
    p = norm_pdf(open(txt, encoding="utf-8").read())
    nums = sorted(set(re.findall(r"(?<![A-Za-z\\])\d+(?:\.\d+)?", body)), key=lambda x: (len(x), x))
    pdf_nums = set(re.findall(r"\d+(?:\.\d+)?", p))
    missing = [n for n in nums if n not in pdf_nums and n not in p]
    print(f"{tex}: {len(nums)} distinct numbers; missing from PDF text: {missing if missing else 'none'}")
