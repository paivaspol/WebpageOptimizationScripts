#!/bin/bash
settings=(phone_4g phone_wifi)
loads=(alexa_top_100_subset_regular alexa_top_100_subset_from_squid_cache)

for setting in "${settings[@]}"
do
  for load in "${loads[@]}"
  do
    python get_one_load_from_multiple_loads.py ../../results/$setting/$load/ ../page_list/selected_subset_from_top_100_with_redirected_url.txt 5 median --output-dir ../../results/$setting/$load/median
    python get_page_load_time.py ../../results/$setting/$load/median > ../../results/$setting/$load/page_load_time.txt
  done
done

