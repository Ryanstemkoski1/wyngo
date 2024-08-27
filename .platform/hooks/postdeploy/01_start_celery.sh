#!/bin/bash

# adding env variables
cat /opt/elasticbeanstalk/deployment/env >> /etc/default/celeryd

# worker
(cd /var/app/current; systemctl stop celery_worker)
(cd /var/app/current; systemctl start celery_worker)
(cd /var/app/current; systemctl enable celery_worker.service)

# beat
(cd /var/app/current; systemctl stop celery_beat)
(cd /var/app/current; systemctl start celery_beat)
(cd /var/app/current; systemctl enable celery_beat.service)