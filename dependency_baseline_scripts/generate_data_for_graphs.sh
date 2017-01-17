#!/bin/bash

set -e

if [ "$#" -ne 1 ]; then
  exit 1
fi

page_list=$1

# The directories to generate the data for.
# directories=( ../../results/vroom_benefits/baseline ../../results/vroom_benefits/after_dependency_list_generation_and_XHR_fix )
# directories=( ../../results/vroom_benefits/with_scheduler_combined_news_sports_new_chromium_throttled )
# directories=( ../../results/vroom_debugging/network_utilizations/baseline_with_utilizations ../../results/vroom_debugging/network_utilizations/push_and_hints_after_server_side_dup_change_iframe_fifa_fix )
directories=( ../../results/vroom_debugging/network_utilizations/network_throughput_bottleneck_updated_dependencies ../../results/vroom_debugging/network_utilizations/baseline_with_utilizations_and_tracing ../../results/vroom_debugging/network_utilizations/push_and_hints_new_dependency_from_baseline_with_hsts ../../results/vroom_debugging/network_utilizations/no_push_only_hints.new )
# directories=( ../../results/vroom_debugging/network_utilizations/no_push_only_hints.new )

# The directories for the target_resources
# target_resource_dirs=( ../../results/vroom_benefits/dependency_list_generation/dependency_trees/dependency_tree_up_to_iframes ../../results/vroom_benefits/dependency_list_generation/all_requests )
target_resource_dirs=( /Users/vaspol/Documents/research/MobileWebPageOptimization/results/dependencies_trees/dependency_tree_raw_from_new_baseline_up_to_iframe temp_all_requests )

# Array containing important and all
important_all=( important all )



for dir in ${directories[@]};
do
  echo $dir
  
  # Setup some variables for this directory.
  resource_root_dir=${dir}/median
  resource_server_side_logs=${dir}/server_side_logs
  page_to_run_index=${dir}/page_to_run_index.txt

  python find_page_resources.py ${resource_root_dir} ${target_resource_dirs[1]}

  if [[ ${dir} == *"baseline" ]]; then
    iterations=5
  else
    iterations=3
  fi

  resource_count_directory=${dir}/resource_request_count
  python get_dependency_request_count.py ${resource_server_side_logs} ${page_to_run_index} ${target_resource_dirs[0]} ${iterations} ${page_list} ${resource_count_directory}

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
        python find_all_dependencies_finished_loading_from_network_events.py ${resource_root_dir} ${target_resource_dir} --output-finish-times ${client_side_resource_finish_load_time_dir} --page-list ${page_list} --only-important > ${client_side_fetch_time_output}

        # Find the resource finish fetch time on the client-side with dups.
        python find_all_dependencies_finished_loading_from_network_events_consider_duplicated_requests.py ${resource_root_dir} ${target_resource_dir} --output-finish-times ${client_side_resource_finish_load_time_with_dup_dir} --page-list ${page_list} --only-important > ${client_side_fetch_time_with_dup_output}

        # Find the resource finish fetch fime on the server-side.
        python find_all_dependencies_finished_loading_from_server_side_logs.py ${resource_server_side_logs} ${page_to_run_index} ${target_resource_dir} ${iterations} ${page_list} --only-important --resource-output-dir ${server_side_resource_finish_load_time_dir} \
          | sort -k 2 -g > ${server_side_fetch_time_output}

        # Find all resource discovery time.
        python find_all_dependencies_discovered_from_network_events.py ${resource_root_dir} ${target_resource_dir} --only-important --output-discovery-times ${resource_discovery_time_dir} > ${resource_discovery_time_output}


      else
        # Find the resource finish fetch time on the client-side.
        python find_all_dependencies_finished_loading_from_network_events.py ${resource_root_dir} ${target_resource_dir} --output-finish-times ${client_side_resource_finish_load_time_dir} --page-list ${page_list} > ${client_side_fetch_time_output}

        # Find the resource finish fetch time on the client-side with dups.
        python find_all_dependencies_finished_loading_from_network_events_consider_duplicated_requests.py ${resource_root_dir} ${target_resource_dir} --output-finish-times ${client_side_resource_finish_load_time_with_dup_dir} --page-list ${page_list} > ${client_side_fetch_time_with_dup_output}

        # Find the resource finish fetch fime on the server-side.
        python find_all_dependencies_finished_loading_from_server_side_logs.py ${resource_server_side_logs} ${page_to_run_index} ${target_resource_dir} ${iterations} ${page_list} --resource-output-dir ${server_side_resource_finish_load_time_dir} \
          | sort -k 2 -g > ${server_side_fetch_time_output}

        # Find all resource discovery time.
        python find_all_dependencies_discovered_from_network_events.py ${resource_root_dir} ${target_resource_dir} --output-discovery-times ${resource_discovery_time_dir} > ${resource_discovery_time_output}
      fi
    done
  done
done

