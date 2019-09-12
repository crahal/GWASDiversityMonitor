git pull origin master
cd /media/charlie/raspi_usb/gwasdiversitymonitor/
/home/charlie/berryconda3/bin/python3 generate_data.py
rm -rf .fuse*
git add .
git reset HEAD -- correspondance/
git reset HEAD -- __pycache__/
git reset HEAD -- gwasdiversitymonitor_app/data/catalog/cached_files/*/*
git reset HEAD -- *swp
git commit -m "daily update"
git push origin master
