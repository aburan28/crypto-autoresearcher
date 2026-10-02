import importlib.util, json, sys
spec = importlib.util.spec_from_file_location("rw", "/home/user/crypto-autoresearcher/experiments/EXP-PFDR-1b78f7/amd-1de84f/run_wrapper.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
json.dump(m.environment(), open(sys.argv[1], "w"), indent=2, sort_keys=True)
