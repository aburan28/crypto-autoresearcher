#!/bin/bash
set -eu

DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
PWD=$(pwd)

if [ "$(readlink -f "$PWD/scripts")" != "$(readlink -f "$DIR")" ]; then
    echo "This script must be run as scripts/gen_kat_files.sh from the repository root."
    exit 1
fi

mkdir -p KAT
cd KAT

echo 'Generating KATs for p324_3...'
../build/apps/PQCgenKAT_sign_p324_3

echo 'Generating KATs for p500_27...'
../build/apps/PQCgenKAT_sign_p500_27

echo 'Generating KATs for p664_17...'
../build/apps/PQCgenKAT_sign_p664_17

echo 'Done!'

