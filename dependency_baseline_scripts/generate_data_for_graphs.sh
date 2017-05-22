#!/bin/bash

set -e

if [ "$#" -ne 1 ]; then
  exit 1
fi

page_list=$1

# The directories to generate the data for.
directories=( /Users/vaspol/Documents/research/MobileWebPageOptimization/results/vroom_debugging/current_debugging/vroom /Users/vaspol/Documents/research/MobileWebPageOptimization/results/vroom_debugging/current_debugging/baseline )
# directories=( ../../results/vroom_debugging/network_utilizations/no_push_only_hints.new )

# The directories for the target_resources
target_resource_dirs=( /Users/vaspol/Documents/research/MobileWebPageOptimization/scripts/dependency_tree_generation/temp_all_iframe_descendants_important/dependency_list_sorted_by_execution_time/ )

# Array containing important and all
important_all=( important all )

for dir in ${directories[@]};
do
  echo $dir
  
  # Setup some variables for this directory.
  resource_root_dir=${dir}/median
  resource_server_side_logs=${dir}/server_side_logs
  page_to_run_index=${dir}/page_to_run_index.txt

  if [[ ${dir} == *"baseline" ]]; then
    iterations=5
  else
    iterations=3
  fi

  # resource_count_directory=${dir}/resource_request_count
  # python get_dependency_request_count.py ${resource_server_side_logs} ${page_to_run_index} ${target_resource_dirs[0]} ${iterations} ${page_list} ${resource_count_directory}

  for mode in ${important_all[@]}; do
    for target_resource_dir in ${target_resource_dirs[@]}; do
      resource_type="page_resource"
      if [[ ${target_resource_dir} == *"dependency_tree"* ]]; then
        resource_type="dependencies"
      fi
      
      echo ${dir} ${mode} ${target_resource_dir}
      client_side_fetch_time_output=${dir}/${mode}_${resource_type}_fetch_time_client_side.txt
      client_side_fetch_time_with_dup_output=${dir}/${mode}_${resource_type}_fetch_time_client_side_with_dup.txt
      server_side_fetch_time_output=${dir}/${mode}_${resource_type}_fetch_time_server_side.txt
      resource_discovery_time_output=${dir}/${mode}_${resource_type}_discovery_time.txt
      resource_discovery_time_dir=${dir}/${mode}_${resource_type}_discovery_time
      client_side_resource_finish_load_time_dir=${dir}/${mode}_${resource_type}_finished_loading_time_client_side
      client_side_resource_finish_load_time_with_dup_dir=${dir}/${mode}_${resource_type}_finished_loading_time_client_side_with_dup
      server_side_resource_finish_load_time_dir=${dir}/${mode}_${resource_type}_finished_loading_time_server_side

      if [[ ${mode} == "important" ]]; then
        # Find the resource finish fetch time on the client-side.
        echo "python find_all_dependencies_finished_loading_from_network_events.py ${resource_root_dir} ${page_list} ${target_resource_dir} --output-finish-times ${client_side_resource_finish_load_time_dir} --only-important > ${client_side_fetch_time_output}"
        echo ""
        python find_all_dependencies_finished_loading_from_network_events.py ${resource_root_dir} ${page_list} ${target_resource_dir} --output-finish-times ${client_side_resource_finish_load_time_dir} --only-important > ${client_side_fetch_time_output}

        # Find the resource finish fetch time on the client-side with dups.
        python find_all_dependencies_finished_loading_from_network_events_consider_duplicated_requests.py ${resource_root_dir} ${target_resource_dir} --output-finish-times ${client_side_resource_finish_load_time_with_dup_dir} --page-list ${page_list} --only-important > ${client_side_fetch_time_with_dup_output}

        # Find all resource discovery time.
        echo "python find_all_dependencies_discovered_from_network_events.py ${resource_root_dir} ${page_list}  ${target_resource_dir} --only-important --output-discovery-times ${resource_discovery_time_dir} > ${resource_discovery_time_output}"
        echo ""
        python find_all_dependencies_discovered_from_network_events.py ${resource_root_dir} ${page_list}  ${target_resource_dir} --only-important --output-discovery-times ${resource_discovery_time_dir} > ${resource_discovery_time_output}

      else
        # Find the resource finish fetch time on the client-side.
        echo "python find_all_dependencies_finished_loading_from_network_events.py ${resource_root_dir} ${page_list} ${target_resource_dir} --output-finish-times ${client_side_resource_finish_load_time_dir} > ${client_side_fetch_time_output}"
        echo ""
        python find_all_dependencies_finished_loading_from_network_events.py ${resource_root_dir} ${page_list} ${target_resource_dir} --output-finish-times ${client_side_resource_finish_load_time_dir} > ${client_side_fetch_time_output}

        # Find the resource finish fetch time on the client-side with dups.
        python find_all_dependencies_finished_loading_from_network_events_consider_duplicated_requests.py ${resource_root_dir} ${target_resource_dir} --output-finish-times ${client_side_resource_finish_load_time_with_dup_dir} --page-list ${page_list} > ${client_side_fetch_time_with_dup_output}

        # Find all resource discovery time.
        echo "python find_all_dependencies_discovered_from_network_events.py ${resource_root_dir} ${page_list} ${target_resource_dir} --output-discovery-times ${resource_discovery_time_dir} > ${resource_discovery_time_output}"
        echo ""
        python find_all_dependencies_discovered_from_network_events.py ${resource_root_dir} ${page_list} ${target_resource_dir} --output-discovery-times ${resource_discovery_time_dir} > ${resource_discovery_time_output}
      fi
    done
  done
done

