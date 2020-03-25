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

After following the steps under **Setup**, add the folowing to `.env`:

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

Then, create a file `/etc/tmpfiles.d/isimip-cutout.conf` with the following content:

```
d /var/log/isimip-cutout    750 isimip isimip
d /var/log/gunicorn/cutout  750 isimip isimip
d /run/gunicorn/cutout      750 isimip isimip
```

Create temporary directories using:

```
systemd-tmpfiles --create
```

Next, create a file `/etc/systemd/system/isimip-cutout.service` with the following content:

```
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
  config.wsgi:application'

ExecReload=/bin/sh -c '/usr/bin/pkill -HUP -F ${GUNICORN_PID_FILE}'

ExecStop=/bin/sh -c '/usr/bin/pkill -TERM -F ${GUNICORN_PID_FILE}'

[Install]
WantedBy=multi-user.target
```

Reload `systemd`, start and enable the service:

```
systemctl daemon-reload
systemctl start isimip-cutout
systemctl enable isimip-cutout
```

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

to your nginx virtual host configuration.
