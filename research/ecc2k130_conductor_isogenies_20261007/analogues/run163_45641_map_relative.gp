\\ Direct-input driver for the relative-tower K-163 degree-45641 forward
\\ producer.  Stack sizing must happen before read(); loading this driver
\\ through read() is unsupported for the same reason as the original driver.
\\
\\ CLAIM BOUNDARY: this is an unexecuted implementation, not an admitted
\\ scientific run.  Do not launch it until a committed EXP contract, frozen
\\ trial plan, checker, queue/handoff, and execution owner admit the run.
default(parisizemax, "14G");
default(parisize, "4G");

OUT = "kernel163_45641_map_relative.txt";
RUN_COMPLETE = 0;
iferr(read("kernel163_45641_map_relative.gp"), E, print("RESULT=FAIL reason=uncaught_gp_error detail=", E); quit(1));
if(RUN_COMPLETE != 1, print("RESULT=FAIL reason=producer_returned_without_completion_sentinel"); quit(1));
