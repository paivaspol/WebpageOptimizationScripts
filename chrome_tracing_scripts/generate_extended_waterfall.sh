#!/bin/bash

set -e

basedir=$1
depdir=$2

if [[ "$#" -ne 2 ]];
then
  echo './generate_extended_waterfall.sh [base_dir] [dep_dir]'
  exit 1
fi

python generate_extended_waterfall.py ${basedir}/median ${basedir}/extended_waterfall
python find_dynamically_generated_urls.py ${basedir}/extended_waterfall/ ${depdir} ${basedir}/dynamic_urls
