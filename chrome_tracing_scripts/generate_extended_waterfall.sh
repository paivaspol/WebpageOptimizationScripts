#!/bin/bash

set -e

basedir=$1

if [[ "$#" -ne 1 ]];
then
  echo './generate_extended_waterfall.sh [base_dir]'
  exit 1
fi

python generate_extended_waterfall.py ${basedir}/median ${basedir}/extended_waterfall
# python generate_extended_waterfall.py ${basedir}/median ${basedir}/extended_waterfall_json --output-json
#
# python get_all_times.py ${basedir}/median/ > ${basedir}/main_process_timings
