\\ Compatibility probe for the deterministic seed used by
\\ kernel163_45641_map.gp.  This stops after constructing one endpoint;
\\ it does not construct a kernel polynomial or point map.
\\ Execute through run_probe163_45641_seed.gp.
{if(type(FAIL_CLOSED_DRIVER) != "t_INT" || FAIL_CLOSED_DRIVER != 1,
  print("SEED_PREFLIGHT FAIL reason=use_run_probe163_45641_seed_driver");
  quit(1)
)};
if(getenv("GP_FAIL_CLOSED_FAULT") == "1", error("injected fail-closed fault"));

setrand(45641);
MOD = x^163 + x^7 + x^6 + x^3 + 1;
m = 163;
a = 1;
lp = 45641;
k = 20;
twist = 1;
NISO = 1;
MAX_TRIES = 100000;
read("probe163_45641_seed_bounded.inc.gp");

expected = 24362196697750487851526857852297647817644684697;
historical = Set([20183018253319052689704116247546275258431720285, 1699056145793825809974781818934579013935268431, 71177121262957429327531167482112665894165601519, 86418753047285346854356540661746105839786105877, 41105051057298702718687969060611106606052833369, 9458681452661928675008670406069307198816595651]);
{must(ok, message) =
  if(!ok,
    print("SEED_PREFLIGHT FAIL reason=", message);
    quit(1)
  )
};
must(res[1][1] == expected, "seed-45641 endpoint replay mismatch");
archive_match = setsearch(historical, res[1][1]) != 0;
must(!archive_match, "probe unexpectedly reproduced a historical sample");
print("SEED_PREFLIGHT expected=PASS historical_allow_list_match=", archive_match);
RUN_COMPLETE = 1;
