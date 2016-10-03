#!/bin/bash
# python iterative_mahimahi_record.py ../page_list/alexa_top_50_sports.txt replay_configuration_ec2_55.cfg Nexus_6_2 20 record ../../results/alexa_top_50_sports/ --collect-streaming
# python iterative_mahimahi_record.py ../page_list/continue_page_load.txt replay_configuration_ec2_55.cfg Nexus_6_2 20 record ../../results/alexa_top_50_news/ --collect-streaming --times times.txt
# python iterative_mahimahi_record.py ../page_list/alexa_top_50_shopping.txt replay_configuration_ec2_55.cfg Nexus_6_2 20 record ../../results/alexa_top_50_shopping/ --collect-streaming --times times.txt
# python iterative_mahimahi_record.py ../page_list/1_page.txt replay_configuration_ec2_238.cfg Nexus_6 1 record temp --collect-streaming
python iterative_mahimahi_record.py ../page_list/1_page_file.txt replay_configuration_ec2_55.cfg Nexus_6_2 1 record temp --collect-streaming
