#!/bin/bash

set -e

basedir=$1

if [[ "$#" -ne 1 ]];
then
  echo './generate_extended_waterfall.sh [base_dir]'
  exit 1
fi

python generate_extended_waterfall.py ${basedir}/median ${basedir}/extended_waterfall
python find_normalized_start_processing_times.py ${basedir}/extended_waterfall/ ${basedir}/extended_waterfall
