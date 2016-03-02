#!/bin/bash
experiment_settings=(laptop_wifi phone_wifi phone_4g)

for experiment_setting in "${experiment_settings[@]}"
do
  echo "$experiment_setting"
  python get_one_load_from_multiple_loads.py ../../results/"$experiment_setting"/alexa_top_100_subset ../page_list/selected_subset_from_top_100.txt 5 median --output-dir ../../results/"$experiment_setting"/alexa_top_100_subset/median
  mkdir -v ../../results/"$experiment_setting"/alexa_top_100_subset/plots/
  mkdir -v ../../results/"$experiment_setting"/alexa_top_100_subset/plots/cdf_page_load_time/
  python get_page_load_time.py ../../results/"$experiment_setting"/alexa_top_100_subset/median > ../../results/"$experiment_setting"/alexa_top_100_subset/plots/cdf_page_load_time/data_with_page_names.txt
  cat ../../results/"$experiment_setting"/alexa_top_100_subset/plots/cdf_page_load_time/data_with_page_names.txt | awk '{ print $2 }' | tail -n+2 > ../../results/"$experiment_setting"/alexa_top_100_subset/plots/cdf_page_load_time/data.txt
  $useful_scripts/generate_cdf.sh ../../results/"$experiment_setting"/alexa_top_100_subset/plots/cdf_page_load_time/data.txt
  cp ../../results/"$experiment_setting"/alexa_top_100_subset/plots/cdf_page_load_time/cdf_data.txt ../../results/cdf_page_load_time/alexa_top_100_subset/cdf_"$experiment_setting".txt
done
