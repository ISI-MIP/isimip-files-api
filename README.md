isimip-cutout
=============

Microservice to asynchronously cut out regions from an [ISIMIP](https://isimip.org) NetCDF file, using [Flask](https://palletsprojects.com/p/flask/) and [RQ](https://python-rq.org/).

Setup
-----

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

The following assumes that a user `isimip` with the group `isimip` and the home `/home/isimip` exists. The repo is cloned at `/home/isimip/cutout`.

After following the steps under **Setup** (as the `isimip` user), add the folowing to `.env`:

```
# gunicorn configuration
GUNICORN_BIN=/home/isimip/cutout/env/bin/gunicorn
GUNICORN_WORKER=3
GUNICORN_PORT=9002
GUNICORN_TIMEOUT=120
GUNICORN_PID_FILE=/run/gunicorn/cutout/pid
GUNICORN_ACCESS_LOG_FILE=/var/log/gunicorn/cutout/access.log
GUNICORN_ERROR_LOG_FILE=/var/log/gunicorn/cutout/error.log
```

Then, as `root`, create a file `/etc/tmpfiles.d/isimip-cutout.conf` with the following content:

```
d /var/log/isimip-cutout    750 isimip isimip
d /var/log/gunicorn/cutout  750 isimip isimip
d /run/gunicorn/cutout      750 isimip isimip
```

Create temporary directories using:

```
systemd-tmpfiles --create
```

In order to run the cutout service with systemd three scripts need to be added to `/etc/systemd/system`

```
# in /etc/systemd/system/isimip-cutout.service

[Unit]
Description=pseudo-service to start/stop all isimip-cutout services

[Service]
Type=oneshot
ExecStart=/bin/true
RemainAfterExit=yes

[Install]
WantedBy=network.target
```

```
# in /etc/systemd/system/isimip-cutout-app.service

[Unit]
Description=isimip-cutout gunicorn daemon
After=network.target

[Service]
User=isimip
Group=isimip

WorkingDirectory=/home/isimip/cutout
EnvironmentFile=/home/isimip/cutout/.env

ExecStart=/bin/sh -c '${GUNICORN_BIN} \
  --workers ${GUNICORN_WORKER} \
  --pid ${GUNICORN_PID_FILE} \
  --bind localhost:${GUNICORN_PORT} \
  --timeout ${GUNICORN_TIMEOUT} \
  --access-logfile ${GUNICORN_ACCESS_LOG_FILE} \
  --error-logfile ${GUNICORN_ERROR_LOG_FILE} \
  "cutout:create_app()"'

ExecReload=/bin/sh -c '/usr/bin/pkill -HUP -F ${GUNICORN_PID_FILE}'

ExecStop=/bin/sh -c '/usr/bin/pkill -TERM -F ${GUNICORN_PID_FILE}'

[Install]
WantedBy=isimip-cutout.target
```

```
# in /etc/systemd/system/isimip-cutout-worker.service

[Unit]
Description=RQ worker for isimip-cutout
After=network.target

[Service]
User=isimip
Group=isimip

WorkingDirectory=/home/isimip/cutout
Environment=LANG=en_US.UTF-8
Environment=LC_ALL=en_US.UTF-8
Environment=LC_LANG=en_US.UTF-8

ExecStart=/home/isimip/cutout/env/bin/rq worker

ExecReload=/bin/kill -s HUP $MAINPID

ExecStop=/bin/kill -s TERM $MAINPID

PrivateTmp=true
Restart=always

[Install]
WantedBy=isimip-cutout.target
```

Reload `systemd`, start and enable the service:

```
systemctl daemon-reload
systemctl start isimip-cutout-app
systemctl start isimip-cutout-worker

systemctl enable isimip-cutout-app
systemctl enable isimip-cutout-worker
systemctl enable isimip-cutout
```

From now on, the services can be controlled using:

```
systemctl start isimip-cutout
systemctl stop isimip-cutout
systemctl restart isimip-cutout
```

If the services won't start: `journalctl -xf` might give a clue why.

Lastly, add

```
    location /cutout {
        proxy_pass         http://127.0.0.1:9002/;
    proxy_redirect     off;

    proxy_set_header   Host                 $host;
    proxy_set_header   X-Real-IP            $remote_addr;
    proxy_set_header   X-Forwarded-For      $proxy_add_x_forwarded_for;
    proxy_set_header   X-Forwarded-Proto    $scheme;
    }
```

to your nginx virtual host configuration. The service should then be available at https://yourdomain/cutout/
