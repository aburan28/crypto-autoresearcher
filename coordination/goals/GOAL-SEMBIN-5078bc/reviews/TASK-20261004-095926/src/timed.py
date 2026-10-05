#!/usr/bin/env python3
"""timed.py CMD...: run a command, forward stdout/stderr, then print 'TIMED wall=<s> maxrss_kb=<kb> rc=<rc>' on stderr."""
import sys, time, subprocess, resource
t = time.time()
rc = subprocess.call(sys.argv[1:])
w = time.time() - t
ru = resource.getrusage(resource.RUSAGE_CHILDREN)
sys.stderr.write('TIMED wall=%.2f maxrss_kb=%d rc=%d\n' % (w, ru.ru_maxrss, rc))
sys.exit(rc)
