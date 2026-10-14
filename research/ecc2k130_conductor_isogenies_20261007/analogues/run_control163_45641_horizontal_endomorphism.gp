\\ Fail-closed entry point for the K-163 horizontal control.
\\ Canonical invocation:
\\   gp -q -f -s 64M run_control163_45641_horizontal_endomorphism.gp
FAIL_CLOSED_DRIVER = 1;
RUN_COMPLETE = 0;
{iferr(read("control163_45641_horizontal_endomorphism.gp"), run_error,
  print("RESULT=FAIL reason=uncaught_gp_exception detail=", run_error);
  quit(1)
)};
{if(RUN_COMPLETE != 1,
  print("RESULT=FAIL reason=implementation_returned_without_completion_sentinel");
  quit(1)
)};
FAIL_CLOSED_DRIVER = 0;
RUN_COMPLETE = 0;
