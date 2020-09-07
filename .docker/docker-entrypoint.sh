#!/bin/sh
set -e
flask db upgrade
# gunicorn -b :5000 trek:app
flask run --host=0.0.0.0