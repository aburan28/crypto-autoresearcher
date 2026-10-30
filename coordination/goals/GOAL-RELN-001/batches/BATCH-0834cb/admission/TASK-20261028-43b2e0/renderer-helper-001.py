import sys, pathlib, hashlib, datetime, resource, typst, importlib.metadata, json
root=pathlib.Path(sys.argv[1]).resolve()
assert importlib.metadata.version("typst")=="0.15.0"
native=pathlib.Path(typst.__file__).parent/"_typst.abi3.so"
assert hashlib.sha256(native.read_bytes()).hexdigest()=="00618956a34c4863319fdf5e8835ea743f1d3af9d993273d020c4591073d2ef9"
source=(root/"report.typ").read_text()
assert "#import" not in source and "#include" not in source
resource.setrlimit(resource.RLIMIT_AS,(2147483648,2147483648))
typst.compile(str(root/"report.typ"), output=str(root/"report.pdf"), root=str(root), font_paths=[str(root/"fonts")], ignore_system_fonts=True, package_path=str(root/"packages"), package_cache_path=str(root/"package-cache"), timestamp=datetime.datetime(2026,10,29,tzinfo=datetime.timezone.utc))
print(json.dumps({"typst_version":"0.15.0","pdf_sha256":hashlib.sha256((root/"report.pdf").read_bytes()).hexdigest(),"pdf_bytes":(root/"report.pdf").stat().st_size,"maximum_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,"shell_execution":False}))
