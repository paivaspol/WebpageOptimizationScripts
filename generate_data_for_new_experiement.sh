#!/usr/bin/env bash

set -e

if [[ $# -ne 3 ]];
then
  echo "Usage: $0 [root_dir] [pages_file] [iterations]"
  exit 1
fi

root_dir=`realpath $1`
pages_file=`realpath $2`
iterations=$3


# Get the median and plt.
cd utils
./get_median_and_plt.sh  ${root_dir} ${pages_file} ${iterations}
# python extract_screenshots.py ${root_dir}/chrome_tracing/ ${root_dir}/screenshots
cd -

# Generate the extended waterfall
cd chrome_tracing_scripts
# ./generate_extended_waterfall.sh ${root_dir}
cd -
