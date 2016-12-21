#!/bin/bash
set -e

python find_fraction_files_different.py output_dir/1468888449.93 output_dir/1468892049.7 | sort -g -k 2 > fraction_data/one_hour.txt
python find_fraction_files_different.py output_dir/1468888449.93 output_dir/1468985649.3 | sort -g -k 2 > fraction_data/one_day.txt
python find_fraction_files_different.py output_dir/1468888449.93 output_dir/1469547249.15 | sort -g -k 2 > fraction_data/one_week.txt

# python generate_record_directory_with_pages_response.py ../../datasets/longitudial_page_record/1468888449.93 ../../WebpageLoader/page_to_timestamp.txt output_dir/1468888449.93
# python generate_record_directory_with_pages_response.py ../../datasets/longitudial_page_record/1468892049.7 ../../WebpageLoader/page_to_timestamp.txt output_dir/1468892049.7
# python generate_record_directory_with_pages_response.py ../../datasets/longitudial_page_record/1468985649.3 ../../WebpageLoader/page_to_timestamp.txt output_dir/1468985649.3
# python generate_record_directory_with_pages_response.py ../../datasets/longitudial_page_record/1469547249.15 ../../WebpageLoader/page_to_timestamp.txt output_dir/1469547249.15
