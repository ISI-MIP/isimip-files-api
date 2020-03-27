isimip-files-api
================

Microservice to asynchronously mask regions from an [ISIMIP](https://isimip.org) NetCDF file, using [Flask](https://palletsprojects.com/p/flask/) and [RQ](https://python-rq.org/).

Setup
-----

The service needs [redis](https://redis.io/) to be set up and configured proberly. With redit it is especially important to [guard it agains remote access](https://redis.io/topics/security).

The python dependencies can be installed (in a virtual enviroment) using:

```
pip install -r requirements.txt
```

The the `.env` file can be created from `.env.sample` and adjusted to the particular environment.


Usage
-----

Once the application is setup, the development server can be started using:

```
flask run
```

The worker for the asyncronous jobs need to be started in a different terminal session using:

```
rq worker
```


Deployment
----------

When deploying to the internet, a setup of [NGINX](https://www.nginx.com/), (gunicorn)[https://gunicorn.org/], and [systemd](https://www.freedesktop.org/wiki/Software/systemd/) services is recommended, but other services can be used as well. We further assume that a user `isimip` with the group `isimip` and the home `/home/isimip` exists, and that the repository is cloned at `/home/isimip/api`.

After following the steps under **Setup** (as the `isimip` user), add the folowing to `.env`:

```
# gunicorn configuration
GUNICORN_BIN=/home/isimip/api/env/bin/gunicorn
GUNICORN_WORKER=3
GUNICORN_PORT=9002
GUNICORN_TIMEOUT=120
GUNICORN_PID_FILE=/run/gunicorn/api/pid
GUNICORN_ACCESS_LOG_FILE=/var/log/gunicorn/api/access.log
GUNICORN_ERROR_LOG_FILE=/var/log/gunicorn/api/error.log
```

Then, as `root`, create a file `/etc/tmpfiles.d/isimip-api.conf` with the following content:

```
d /var/log/isimip-api    750 isimip isimip
d /var/log/gunicorn/api  750 isimip isimip
d /run/gunicorn/api      750 isimip isimip
```

Create temporary directories using:

```
systemd-tmpfiles --create
```

In order to run the api service with systemd three scripts need to be added to `/etc/systemd/system`

```
# in /etc/systemd/system/isimip-api.service

[Unit]
Description=pseudo-service to start/stop all isimip-api services

[Service]
Type=oneshot
ExecStart=/bin/true
RemainAfterExit=yes

[Install]
WantedBy=network.target
```

```
# in /etc/systemd/system/isimip-api-app.service

[Unit]
Description=isimip-api gunicorn daemon
After=network.target

[Service]
User=isimip
Group=isimip

WorkingDirectory=/home/isimip/api
EnvironmentFile=/home/isimip/api/.env

ExecStart=/bin/sh -c '${GUNICORN_BIN} \
  --workers ${GUNICORN_WORKER} \
  --pid ${GUNICORN_PID_FILE} \
  --bind localhost:${GUNICORN_PORT} \
  --timeout ${GUNICORN_TIMEOUT} \
  --access-logfile ${GUNICORN_ACCESS_LOG_FILE} \
  --error-logfile ${GUNICORN_ERROR_LOG_FILE} \
  "api:create_app()"'

ExecReload=/bin/sh -c '/usr/bin/pkill -HUP -F ${GUNICORN_PID_FILE}'

ExecStop=/bin/sh -c '/usr/bin/pkill -TERM -F ${GUNICORN_PID_FILE}'

[Install]
WantedBy=isimip-api.target
```

```
# in /etc/systemd/system/isimip-api-worker.service

[Unit]
Description=RQ worker for isimip-api
After=network.target

[Service]
User=isimip
Group=isimip

WorkingDirectory=/home/isimip/api
Environment=LANG=en_US.UTF-8
Environment=LC_ALL=en_US.UTF-8
Environment=LC_LANG=en_US.UTF-8

ExecStart=/home/isimip/api/env/bin/rq worker

ExecReload=/bin/kill -s HUP $MAINPID

ExecStop=/bin/kill -s TERM $MAINPID

PrivateTmp=true
Restart=always

[Install]
WantedBy=isimip-api.target
```

Reload `systemd`, start and enable the service:

```
systemctl daemon-reload
systemctl start isimip-api-app
systemctl start isimip-api-worker

systemctl enable isimip-api-app
systemctl enable isimip-api-worker
systemctl enable isimip-api
```

From now on, the services can be controlled using:

```
systemctl start isimip-api
systemctl stop isimip-api
systemctl restart isimip-api
```

If the services won't start: `journalctl -xf` might give a clue why.

Lastly, add

```
    location /api/v1 {
        proxy_pass         http://127.0.0.1:9002/;
        proxy_redirect     off;

        proxy_set_header   Host                 $host;
        proxy_set_header   X-Real-IP            $remote_addr;
        proxy_set_header   X-Forwarded-For      $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto    $scheme;
    }

    location /api/public {
        alias /data/api/public;
    }
```

to your nginx virtual host configuration. The service should then be available at https://yourdomain/api/v1/
