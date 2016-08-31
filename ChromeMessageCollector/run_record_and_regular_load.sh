#!/bin/bash
python iterative_mahimahi_record.py ../page_list/selected_test_pages.txt replay_configuration.cfg Nexus_6_chromium 15 record ../../results/real_load_to_record_comparison/record_load_15_loads --collect-streaming
python wrapper_script.py 15

python iterative_mahimahi_record.py ../page_list/selected_test_pages.txt replay_configuration.cfg Nexus_6_chromium 20 record ../../results/real_load_to_record_comparison/record_load_20_loads --collect-streaming
python wrapper_script.py 20
