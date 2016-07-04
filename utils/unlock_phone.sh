#!/bin/bash
adb -s $1 shell input keyevent 82
adb -s $1 shell input text 1111
adb -s $1 shell input keyevent 66
