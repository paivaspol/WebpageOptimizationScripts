#!/usr/bin/env bash
set -e

# This is the root directory of the crawl. The directory is structured as [page]/0/[data]
landing_page_dir=$1
outgoing_links_dir=$2
output_dir=$3

if [ $# -ne 3 ]; then
  echo "Usage: ${0} [landing_page_dir] [outgoing_links_dir] [output_dir]"
  exit 1
fi

# Clear any existing directory.
rm -rf ${output_dir}

# run_analysis() runs all analysis for a page.
# Params:
#   - ${1}: the page
run_analysis() {
  p=${1}
  base_page=`basename ${p}`
  landing_page_crawl_dir=${landing_page_dir}/${base_page}
  page_outgoing_links_dir=${p}
  # Setup the output directory for this page.
  # Only keep the last portion of the page.
  page_output_dir=${output_dir}/${base_page}
  mkdir -p "${page_output_dir}"

  # First, generate the page histogram.
  # Example: python generate_resource_page_histogram.py ~/research/results/prefetch_user_think_time/crawl/all_links_from_pages/ ~/research/results/prefetch_user_think_time/page_lists/landing_pages
  histogram_output_dir=${page_output_dir}/histogram
  mkdir -p "${histogram_output_dir}"
  echo "python generate_resource_page_histogram.py \"${page_outgoing_links_dir}/0/\" > \"${page_output_dir}/histogram/data\""
  python generate_resource_page_histogram.py "${page_outgoing_links_dir}/0/" > "${page_output_dir}/histogram/data"
  echo "python generate_resource_page_histogram.py \"${page_outgoing_links_dir}/0/\" --group-pages > \"${page_output_dir}/histogram/data_grouped\""
  python generate_resource_page_histogram.py "${page_outgoing_links_dir}/0/" --group-pages > "${page_output_dir}/histogram/data_grouped"

  # # Generate the caching data.
  # # python find_intersection_cache_times.py ~/research/results/prefetch_user_think_time/crawl/landing_pages/cnn.com/network_cnn.com ~/research/results/prefetch_user_think_time/crawl/all_links_from_pages/cnn.com/0 10
  # mkdir -p "${page_output_dir}/cache_times"
  # python find_intersection_cache_times.py "${landing_page_crawl_dir}/network_${base_page}" "${page_outgoing_links_dir}"/0 10 > "${page_output_dir}/cache_times"/data

  # # Generate landing page resource used.
  # # python find_lp_resource_used.py ~/research/results/prefetch_user_think_time/crawl/landing_pages/cnn.com/network_cnn.com ~/research/results/prefetch_user_think_time/crawl/all_links_from_pages/cnn.com/0/
  # mkdir -p "${page_output_dir}/cacheable_resources_used_from_lp"
  # python find_lp_resource_used.py "${landing_page_crawl_dir}/network_${base_page}" "${page_outgoing_links_dir}"/0/ > "${page_output_dir}/cacheable_resources_used_from_lp"/data
  # python find_lp_resource_used.py "${landing_page_crawl_dir}/network_${base_page}" "${page_outgoing_links_dir}"/0/ --group-pages > "${page_output_dir}/cacheable_resources_used_from_lp"/data_grouped


  # Find the fetch time of resources.
  # fetch_time_output_dir=${page_output_dir}/fetch_time
  # mkdir -p "${fetch_time_output_dir}"
  # CONNECTION_TYPES=( 3G 4G LTE )
  # for ct in ${CONNECTION_TYPES[@]};
  # do
  #   echo "python find_time_to_prefetch_resources.py ${page_outgoing_links_dir}/0/ ${ct} > ${page_output_dir}/fetch_time/${ct}_data"
  #   python find_time_to_prefetch_resources.py "${page_outgoing_links_dir}/0/" ${ct} > "${page_output_dir}/fetch_time/${ct}_data"
  #   echo "python find_time_to_prefetch_resources.py ${page_outgoing_links_dir}/0/ ${ct} --group-pages > ${page_output_dir}/fetch_time/${ct}_data_grouped"
  #   python find_time_to_prefetch_resources.py "${page_outgoing_links_dir}/0/" ${ct} --group-pages > "${page_output_dir}/fetch_time/${ct}_data_grouped"
  # done

  # Find fraction of prefetched resources used on a page.
  prefetch_resource_used_output_dir=${page_output_dir}/prefetch_resource_used_rel_to_page_resources
  echo "${prefetch_resource_used_output_dir}"
  mkdir -p "${prefetch_resource_used_output_dir}"
  mkdir -p "${page_output_dir}"/resource_count/
  # Find prefetched resources used.
  echo "python find_fraction_page_resource_prefetched.py ${page_outgoing_links_dir}/0/ --output-resource-count="${page_output_dir}"/resource_count/data "${prefetch_resource_used_output_dir}/data""
  python find_fraction_page_resource_prefetched.py "${page_outgoing_links_dir}/0/" --output-resource-count="${page_output_dir}"/resource_count/data "${prefetch_resource_used_output_dir}/"
  # echo "python find_fraction_page_resource_prefetched.py ${page_outgoing_links_dir}/0/ --output-resource-count="${page_output_dir}"/resource_count/data "${prefetch_resource_used_output_dir}/data_grouped" --group-pages"
  # python find_fraction_page_resource_prefetched.py "${page_outgoing_links_dir}/0/" --output-resource-count="${page_output_dir}"/resource_count/data "${prefetch_resource_used_output_dir}/" --group-pages

  # Find fraction of prefetched resources out of the ones that have been prefetched.
  prefetch_resource_used_output_dir=${page_output_dir}/prefetch_resource_used_rel_to_prefetched
  echo "${prefetch_resource_used_output_dir}"
  mkdir -p "${prefetch_resource_used_output_dir}"
  mkdir -p "${page_output_dir}"/resource_count/
  # Find prefetched resources used.
  echo "python find_fraction_prefetched_resources_used.py ${page_outgoing_links_dir}/0/ --output-resource-count="${page_output_dir}"/resource_count/data "${prefetch_resource_used_output_dir}/""
  python find_fraction_prefetched_resources_used.py "${page_outgoing_links_dir}/0/" --output-resource-count="${page_output_dir}"/resource_count/data "${prefetch_resource_used_output_dir}/"
  # echo "python find_fraction_prefetched_resources_used.py ${page_outgoing_links_dir}/0/ --output-resource-count="${page_output_dir}"/resource_count/data "${prefetch_resource_used_output_dir}/data_grouped" --group-pages"
  # python find_fraction_prefetched_resources_used.py "${page_outgoing_links_dir}/0/" --output-resource-count="${page_output_dir}"/resource_count/data "${prefetch_resource_used_output_dir}/" --group-pages
}

# Main loop for processing.
for p in ${outgoing_links_dir}/*;
do
  echo "Processing: ${p}"
  # if [[ ${p} != *"cnn.com"* ]]; then
  #     continue
  # fi
  run_analysis "${p}" &
done

# Wait for all processes to finish
wait
echo "Finished processing all pages.. Bye..."
