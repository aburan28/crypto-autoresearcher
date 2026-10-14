\\ Fail-closed entry point for the deterministic absolute-field seed probe.
\\ Canonical invocation:
\\   gp -q -f -s 1G --default parisizemax=8G run_probe163_45641_seed.gp
FAIL_CLOSED_DRIVER = 1;
RUN_COMPLETE = 0;
{iferr(read("probe163_45641_seed.gp"), run_error,
  print("SEED_PREFLIGHT FAIL reason=uncaught_gp_exception detail=", run_error);
  quit(1)
)};
{if(RUN_COMPLETE != 1,
  print("SEED_PREFLIGHT FAIL reason=implementation_returned_without_completion_sentinel");
  quit(1)
)};
FAIL_CLOSED_DRIVER = 0;
RUN_COMPLETE = 0;
