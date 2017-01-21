#!/bin/bash

base_dir=$1

python calculate_speedindex.py ${base_dir}/median ${base_dir}/visual_metrics/
python parse_speedindex.py ${base_dir}/visual_metrics/ > ${base_dir}/aft_speedindex.txt
