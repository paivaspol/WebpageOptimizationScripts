#!/bin/bash

root_dir=$1
pages_filename=$2
iterations=$3
pages_to_ignore=$4

if [ "$#" -ne 4 ]; then
  echo 'usage: ./get_median_and_plt.sh [root_dir] [pages_filename] [iterations] [pages_to_ignore]'
  exit 1
fi

python get_one_load_from_multiple_loads.py ${root_dir} ${pages_filename} ${iterations} median ${root_dir}/median --skip-first-load
# python get_one_load_from_multiple_loads.py ${root_dir} ${pages_filename} ${iterations} median ${root_dir}/median
python get_page_load_time.py ${root_dir}/median > ${root_dir}/page_load_time.txt --pages-to-ignore ${pages_to_ignore}
python parse_json.py ${root_dir}/median ${root_dir}/chrome_tracing
