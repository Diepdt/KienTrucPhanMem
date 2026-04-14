#!/bin/bash
echo "Waiting for MySQL..."
while ! python -c "import MySQLdb; MySQLdb.connect(host='$DB_HOST', user='$DB_USER', passwd='$DB_PASSWORD', db='$DB_NAME')" 2>/dev/null; do sleep 1; done
echo "MySQL is ready."
python manage.py makemigrations --noinput
python manage.py migrate --noinput
exec python manage.py runserver 0.0.0.0:8009
