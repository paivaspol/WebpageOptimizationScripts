#!/bin/bash
adb shell am start \
  -a android.intent.action.VIEW \
  -n org.chromium.content_shell_apk/.ContentShellActivity \
  --esa commandLineArgs --proxy-pac-url="http://192.168.1.109/pac_files/config_home_network_nghttpx.pac",--use-npn
