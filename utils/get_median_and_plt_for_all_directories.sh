#!/bin/bash

root_dir=$1

set -e

for d in ${root_dir}/*
do
  if [[ -d ${d} ]];
  then
    echo ${d}
    ./get_median_and_plt.sh ${d} ../../page_loader/page_list/longitudinal_page_load_4g.txt 3
  fi
done
