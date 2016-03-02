#!/bin/bash
python page_load_wrapper.py ../page_list/alexa_top_50_news_25_sports.txt 5 --dont-start-measurements --output-dir ../../results/phone_wifi/alexa_50_news_25_sports_HTTP_1 --disable-tracing --use-device mac
python page_load_wrapper.py ../page_list/alexa_top_50_news_25_sports.txt 5 --dont-start-measurements --output-dir ../../results/laptop_wifi/alexa_50_news_25_sports_HTTP_1 --disable-tracing --use-device Nexus_6
