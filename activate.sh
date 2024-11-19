#!/bin/bash

cd /var/app/current/

source $(find /var/app/venv/*/bin/activate)

export $(sudo cat /opt/elasticbeanstalk/deployment/env | xargs)

python manage.py shell_plus
