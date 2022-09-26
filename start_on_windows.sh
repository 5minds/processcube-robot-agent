#!/bin/sh

export CONFIG_FILE=`pwd`/config.dev-win.json
export PYTHONPATH=`pwd`

python -m processcube_robot_agent serve

