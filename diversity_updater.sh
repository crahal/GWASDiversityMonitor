#!/bin/bash
/home/charlie/berryconda3/bin/python3 /media/charlie/raspi_usb/gwasdiversitymonitor/generate_data.py
git add /media/charlie/raspi_usb/gwasdiversitymonitor/
git commit -m "daily update"
git push heroku master