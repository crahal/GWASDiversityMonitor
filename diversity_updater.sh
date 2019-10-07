git pull origin master
cd /home/tsl/Dropbox/gwasdiversitymonitor/
python3 gwasdiversitymonitor_app/generate_data.py
rm -rf .fuse*
git add .
git reset HEAD -- correspondance/
git reset HEAD -- __pycache__/
git reset HEAD -- gwasdiversitymonitor_app/__pycache__/
git reset HEAD -- gwasdiversitymonitor_app/data/catalog/cached_files/*/*
git reset HEAD -- *swp
git commit -m "daily update"
git push origin master
