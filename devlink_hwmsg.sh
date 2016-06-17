#!/bin/bash

sudo perf record -a -e devlink:devlink_hwmsg --no-buffering --quiet | sudo perf script -s ~/bin/devlink_hwmsg_perf.py
