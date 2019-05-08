#!/usr/bin/env bash
python compute_visual_metrics.py ../../results/vroom_camera_ready_results/visualmetrics/news_and_sports_cpu_bottleneck_05_29/median/ test_cpu_bottleneck
python compute_visual_metrics.py ../../results/vroom_camera_ready_results/visualmetrics/news_and_sports_baseline_http1_with_screen_recording_05_29//median/ test_http1
