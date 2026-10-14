\\ PARI abandons the remainder of a file loaded by read() when that file
\\ grows the stack.  Size the stack here, while this driver is GP's direct
\\ input, before loading the implementation.
default(parisizemax, "14G");
default(parisize, "4G");

OUT = "kernel163_45641_map.txt";
read("kernel163_45641_map.gp");

