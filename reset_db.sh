#!/bin/bash
rm src/db.sqlite3 &> /dev/null
python3 src/manage.py migrate
python3 src/manage.py loaddata default_database.json
