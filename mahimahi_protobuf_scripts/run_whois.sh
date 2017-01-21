#!/bin/bash

input=$1
output_dir=$2

mkdir -p ${output_dir}

while read line;
do
  echo ${line}
  query=${line}
  if [[ ${line} == www.* ]];
  then
    query=${query:4}
  fi
  whois ${query} > ${output_dir}/${line}
done < ${input}
