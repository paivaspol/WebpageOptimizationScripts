#!/bin/bash

set -e

iterations=$1
basedir=$2

if [[ "$#" -ne 2 ]];
then
  echo './generate_extended_waterfall.sh [iterations] [base_dir]'
  exit 1
fi

actual_iter=$((${iterations} - 1))

for i in $(seq 0 1 ${actual_iter})
do
  python generate_extended_waterfall.py ${basedir}/${i} ${basedir}/extended_waterfall_${i}
done
