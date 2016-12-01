#!/bin/bash

set -e

base_directory=$1

if [ "$#" -ne 1 ]; then
  echo 'Usage: ./generate_utilization_data.sh [base_directory]'
  exit 1
fi

output_directory=${base_directory}/network_utilizations

mkdir -p ${output_directory}
mkdir -p ${output_directory}/timeseries
mkdir -p ${output_directory}/timeseries/entire_page_load
mkdir -p ${output_directory}/timeseries/until_all_dep_fetch_time_client_side
mkdir -p ${output_directory}/timeseries/until_all_dep_fetch_time_server_side

python compute_network_utilization_final.py ${base_directory}/median \
  --output-timeseries ${output_directory}/timeseries/entire_page_load/ \
  > ${output_directory}/page_load_utilization.txt

python compute_network_utilization_final.py ${base_directory}/median \
  --custom-end-time ${base_directory}/all_dependencies_fetch_time_client_side.txt \
  --output-timeseries ${output_directory}/timeseries/until_all_dep_fetch_time_client_side \
    > ${output_directory}/page_load_utilization_until_fetch_time_client_side.txt

python compute_network_utilization_final.py ${base_directory}/median \
  --custom-end-time ${base_directory}/all_dependencies_fetch_time_server_side.txt \
  --output-timeseries ${output_directory}/timeseries/until_all_dep_fetch_time_server_side \
  > ${output_directory}/page_load_utilization_until_fetch_time_server_side.txt

python compute_network_utilization_final.py ${base_directory}/median \
  --custom-start-time ${base_directory}/all_dependencies_discovery_time.txt \
  --custom-end-time ${base_directory}/all_dependencies_fetch_time_client_side.txt \
  > ${output_directory}/page_load_utilization_between_discovery_and_fetch_time_client_side.txt

python compute_network_utilization_final.py ${base_directory}/median \
  --custom-start-time ${base_directory}/all_dependencies_discovery_time.txt \
  --custom-end-time ${base_directory}/all_dependencies_fetch_time_server_side.txt \
  > ${output_directory}/page_load_utilization_between_discovery_and_fetch_time_server_side.txt

