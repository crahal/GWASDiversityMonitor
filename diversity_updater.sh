#!/bin/bash
<<<<<<< HEAD
git pull origin master
cd /media/charlie/raspi_usb/gwasdiversitymonitor/
/home/charlie/berryconda3/bin/python3 generate_data.py
git add .
git reset HEAD -- correspondance/
git reset HEAD -- data/catalog/cached_files/*/*
git reset HEAD -- static_figures
git commit -m "daily update"
git push origin master
=======
cd /media/charlie/raspi_usb/gwasdiversitymonitor/
/home/charlie/berryconda3/bin/python3 generate_data.py
git add .
git commit -m "daily update"
git push heroku master
>>>>>>> 7a73317f0e3ddf00eed4339c54f9b3cfdf5aa4c8
