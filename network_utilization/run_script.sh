#!/bin/bash
INTERVALS=(100 200 500)
for i in ${INTERVALS[@]};
do
  echo $i
  python utilization_periods_less_than_threshold_in_directory.py ../../results/alexa_50_news_25_sports_spdyproxy/median/ ../../results/alexa_50_news_25_sports_spdyproxy/plots/cdf_utilization_during_${i}_ms_periods_less_than_x/ 12 --interval-size ${i}
  python bar_and_whisker_of_request_sizes.py ../../results/alexa_50_news_25_sports_spdyproxy/median/ ../../results/alexa_50_news_25_sports_spdyproxy/plots/scatter_utilization_and_sum_request_sizes_${i}ms_interval/ --interval-size ${i} --requests-to-ignore ../../results/alexa_50_news_25_sports_spdyproxy/ignoring/requests_to_ignore.txt --pages-to-use ../../results/alexa_50_news_25_sports_spdyproxy/ignoring/top_30_percent_pages_of_max_requests.txt
done
