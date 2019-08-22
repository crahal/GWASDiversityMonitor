#!/bin/bash
python3 generate_data.py
git init
git add .
git commit -m "daily update"
git heroku push master
