#!/bin/bash
git pull origin master
cd /media/charlie/raspi_usb/gwasdiversitymonitor/
/home/charlie/berryconda3/bin/python3 generate_data.py
rm -rf .fuse*
git add .
git reset HEAD -- correspondance/
git reset HEAD -- data/catalog/cached_files/*/*
git reset HEAD -- static_figures
git commit -m "daily update"
git push origin master
