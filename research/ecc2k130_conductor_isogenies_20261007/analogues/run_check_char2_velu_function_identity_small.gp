\\ Fail-closed entry point for the bounded degree-seven identity fixture.
FAIL_CLOSED_DRIVER = 1;
RUN_COMPLETE = 0;
{iferr(read("check_char2_velu_function_identity_small.gp"), run_error,
  print("RESULT=FAIL reason=uncaught_gp_exception detail=", run_error);
  quit(1)
)};
{if(RUN_COMPLETE != 1,
  print("RESULT=FAIL reason=implementation_returned_without_completion_sentinel");
  quit(1)
)};
FAIL_CLOSED_DRIVER = 0;
RUN_COMPLETE = 0;
