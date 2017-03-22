#!/bin/bash

set -e

root_dir=$1
page_list_filename=$2
iterations=$3
output_dir=$4

if [[ $# -ne 4 ]];
then
  echo 'Usage: ./generate_dependency_list.sh root_dir page_list_filename iterations output_dir'
  exit 1
fi

mkdir -p ${output_dir}

# First find the resource intersection
echo 'Finding resource intersection...'
python find_resource_intersection.py ${root_dir} ${page_list_filename} ${iterations} ${output_dir}/resource_intersection --skip-first-load

echo 'Generating raw dependency files...'
# Generate the raw dependency file
python find_dependency_tree_in_directory.py ${root_dir}/median/ ${page_list_filename} ${output_dir}/raw_dependency_tree --common-resource-dir ${output_dir}/resource_intersection/

# Generate the dependency list (this is sorted be request time)
python generate_dependency_tree_file_for_proxy_return_up_to_iframe.py ${output_dir}/raw_dependency_tree ${page_list_filename} ${output_dir}/dependency_list_sorted_by_request_time --use-only-given-dependencies ${output_dir}/resource_intersection/

# Generate the dependency list sorted on execution time
# echo "python find_dependency_ordering_from_execution_time.py ${root_dir} ${page_list_filename} ${output_dir}/dependency_list_sorted_by_request_time ${iterations} ${output_dir}/dependency_list_sorted_by_execution_time --skip-first-load"
python find_dependency_ordering_from_execution_time.py ${root_dir} ${page_list_filename} ${output_dir}/dependency_list_sorted_by_request_time ${iterations} ${output_dir}/dependency_list_sorted_by_execution_time --skip-first-load

# echo 'Generating raw dependency files...'
# # Generate the raw dependency file
# python find_dependency_tree_in_directory.py ${root_dir}/median/ ${page_list_filename} ${output_dir}/raw_dependency_tree
# 
# # Generate the dependency list (this is sorted be request time)
# python generate_dependency_tree_file_for_proxy_return_up_to_iframe.py ${output_dir}/raw_dependency_tree ${page_list_filename} ${output_dir}/dependency_list_sorted_by_request_time
# 
# # Generate the dependency list sorted on execution time
# python find_dependency_ordering_from_execution_time_all_requests.py ${root_dir} ${page_list_filename} ${output_dir}/dependency_list_sorted_by_request_time ${iterations} ${output_dir}/dependency_list_sorted_by_execution_time --skip-first-load

echo 'DONE'
