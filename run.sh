#!/bin/bash

# Try to use python from virtualenv if it exists, else use system version
py3=.venv/bin/python3
[[ -x "$py3" ]] || py3=$( which python3 )

$py3 run.py "$@"
