#!/bin/bash

root_dir=$1
iterations=$2

if [ "$#" -ne 2 ]; then
  echo 'usage: ./get_median_and_plt.sh [root_dir] [iterations]'
  exit 1
fi

correct_iter=$((${iterations} - 1))
for i in `seq 0 ${correct_iter}`;
do
  python get_page_load_time.py ${root_dir}/${i} > ${root_dir}/page_load_time_${i}.txt
  python parse_json.py ${root_dir}/${i} ${root_dir}/chrome_tracing_${i}
done
