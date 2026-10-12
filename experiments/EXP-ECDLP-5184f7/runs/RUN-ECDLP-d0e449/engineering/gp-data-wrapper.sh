#!/bin/sh
export GP_DATA_DIR=/workspace/solinas-runtime/nist-comparison/seadata/usr/share/pari
exec /workspace/solinas-runtime/pari/usr/bin/gp-real "$@"
