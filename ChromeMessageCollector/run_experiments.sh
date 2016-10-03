#!/bin/bash

# python mahimahi_page_script.py ../page_list/final_combined_news_sports.txt replay_configuration_ec2_55.cfg Nexus_6 5 per_packet_delay_replay ../../results/final_set_of_pages/motivation_http1.1_replay_over_dongle --collect-streaming --use-openvpn --pac-file-location http://ec2-54-237-249-55.compute-1.amazonaws.com/config_testing.pac --page-time-mapping page_to_timestamp.txt --without-dependencies --fetch-server-side-logs --http-version 1

# python mahimahi_page_script.py ../page_list/final_combined_news_sports.txt replay_configuration_ec2_55.cfg Nexus_6 5 per_packet_delay_replay ../../results/final_set_of_pages/motivation_http1.1_replay_over_dongle --collect-streaming --use-openvpn --pac-file-location http://ec2-54-237-249-55.compute-1.amazonaws.com/config_testing.pac --page-time-mapping page_to_timestamp.txt --without-dependencies --fetch-server-side-logs --http-version 1

# python mahimahi_page_script.py ../page_list/final_combined_news_sports.txt replay_configuration_ec2_55.cfg Nexus_6 5 per_packet_delay_replay ../../results/final_set_of_pages/motivation_http1.1_replay_over_dongle --collect-streaming --use-openvpn --pac-file-location http://ec2-54-237-249-55.compute-1.amazonaws.com/config_testing.pac --page-time-mapping page_to_timestamp.txt --without-dependencies --fetch-server-side-logs --http-version 1

# python mahimahi_page_script.py ../page_list/pages_with_dependencies.txt replay_configuration_localhost.cfg  Nexus_6_2 5 per_packet_delay_replay ../../results/page_load_improvements_with_dependency_frames/5_replay_no_dependencies_new --collect-streaming --use-openvpn --pac-file-location http://ec2-54-237-249-55.compute-1.amazonaws.com/config_testing.pac --page-time-mapping ../../results/page_load_improvements_with_dependency_frames/page_to_timestamp.txt --without-dependencies

# python mahimahi_page_script.py ../page_list/pages_with_dependencies.txt replay_configuration_localhost.cfg  Nexus_6_2 5 per_packet_delay_replay ../../results/page_load_improvements_with_dependency_frames/5_replay_with_dependencies_new_2 --collect-streaming --use-openvpn --pac-file-location http://ec2-54-237-249-55.compute-1.amazonaws.com/config_testing.pac --page-time-mapping ../../results/page_load_improvements_with_dependency_frames/page_to_timestamp.txt

# python mahimahi_page_script.py ../page_list/pages_with_dependencies.txt replay_configuration_localhost.cfg  Nexus_6_2 5 per_packet_delay_replay ../../results/page_load_improvements_with_dependency_frames/5_replay_with_dependencies_only_js_css_html_new_2 --collect-streaming --use-openvpn --pac-file-location http://ec2-54-237-249-55.compute-1.amazonaws.com/config_testing.pac --page-time-mapping ../../results/page_load_improvements_with_dependency_frames/page_to_timestamp.txt

# python mahimahi_page_script.py ../page_list/continue_page_load.txt replay_configuration_localhost.cfg  Nexus_6_2 2 per_packet_delay_replay temp --collect-streaming --use-openvpn --pac-file-location http://ec2-54-237-249-55.compute-1.amazonaws.com/config_testing.pac --page-time-mapping ../../results/page_load_improvements_with_dependency_frames/page_to_timestamp.txt

# python mahimahi_page_script.py ../page_list/combined_news_sports_shopping.txt replay_configuration_ec2_55.cfg Nexus_6 5 per_packet_delay_replay /home/vaspol/Research/MobileWebOptimization/results/final_set_of_pages/5_replay_news_sports_shopping_without_dependencies_with_iframes_new_2 --collect-streaming --use-openvpn --pac-file-location http://ec2-54-237-249-55.compute-1.amazonaws.com/config_testing.pac --page-time-mapping page_to_timestamp.txt --fetch-server-side-logs --without-dependencies

# python mahimahi_page_script.py ../page_list/combined_news_sports_shopping.txt replay_configuration_ec2_55.cfg Nexus_6 5 per_packet_delay_replay /home/vaspol/Research/MobileWebOptimization/results/final_set_of_pages/5_replay_news_sports_shopping_with_dependencies_without_iframes_new --collect-streaming --use-openvpn --pac-file-location http://ec2-54-237-249-55.compute-1.amazonaws.com/config_testing.pac --page-time-mapping page_to_timestamp.txt --fetch-server-side-logs


# python mahimahi_page_script.py ../page_list/1_page.txt replay_configuration_ec2_55.cfg Nexus_6 2 per_packet_delay_replay temp --collect-streaming --use-openvpn --pac-file-location http://ec2-54-237-249-55.compute-1.amazonaws.com/config_testing.pac --page-time-mapping page_to_timestamp.txt --fetch-server-side-logs --start-tcpdump-and-cpu-measurements

# python mahimahi_page_script.py ../page_list/1_page.txt replay_configuration_ec2_55.cfg Nexus_6 2 per_packet_delay_replay temp_cache_disabled --collect-streaming --use-openvpn --pac-file-location http://ec2-54-237-249-55.compute-1.amazonaws.com/config_testing.pac --page-time-mapping page_to_timestamp.txt --fetch-server-side-logs

# python mahimahi_page_script.py ../page_list/scheduler_test_pages.txt replay_configuration_ec2_238.cfg Nexus_6_2_chromium 5 per_packet_delay_replay scheduler_testing  --collect-streaming --use-openvpn --pac-file-location http://ec2-54-85-76-238.compute-1.amazonaws.com/config_testing.pac --page-time-mapping page_to_timestamp.txt --fetch-server-side-logs
# python mahimahi_page_script.py ../page_list/1_page_file.txt replay_configuration_ec2_55.cfg Nexus_6 1 per_packet_delay_replay test_page_script_run --collect-streaming --use-openvpn --pac-file-location http://ec2-54-85-76-238.compute-1.amazonaws.com/config_testing.pac --page-time-mapping page_to_timestamp.txt --fetch-server-side-logs --without-dependencies
# python mahimahi_page_script.py ../page_list/scheduler_test_pages.txt replay_configuration_ec2_238.cfg Nexus_6_2_chromium 3 per_packet_delay_replay scheduler_testing_baseline  --collect-streaming --use-openvpn --pac-file-location http://ec2-54-85-76-238.compute-1.amazonaws.com/config_testing.pac --page-time-mapping page_to_timestamp.txt --fetch-server-side-logs --without-dependencies

# python mahimahi_page_script.py ../page_list/1_page_file.txt replay_configuration_apple-pi.cfg Nexus_6_2 1 per_packet_delay_replay temp --collect-streaming --use-openvpn --pac-file-location http://apple-pi.eecs.umich.edu/config_testing.pac --page-time-mapping page_to_timestamp.txt --fetch-server-side-logs --without-dependencies

###############################################################################################################################################################################
# Regenerate Dependencies pages.
# python mahimahi_page_script.py ../page_list/1_page.txt replay_configuration_ec2_238.cfg Nexus_6_chromium 3 per_packet_delay_replay ../../results/vroom_results/dependency_list_generation_new --collect-streaming --use-openvpn --pac-file-location http://ec2-54-85-76-238.compute-1.amazonaws.com/config_testing.pac --page-time-mapping page_to_timestamp.txt --fetch-server-side-logs --without-dependencies

###############################################################################################################################################################################
# DESIGN MOTIVATION
# python mahimahi_page_script.py ../page_list/final_combined_news_sports replay_configuration_ec2_55.cfg Nexus_6 3 per_packet_delay_replay ../../results/design_motivation/final_news_sports_preload_headers_all_dependencies --collect-streaming --use-openvpn --pac-file-location http://ec2-54-237-249-55.compute-1.amazonaws.com/config_testing.pac --page-time-mapping page_to_timestamp.txt --fetch-server-side-logs
# python mahimahi_page_script.py ../page_list/continue_page_load.txt replay_configuration_ec2_55.cfg Nexus_6 3 per_packet_delay_replay ../../results/design_motivation/final_news_sports_preload_headers_all_dependencies --collect-streaming --use-openvpn --pac-file-location http://ec2-54-237-249-55.compute-1.amazonaws.com/config_testing.pac --page-time-mapping page_to_timestamp.txt --fetch-server-side-logs


###############################################################################################################################################################################
# EVALUATION

###############################################################################################################################################################################
# 3 Test pages.
# python mahimahi_page_script.py ../page_list/scheduler_3_test_pages.txt replay_configuration_ec2_238.cfg Nexus_6_chromium 3 per_packet_delay_replay ../../results/vroom_results/after_ravi_fix_2_pages_new --collect-streaming --use-openvpn --pac-file-location http://ec2-54-85-76-238.compute-1.amazonaws.com/config_testing.pac --page-time-mapping page_to_timestamp.txt --fetch-server-side-logs

#################
# 15 Pages
# python mahimahi_page_script.py ../page_list/scheduler_3_test_pages.txt replay_configuration_ec2_238.cfg Nexus_6_chromium 3 per_packet_delay_replay ../../results/vroom_results/aljazeera_no_scheduler_with_dependencies --collect-streaming --use-openvpn --pac-file-location http://ec2-54-85-76-238.compute-1.amazonaws.com/config_testing.pac --page-time-mapping page_to_timestamp.txt --fetch-server-side-logs 
# python mahimahi_page_script.py ../page_list/scheduler_test_pages.txt replay_configuration_ec2_238.cfg Nexus_6_chromium 3 per_packet_delay_replay ../../results/vroom_results/after_ravi_fix_2_pages_15_pages_fixed_scheduler_4 --collect-streaming --use-openvpn --pac-file-location http://ec2-54-85-76-238.compute-1.amazonaws.com/config_testing.pac --page-time-mapping page_to_timestamp.txt --fetch-server-side-logs

###############################################################################################################################################################################
# All pages in news sports.
# python mahimahi_page_script.py ../page_list/final_combined_news_sports.txt replay_configuration_ec2_238.cfg Nexus_6_chromium 3 per_packet_delay_replay ../../results/vroom_results/with_scheduler_combined_news_sports_new_chromium_throttled --collect-streaming --use-openvpn --pac-file-location http://ec2-54-85-76-238.compute-1.amazonaws.com/config_testing.pac --page-time-mapping page_to_timestamp.txt --fetch-server-side-logs
# python mahimahi_page_script.py ../page_list/1_page_file.txt replay_configuration_ec2_238.cfg Nexus_6_2_chromium 1 per_packet_delay_replay test_page_script_run --collect-streaming --use-openvpn --pac-file-location http://ec2-54-85-76-238.compute-1.amazonaws.com/config_testing.pac --page-time-mapping page_to_timestamp.txt --fetch-server-side-logs --without-dependencies

# python mahimahi_page_script.py ../page_list/continue_page_load.txt replay_configuration_ec2_238.cfg Nexus_6_2_chromium 5 per_packet_delay_replay ../../results/vroom_benefits/baseline_mac_throttle --collect-streaming --use-openvpn --pac-file-location http://ec2-54-85-76-238.compute-1.amazonaws.com/config_testing.pac --page-time-mapping page_to_timestamp.txt --fetch-server-side-logs --without-dependencies

# python mahimahi_page_script.py ../page_list/continue_page_load.txt replay_configuration_ec2_238.cfg Nexus_6_2_chromium 5 per_packet_delay_replay ../../results/vroom_benefits/with_scheduler_mac_throttle_new --collect-streaming --use-openvpn --pac-file-location http://ec2-54-85-76-238.compute-1.amazonaws.com/config_testing.pac --page-time-mapping page_to_timestamp.txt --fetch-server-side-logs

# python mahimahi_page_script.py ../page_list/continue_page_load.txt replay_configuration_ec2_238.cfg Nexus_6_2_chromium 5 per_packet_delay_replay ../../results/vroom_benefits/scheduler_up_to_iframe_mac_throttling --collect-streaming --use-openvpn --pac-file-location http://ec2-54-85-76-238.compute-1.amazonaws.com/config_testing.pac --page-time-mapping page_to_timestamp.txt --fetch-server-side-logs
# python mahimahi_page_script.py ../page_list/final_combined_news_sports.txt replay_configuration_ec2_238.cfg Nexus_6_2 5 per_packet_delay_replay ../../results/vroom_benefits/scheduler_up_to_iframe_mac_throttling --collect-streaming --use-openvpn --pac-file-location http://ec2-54-85-76-238.compute-1.amazonaws.com/config_testing.pac --page-time-mapping page_to_timestamp.txt --fetch-server-side-logs

# python mahimahi_page_script.py ../page_list/1_page_file.txt replay_configuration_apple-pi.cfg Nexus_6_2 1 per_packet_delay_replay temp --collect-streaming --use-openvpn --pac-file-location http://apple-pi.eecs.umich.edu/config_testing.pac --page-time-mapping page_to_timestamp.txt --fetch-server-side-logs --without-dependencies

python mahimahi_page_script.py ../page_list/final_combined_news_sports.txt replay_configuration_ec2_55.cfg Nexus_6_2_chromium 3 per_packet_delay_replay /Users/vaspol/Documents/research/MobileWebPageOptimization/results/vroom_benefits/final_bottom_half --collect-streaming --use-openvpn --pac-file-location http://ec2-54-237-249-55.compute-1.amazonaws.com/config_testing.pac --page-time-mapping page_to_timestamp.txt --fetch-server-side-logs

#############################################################################################
# Design Motivation
# python mahimahi_page_script.py ../page_list/final_combined_news_sports.txt replay_configuration_ec2_55.cfg Nexus_6_2 3 per_packet_delay_replay /Users/vaspol/Documents/research/MobileWebPageOptimization/results/design_motivation/final_vroom_without_scheduler_news_sports_throttled --collect-streaming --use-openvpn --pac-file-location http://ec2-54-237-249-55.compute-1.amazonaws.com/config_testing.pac --page-time-mapping page_to_timestamp.txt --fetch-server-side-logs --without-dependencies
