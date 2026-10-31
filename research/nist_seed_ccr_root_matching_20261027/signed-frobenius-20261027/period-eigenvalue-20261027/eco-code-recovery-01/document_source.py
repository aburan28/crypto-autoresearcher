"""Create write-once reading notes and a qualified package version record."""
import gzip
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent


def binding(p):
    b = p.read_bytes()
    return {'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}


record = {
    'provenance': 'retrieved', 'verified_by': 'Codex /root, T-5518',
    'author': 'Frank J. Lehmann', 'title_page_date': '1994-07-29',
    'title': 'Implementierung von Algorithmen zur Berechnung modularer Polynome und deren Anwendung im Algorithmus von Atkin',
    'ps_creation_header': 'Tue Oct 18 16:10:42 1994',
    'tex_source_header': '1994.10.18:1602', 'pages': 125,
    'archive_capture': '19970731071932',
    'url': 'https://web.archive.org/web/19970731071932id_/http://www.cs.uni-sb.de:80/users/mdenny/Bewohner/lehmann/lehmann.diplom.ps',
    'discovery': '1997 archived Muller author page -> Lehmann author homepage -> uncompressed lehmann.diplom.ps link; exact CDX lookup.',
    'read_scope': ['title/date and contents', 'chapter2 pp16-24',
                   'chapter4 pp57-62', 'chapter5 pp63-68 and79-89',
                   'chapter6 pp90-95,108,110,116-117', 'chapter7 pp118-122'],
    'visually_inspected_pdf_pages': [1, 25, 67, 93, 120, 122],
    'printed_page_offset_from_pdf': -1,
    'conversion': {'tool': 'Ghostscript10.08.0', 'flags': ['-dSAFER','-dBATCH','-dNOPAUSE','-sDEVICE=pdfwrite'],
                   'exit_code': 0, 'original_ps_unmodified': True,
                   'text': 'pdftotext -layout',
                   'page_render_note': 'pdftoppm returned exit0 with Type3 glyph bounding-box warnings; the six selected pages were legible and inspected.'},
    'private_sources': {n: binding(P/'.work'/n) for n in ['lehmann-1994-ps.bin','lehmann-1994.pdf','lehmann-1994.txt']},
    'observations': [
        {'printed_pages': [23,24,57,59,62], 'fact': 'Curve interface evaluates the integer modular polynomial at J=j(E), reduces modulo p, and uses splitting types; no input cube-root-of-j operation is specified.'},
        {'printed_pages': [64,66,85,86], 'fact': 'Type1 eta-quotient construction and Weber formula compute formal q-series and integer coefficient tables; the cube in j=(f2^24+16)^3/f2^24 is a forward formula in precomputation.'},
        {'printed_pages': [92,94], 'fact': 'Type2 Hecke-index conditions depend on auxiliary l and chosen index n, not curve input p,j or CM conductor.'},
        {'printed_pages': [85,86,119], 'fact': 'Integer table construction combines coefficients modulo small primes by CRT and heuristically stops after two unchanged iterations; validation is by counting on test inputs.'},
        {'printed_pages': [120,121], 'fact': 'Tables are stored as out... ASCII files; atobin uses libI long-integer structures for .bin conversion, bintoa converts back. The thesis reports one equivalent polynomial for every prime l<800.'},
        {'printed_pages': [121,122], 'fact': 'Named routines include lmod_equ, examine_l, lcompute_eta_de/sp, lcompute_f, lcompute_j, lcompute_A, lcompute_ark and lcompute_ars. The original bodies and output coefficient files were not recovered here.'},
    ],
    'limits': ['Reading notes are not a proof of every theorem in the thesis.',
               'The 1997 archive capture authenticates these preserved bytes, not NIST use.',
               'A heuristic precomputation stop is not a demonstrated erroneous table or curve rejection.',
               'Original caller, file deployment and candidate visitation remain unknown.'],
    'new_scientific_trials': 0, 'historical_criterion_identified': False,
}
version = {
    'package_sha256': '0189dcbb3daab55cb39f213bf612d025b71aac6bd4ca7a5c09b687f47c98d387',
    'readme_declared_version': '1.3', 'version_header_declared_version': '1.2.0',
    'version_header_lines': [13,14,15],
    'version_header_sha256': binding(P/'.work/version.h')['sha256'],
    'readme_sha256': binding(P/'.work/Readme')['sha256'],
    'qualification': 'Advertised1.3 bundle captured May1997; internal version header remains1.2.0. The discrepancy is preserved and is not normalized.',
    'semantic_inspection': [
        {'file': 'LiDIA/src/packages/Fp_polynomial/factoring.c', 'lines': [423,427,452,479,483,525],
         'observation': 'Generic compute_degree/prob_compute_degree/find_root routines; a point-counting-use comment is present, but this is not the eco caller. The probabilistic degree function documents possible0/too-large output.'},
        {'file': 'LiDIA/include/LiDIA/lip.h', 'lines': [2023,2211,2335],
         'observation': 'Elliptic references concern ECM factorization and its RNG, not SEA curve counting.'},
        {'file': 'LiDIA/src/kernel/integers/lip/lip.c', 'lines': [9612],
         'observation': 'Actual ECM curve setup code. It is not a SEA counter; no blanket absence of elliptic arithmetic is asserted.'},
    ],
    'release_announcements': [
        {'url': 'https://math.albany.edu/g/Math/Comp/cas/LiDIA-feb97', 'date': '1997-02-05',
         'finding': 'Counting points over Fp p>3 remains listed as in work.'},
        {'url': 'https://math.albany.edu/g/Math/Comp/cas/LiDIA-feb2000', 'date': '2000-02-02',
         'release_description': 'Alpha of next release2.0',
         'finding': 'The SEA package uses LiDIA but is explicitly outside the free distribution.'},
    ],
    'limits': 'This explains why a general LiDIA tarball need not contain the point counter. It does not identify NIST software, a historical input rejection or a missing mathematical criterion.',
}
for n, data in {'SOURCE-REVIEW.json': record, 'PACKAGE-VERSION-NOTE.json': version}.items():
    assert not (P/n).exists()
    (P/n).write_text(json.dumps(data, indent=2, sort_keys=True)+'\n')
assert not (P/'package-members.csv.gz').exists()
(P/'package-members.csv.gz').write_bytes(gzip.compress((P/'package-members.csv').read_bytes(),mtime=0))
print('Source reading notes, version discrepancy and compressed inventory retained.')
