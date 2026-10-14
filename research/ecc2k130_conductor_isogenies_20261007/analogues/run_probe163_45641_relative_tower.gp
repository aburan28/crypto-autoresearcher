\\ Fail-closed entry point for the bounded K-163 relative-tower probe.
\\ Canonical invocation:
\\   gp -q -f -s 64M --default parisizemax=1G run_probe163_45641_relative_tower.gp
FAIL_CLOSED_DRIVER = 1;
RUN_COMPLETE = 0;
{iferr(read("probe163_45641_relative_tower.gp"), run_error,
  print("RESULT=FAIL reason=uncaught_gp_exception detail=", run_error);
  quit(1)
)};
{if(RUN_COMPLETE != 1,
  print("RESULT=FAIL reason=implementation_returned_without_completion_sentinel");
  quit(1)
)};
FAIL_CLOSED_DRIVER = 0;
RUN_COMPLETE = 0;
