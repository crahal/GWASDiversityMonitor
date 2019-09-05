#!/bin/bash
git pull .
cd /media/charlie/raspi_usb/gwasdiversitymonitor/
/home/charlie/berryconda3/bin/python3 generate_data.py
git add .
git commit -m "daily update"
git push origin master
