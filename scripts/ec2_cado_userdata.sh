#!/bin/bash
# cloud-init style user-data for Amazon Linux 2023 / Ubuntu
set -euxo pipefail
exec > >(tee /var/log/cado-setup.log) 2>&1

export DEBIAN_FRONTEND=noninteractive
if command -v apt-get >/dev/null; then
  apt-get update -y
  apt-get install -y build-essential cmake git python3 python3-pip python3-flask \
    libgmp-dev libhwloc-dev zlib1g-dev libssl-dev curl ca-certificates
elif command -v dnf >/dev/null; then
  dnf -y groupinstall "Development Tools"
  dnf -y install cmake git python3 python3-pip gmp-devel hwloc-devel zlib-devel openssl-devel
  pip3 install flask
fi
pip3 install flask || true

cd /opt
if [[ ! -d cado-nfs ]]; then
  git clone --depth 1 https://gitlab.inria.fr/cado-nfs/cado-nfs.git
fi
cd cado-nfs
# local build tree
mkdir -p build/ec2 && cd build/ec2
cmake ../.. -DCMAKE_BUILD_TYPE=Release
make -j"$(nproc)"

WORKDIR=/opt/cado-nist-open
mkdir -p "$WORKDIR"
CADO=/opt/cado-nfs/build/ec2/cado-nfs.py
PARAMS=/opt/cado-nfs/parameters/factor
THREADS="$(nproc)"

run_one() {
  local name="$1" N="$2" digits="$3"
  local params
  case "$digits" in
    5[0-9]|6[0-4]) params="$PARAMS/params.c60" ;;
    6[5-9]|7[0-4]) params="$PARAMS/params.c70" ;;
    7[5-9]|8[0-4]) params="$PARAMS/params.c80" ;;
    8[5-9]|9[0-4]) params="$PARAMS/params.c90" ;;
    9[5-9]|10[0-4]) params="$PARAMS/params.c100" ;;
    10[5-9]|11[0-4]) params="$PARAMS/params.c110" ;;
    11[5-9]|12[0-4]) params="$PARAMS/params.c120" ;;
    12[5-9]|13[0-4]) params="$PARAMS/params.c130" ;;
    13[5-9]|14[0-4]) params="$PARAMS/params.c140" ;;
    14[5-9]|15[0-4]) params="$PARAMS/params.c150" ;;
    *) params="$PARAMS/params.c155" ;;
  esac
  local w="$WORKDIR/$name"
  mkdir -p "$w"
  echo "===== START $name digits=$digits =====" | tee -a "$WORKDIR/progress.log"
  python3 "$CADO" \
    --parameters "$params" \
    --workdir "$w" \
    --server-threads "$THREADS" \
    --screenlog INFO \
    --filelog DEBUG \
    "$N" \
    "server.whitelist=0.0.0.0/0" \
    2>&1 | tee "$w/run.log"
  echo "===== DONE $name =====" | tee -a "$WORKDIR/progress.log"
}

# Remaining after local Sage finishes on P-192 leftovers.
run_one p224-np1 101353182959212931558898552958720398272397773362497713239408730707 65
run_one p256-np1 6162431570535191525422961519393697367216442534546873887302940876054737203 73
run_one p384-np1 1557469607425165783497727874272260515075606922531352427779657307711218862633639645235933417854787936152469367 109
run_one p384-nm1 3436421262549666772394822963556917303774615320989486016740528979559363282671660872963453367185792335038761002437 112
run_one p521-nm1 8686010947518764000493340485319251269434254259172527620677065040319390409295451248399471796941544773224489068299950553585175735406616468529993634152791 151
run_one p521-np1 15255105911401354922182001775736429371709856222540678687543252131523429296439234209433461658518260438962142214158585158030810596916534178534161797539348901 155
run_one p521-cmdisc 5405277566604743401278975911602132324296054382763978192866815683124167925520445433545449676793281443032921640112007528563470322271623658275613707476827805679 157

echo DONE > "$WORKDIR/ALL_DONE"
shutdown -h now
