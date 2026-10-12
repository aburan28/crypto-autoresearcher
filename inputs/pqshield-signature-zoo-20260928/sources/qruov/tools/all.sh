#!/bin/sh
set -eu

DEFAULT_PARAM_CHOICES="1q127L3 1q127L10 1q31L3 1q31L10 1q7L10"
DEFAULT_PARAM_CHOICES="$DEFAULT_PARAM_CHOICES 3q127L3 3q127L10 3q31L3 3q31L10 3q7L10"
DEFAULT_PARAM_CHOICES="$DEFAULT_PARAM_CHOICES 5q127L3 5q127L10 5q31L3 5q31L10 5q7L10"
PARAM_CHOICES=${PARAM_CHOICES:-"$DEFAULT_PARAM_CHOICES"}
PRG_CHOICES=${PRG_CHOICES:-"aes shake"}

if [ "$#" -eq 0 ]; then
    echo "usage: $0 command [args...]" >&2
    exit 2
fi

for prg in $PRG_CHOICES; do
    for param in $PARAM_CHOICES; do
        echo "RUN PARAM=$param PRG=$prg"
        "$@" PARAM="$param" PRG="$prg"
    done
done
