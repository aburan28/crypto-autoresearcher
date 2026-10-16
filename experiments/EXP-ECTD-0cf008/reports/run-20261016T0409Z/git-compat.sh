#!/bin/sh
if [ "$#" -eq 3 ] && [ "$1" = sparse-checkout ] && [ "$2" = check-rules ] && [ "$3" = --stdin ]; then
    exec /opt/homebrew/bin/git sparse-checkout check-rules
fi
exec /opt/homebrew/bin/git "$@"
