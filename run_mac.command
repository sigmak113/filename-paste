#!/bin/bash
cd "$(dirname "$0")"
python3 -m pip install --user -r requirements-mac.txt
python3 filename_paste_mac.py
