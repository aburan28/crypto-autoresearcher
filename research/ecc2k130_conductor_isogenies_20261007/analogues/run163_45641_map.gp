\\ PARI abandons the remainder of a file loaded by read() when that file
\\ grows the stack.  Size the stack here, while this driver is GP's direct
\\ input, before loading the implementation.
default(parisizemax, "14G");
default(parisize, "4G");

OUT = "kernel163_45641_map.txt";
RUN_COMPLETE = 0;
iferr(read("kernel163_45641_map.gp"), E, print("RESULT=FAIL reason=uncaught_gp_error detail=", E); quit(1));
if(RUN_COMPLETE != 1, print("RESULT=FAIL reason=producer_returned_without_completion_sentinel"); quit(1));
