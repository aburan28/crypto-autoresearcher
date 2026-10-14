\\ Fail-closed entry point for the fresh seed endpoint validator.
\\ Canonical invocation:
\\   gp -q -f -s 1G run_verify163_45641_seed_endpoint.gp
FAIL_CLOSED_DRIVER = 1;
RUN_COMPLETE = 0;
{iferr(read("verify163_45641_seed_endpoint.gp"), run_error,
  print("ENDPOINT_FLOOR_CERTIFICATE FAIL reason=uncaught_gp_exception detail=", run_error);
  quit(1)
)};
{if(RUN_COMPLETE != 1,
  print("ENDPOINT_FLOOR_CERTIFICATE FAIL reason=implementation_returned_without_completion_sentinel");
  quit(1)
)};
FAIL_CLOSED_DRIVER = 0;
RUN_COMPLETE = 0;
