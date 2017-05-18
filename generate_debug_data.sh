#!/bin/bash

root_dir=$1
dep_dir=$2

if [[ $# -ne 2 ]];
then
  echo 'Usage: ./generate_debug_data.sh [root_dir] [dep_dir]'
  exit 1
fi

output_dir=${root_dir}/debug_data
mkdir -p ${output_dir}

python ./chrome_tracing_scripts/get_network_wait_time_excluding_processing_time.py ${root_dir}/median/ ${root_dir}/extended_waterfall_json/ ${dep_dir} ${output_dir}/network_wait_time_scatter_plot
python ./chrome_tracing_scripts/get_all_times.py ${root_dir}/median/ > ${output_dir}/time_on_main_process
