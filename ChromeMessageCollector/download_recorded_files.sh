#!/bin/bash
scp -r -i ~/.ssh/vaspol_aws_key.pem ubuntu@ec2-174-129-71-3.compute-1.amazonaws.com:/home/ubuntu/long_running_page_load_done/* /home/vaspol/Research/MobileWebOptimization/datasets/long_running_record/long_running_page_load
ssh -i ~/.ssh/vaspol_aws_key.pem ubuntu@ec2-174-129-71-3.compute-1.amazonaws.com 'rm -r /home/ubuntu/long_running_page_load_done/*'
