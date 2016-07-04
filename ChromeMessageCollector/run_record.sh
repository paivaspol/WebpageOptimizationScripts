#!/bin/bash
cd /home/vaspol/Research/MobileWebOptimization/scripts/venv/
source bin/activate
python /home/vaspol/Research/MobileWebOptimization/scripts/ChromeMessageCollector/mahimahi_page_script.py /home/vaspol/Research/MobileWebOptimization/scripts/page_list/alexa_top_100_subset_with_top_80_most_cached.txt /home/vaspol/Research/MobileWebOptimization/scripts/ChromeMessageCollector/replay_configuration.cfg Nexus_6_2 1 record /home/vaspol/Research/MobileWebOptimization/scripts/ChromeMessageCollector/temp
