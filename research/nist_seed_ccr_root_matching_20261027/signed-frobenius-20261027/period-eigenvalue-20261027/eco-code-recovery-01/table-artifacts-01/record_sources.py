"""Retain reading notes and exact source identities; no historical execution."""
import datetime
import hashlib
import json
from pathlib import Path

P=Path(__file__).resolve().parent


def bind(p):
    b=p.read_bytes()
    return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}


copied=P/'.work/later-meq-prime.cc'
body=copied.read_bytes()
assert body.endswith(b'\n\n')
body=body[:-1]
blob=hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()
assert blob=='01bec36819fde2ea247872e6add0ed578fe3bdbb'
canonical=P/'.work/later-meq-prime-exact.cc'
assert not canonical.exists();canonical.write_bytes(body)
later={
    'provenance':'retrieved', 'verified_by':'Codex /root, T-5518',
    'repository':'passagemath/upstream-LiDIA',
    'commit':'23dac491f4cd96eb7de648a5cf90eb9ec77653c8',
    'path':'src/ec_order/eco_gfp/eco_gfp/meq_prime.cc',
    'url':'https://github.com/passagemath/upstream-LiDIA/blob/23dac491f4cd96eb7de648a5cf90eb9ec77653c8/src/ec_order/eco_gfp/eco_gfp/meq_prime.cc',
    'Git_blob_sha1':blob, **bind(canonical),
    'version_limit':'Later2.3.0+latte-patches-2019-05-02 lineage; not authenticated1997.',
    'copy_note':'The initial apply_patch copy adds one final newline. That copy is retained; removing exactly that added newline produces the Git-blob-identical separate private file.',
    'read_scope':['get_filename_vector and ropen_meq_file pp322-535 lines',
                  'read_row_ascii/read_row_bin/read_row and build_poly_in_X/Y lines574-800'],
    'observations':[
        'LIDIA_ECO or LIDIA_ECO_DB chooses table directory; type2 appends _II.',
        'Priority is ASCII, .bin, .gz, .bin.gz, .bz2, .bin.bz2.',
        'Binary row readers call the selected bigint backend read_from_file.',
        'Polynomial construction calls the modulus-taking row reader, which handles compressed formats.',
    ],
}
review={
    'provenance':'retrieved','verified_by':'Codex /root, T-5518',
    'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'old_package_sha256':'0189dcbb3daab55cb39f213bf612d025b71aac6bd4ca7a5c09b687f47c98d387',
    'old_source_manifest':'OLD-IO-SOURCES.json',
    'old_interfaces':[
        {'backend':'libI','wrapper_lines':[845,864],'header_lines':[8,9,66],
         'format':'Three native int fields maxlength,length,sign, followed by length native unsigned-long DigitType digits.',
         'read_checks':'Only a pre-read feof test is shown; fread return counts are not checked by this wrapper.',
         'dependency':'File ABI, endianness, int/unsigned-long sizes and representation must agree with reader.'},
        {'backend':'GMP','wrapper_lines':[1015,1019],
         'format':'mpz_inp_raw/mpz_out_raw.',
         'header_comment':'Records exchange of binary versus text API bodies on9 January1997.',
         'limit':'This is a dated source comment; pre-change executable bodies were not obtained.'},
        {'backend':'FreeLIP','wrapper_lines':[962,966],'lip_c_lines':[7830,7890],
         'format':'zbfread/zbfwrite store native long words, including signed digit count and payload; limb representation also matters.',
         'read_checks':'zbfread checks fread/error outcomes, but the void LiDIA wrapper does not expose its return code.'},
    ],
    'deduction':'The generic binary interfaces do not define one backend-independent interchange format. A file/build compatibility condition is source-based. Curve-specific consequences require original file bytes, real level visitation and caller error/fallback policy.',
    'historical_use':'UNESTABLISHED',
    'original_atobin_bintoa_bodies_obtained':False,
    'native_IO_execution':False,
    'new_scientific_trials':0,
    'historical_criterion_identified':False,
    'cohort_historical_IO_predictions':{'published_undetermined':10,'omitted_undetermined':11},
}
snap_path=P/'.work/lidia-history-snapshot.bin'
snap=json.loads(snap_path.read_text())
assert snap['id']=='1a8893e6a86f444e8be8e7bda6cb34fb1735a00e'
assert snap['branches']=={} and snap['next_branch'] is None
history={
    'snapshot_url':'https://archive.softwareheritage.org/api/1/snapshot/1a8893e6a86f444e8be8e7bda6cb34fb1735a00e/?branches_count=100',
    'snapshot':snap, **bind(snap_path),
    'origin':'https://github.com/mkoeppe/LiDIA-history',
    'GitHub_repository_API_observation':{'repository_id':199946365,'advertised_size':0,'archived':True,'forks_count':0},
    'finding':'This preserved snapshot is empty despite earlier full-visit metadata; it supplies no historical source branches. This is not an absence proof for all other CVS/SVN archives.',
    'period_sites':[
        {'name':n,'capture':cap,'finding':'The captured page explicitly describes the counting package as outside the free distribution.'}
        for n,cap in [('lidia-feb1999','19990210121103'),('lidia-oct1999','19991007165750'),('lidia-aug2000','20000815081446')]
    ],
    'CDX_outcomes':{'saarland_filtered_empty':True,'three_prefix_timeouts':True,
                    'interpretation':'Bounded empty/failed queries do not prove original files were never published or no other archive survives.'},
}
search={
    'queries':['"lcompute_ark"','"examine_l.c" Lehmann','LiDIA modular equations download eco','"atobin" "modular"',
               '"LiDIA" "modular equations"','"LiDIA" "meq" "data"','"Lehmann" "atobin"','"lcompute" "ark" Lehmann'],
    'finding':'Search results did not supply the named original C bodies or table files; unrelated matches were not used as technical evidence.',
    'scope_limit':'Search-engine retrieval is neither complete code indexing nor a proof of nonexistence.',
}
for name,data in {'LATER-READER-SOURCE.json':later,'SOURCE-REVIEW.json':review,
                  'HISTORY-REVIEW.json':history,'SEARCH-NOTES.json':search}.items():
    q=P/name;assert not q.exists();q.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
print('Exact source and archive-availability notes retained.')
