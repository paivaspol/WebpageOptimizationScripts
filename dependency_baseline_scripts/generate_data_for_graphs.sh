#!/bin/bash

set -e

if [ "$#" -ne 1 ]; then
  exit 1
fi

page_list=$1

# The directories to generate the data for.
# directories=( ../../results/vroom_benefits/baseline ../../results/vroom_benefits/after_dependency_list_generation_and_XHR_fix )
# directories=( ../../results/vroom_benefits/with_scheduler_combined_news_sports_new_chromium_throttled )
directories=( ../../results/vroom_benefits/baseline ../../results/vroom_hotmobile_results/push_and_hints_with_cpu_and_network_measurements )

# The directories for the target_resources
target_resource_dirs=( ../../results/vroom_benefits/dependency_list_generation/dependency_trees/dependency_tree_up_to_iframes ../../results/vroom_benefits/dependency_list_generation/all_requests )

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

  for mode in ${important_all[@]}; do
    for target_resource_dir in ${target_resource_dirs[@]}; do
      resource_type="page_resource"
      if [[ ${target_resource_dir} == *"dependency_tree_up_to_iframes"* ]]; then
        resource_type="dependencies"
      fi
      
      echo ${dir} ${mode} ${target_resource_dir}
      client_side_fetch_time_output=${dir}/${mode}_${resource_type}_fetch_time_client_side.txt
      server_side_fetch_time_output=${dir}/${mode}_${resource_type}_fetch_time_server_side.txt
      resource_discovery_time_output=${dir}/${mode}_${resource_type}_discovery_time.txt
      resource_discovery_time_dir=${dir}/${mode}_${resource_type}_discovery_time
      client_side_resource_finish_load_time_dir=${dir}/${mode}_${resource_type}_finished_loading_time_client_side
      server_side_resource_finish_load_time_dir=${dir}/${mode}_${resource_type}_finished_loading_time_server_side

      if [[ ${mode} == "important" ]]; then
        # Find the resource finish fetch time on the client-side.
        # python find_all_dependencies_finished_loading_from_network_events.py ../../results/vroom_benefits/baseline/median ../../results/dependencies_benefits_using_preload_headers/dependency_trees/dependency_trees_for_proxy --output-finish-times ../../results/vroom_benefits/baseline/resource_finished_loading_time --page-list ../page_list/scheduler_test_pages.txt > directory/dependency_fetch_time_client_side.txt
        python find_all_dependencies_finished_loading_from_network_events.py ${resource_root_dir} ${target_resource_dir} --output-finish-times ${client_side_resource_finish_load_time_dir} --page-list ${page_list} --only-important > ${client_side_fetch_time_output}

        # Find the resource finish fetch fime on the server-side.
        # python find_all_dependencies_finished_loading_from_server_side_logs.py ../../results/vroom_benefits/with_scheduler_test_pages/server_side_logs/ ../../results/vroom_benefits/with_scheduler_test_pages/page_to_run_index.txt ../../results/dependencies_benefits_using_preload_headers/dependency_trees/dependency_trees_for_proxy 5 ../page_list/scheduler_test_pages.txt | sort -k 2 -g > ../../results/vroom_benefits/with_scheduler_test_pages/dependency_fetch_time.txt
        python find_all_dependencies_finished_loading_from_server_side_logs.py ${resource_server_side_logs} ${page_to_run_index} ${target_resource_dir} ${iterations} ${page_list} --only-important --resource-output-dir ${server_side_resource_finish_load_time_dir} \
          | sort -k 2 -g > ${server_side_fetch_time_output}

        # Find all resource discovery time.
        # python find_all_dependencies_discovered_from_network_events.py ../../results/vroom_benefits/baseline/median ../../results/dependencies_benefits_using_preload_headers/dependency_trees/dependencies_up_to_iframes/ > ../../results/vroom_benefits/baseline/dependency_discovery_time.txt
        python find_all_dependencies_discovered_from_network_events.py ${resource_root_dir} ${target_resource_dir} --only-important --output-discovery-times ${resource_discovery_time_dir} > ${resource_discovery_time_output}
      else
        # Find the resource finish fetch time on the client-side.
        # python find_all_dependencies_finished_loading_from_network_events.py ../../results/vroom_benefits/baseline/median ../../results/dependencies_benefits_using_preload_headers/dependency_trees/dependency_trees_for_proxy --output-finish-times ../../results/vroom_benefits/baseline/resource_finished_loading_time --page-list ../page_list/scheduler_test_pages.txt > directory/dependency_fetch_time_client_side.txt
        python find_all_dependencies_finished_loading_from_network_events.py ${resource_root_dir} ${target_resource_dir} --output-finish-times ${client_side_resource_finish_load_time_dir} --page-list ${page_list} > ${client_side_fetch_time_output}

        # Find the resource finish fetch fime on the server-side.
        # python find_all_dependencies_finished_loading_from_server_side_logs.py ../../results/vroom_benefits/with_scheduler_test_pages/server_side_logs/ ../../results/vroom_benefits/with_scheduler_test_pages/page_to_run_index.txt ../../results/dependencies_benefits_using_preload_headers/dependency_trees/dependency_trees_for_proxy 5 ../page_list/scheduler_test_pages.txt | sort -k 2 -g > ../../results/vroom_benefits/with_scheduler_test_pages/dependency_fetch_time.txt
  
        echo "python find_all_dependencies_finished_loading_from_server_side_logs.py ${resource_server_side_logs} ${page_to_run_index} ${target_resource_dir} ${iterations} ${page_list} --resource-output-dir ${server_side_resource_finish_load_time_dir}"
        python find_all_dependencies_finished_loading_from_server_side_logs.py ${resource_server_side_logs} ${page_to_run_index} ${target_resource_dir} ${iterations} ${page_list} --resource-output-dir ${server_side_resource_finish_load_time_dir} \
          | sort -k 2 -g > ${server_side_fetch_time_output}

        # Find all resource discovery time.
        # python find_all_dependencies_discovered_from_network_events.py ../../results/vroom_benefits/baseline/median ../../results/dependencies_benefits_using_preload_headers/dependency_trees/dependencies_up_to_iframes/ > ../../results/vroom_benefits/baseline/dependency_discovery_time.txt
        python find_all_dependencies_discovered_from_network_events.py ${resource_root_dir} ${target_resource_dir} --output-discovery-times ${resource_discovery_time_dir} > ${resource_discovery_time_output}
      fi
    done
  done
done

