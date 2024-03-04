# Setup

The service needs [redis](https://redis.io/) to be set up and configured properly. With redit it is especially important to [guard it agains remote access](https://redis.io/topics/security).

The Package and its dependencies can be installed (in a virtual environment) using:

```
pip install -e .
```

The service can be configured using a `config.toml` located at the root of the repository. Please refer to [isimip_files_api/config.py](../isimip_files_api/config.py) for the different settings and their default values.

## Usage

Once the application is setup, the development setup can be controlled using the provided `Makefile`, which some enviroment variables and wraps `flask run`
and `rq worker`.

The development server can be started using:

```
make server
```

The worker for the asynchronous jobs need to be started in a different terminal using:

```
make worker
```

The API is then available at http://127.0.0.1:5000.

## Deployment

When deploying to the internet, a setup of [NGINX](https://www.nginx.com/), (gunicorn)[https://gunicorn.org/], and [systemd](https://www.freedesktop.org/wiki/Software/systemd/) services is recommended, but other services can be used as well. We further assume that a user `isimip` with the group `isimip` and the home `/home/isimip` exists, and that the repository is cloned at `/home/isimip/api`.

Then, as `root`, create a file `/etc/tmpfiles.d/api.conf` with the following content:

```
d /var/log/gunicorn/api  750 isimip isimip
d /var/log/flask/api     750 isimip isimip
d /run/gunicorn/api      750 isimip isimip
```

Create temporary directories using:

```
systemd-tmpfiles --create
```

In order to run the api service with systemd three scripts need to be added to `/etc/systemd/system`

```
# in /etc/systemd/system/api.service

[Unit]
Description=isimip-files-api v2 gunicorn daemon
After=network.target

[Service]
User=isimip
Group=isimip

WorkingDirectory=/srv/isimip/api

Environment=FLASK_APP=isimip_files_api.app
Environment=FLASK_ENV=production
Environment=FLASK_CONFIG=config.toml
Environment=FLASK_REDIS_URL=redis://localhost:6379

Environment=GUNICORN_BIN=env/bin/gunicorn
Environment=GUNICORN_WORKER=3
Environment=GUNICORN_PORT=9001
Environment=GUNICORN_TIMEOUT=120
Environment=GUNICORN_PID_FILE=/run/gunicorn/api-v2/pid
Environment=GUNICORN_ACCESS_LOG_FILE=/var/log/gunicorn/api-v2/access.log
Environment=GUNICORN_ERROR_LOG_FILE=/var/log/gunicorn/api-v2/error.log

ExecStart=/bin/sh -c '${GUNICORN_BIN} \
  --workers ${GUNICORN_WORKER} \
  --pid ${GUNICORN_PID_FILE} \
  --bind localhost:${GUNICORN_PORT} \
  --timeout ${GUNICORN_TIMEOUT} \
  --access-logfile ${GUNICORN_ACCESS_LOG_FILE} \
  --error-logfile ${GUNICORN_ERROR_LOG_FILE} \
  "isimip_files_api.app:create_app()"'

ExecReload=/bin/sh -c '/usr/bin/pkill -HUP -F ${GUNICORN_PID_FILE}'

ExecStop=/bin/sh -c '/usr/bin/pkill -TERM -F ${GUNICORN_PID_FILE}'

[Install]
WantedBy=multi-user.target
```

```
# in /etc/systemd/system/api-worker@.service

[Unit]
Description=RQ worker for isimip-files-api v2 (#%i)
After=network.target

[Service]
Type=simple
User=isimip
Group=isimip

WorkingDirectory=/srv/isimip/api

Environment=LANG=en_US.UTF-8
Environment=LC_ALL=en_US.UTF-8
Environment=LC_LANG=en_US.UTF-8

Environment=FLASK_APP=isimip_files_api.app
Environment=FLASK_ENV=production
Environment=FLASK_CONFIG=config.toml

Environment=RQ_BIN=env/bin/rq
Environment=RQ_WORKER_CLASS=isimip_files_api.worker.Worker
Environment=RQ_REDIS_URL=redis://localhost:6379

ExecStart=/bin/sh -c '${RQ_BIN} worker'
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID

PrivateTmp=true
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Reload `systemd`, start and enable the service:

```
systemctl daemon-reload
systemctl start api
systemctl start api-worker@1
systemctl start api-worker@2  # more worked can be created

systemctl enable api
systemctl enable api-worker@1
systemctl enable api-worker@2
```

From now on, the services can be controlled using:

```
systemctl start api
systemctl stop api
systemctl restart api
```

If the services won't start: `journalctl -xf` might give a clue why.

Lastly, add

```
    location /api/v2 {
        proxy_pass         http://127.0.0.1:9000/;
        proxy_redirect     off;

        proxy_set_header   X-Real-IP            $remote_addr;
        proxy_set_header   X-Forwarded-For      $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Host     $host;
        proxy_set_header   X-Forwarded-Proto    $scheme;
    }

    location /api/v2/public {
        alias /data/api/public;
    }
```

to your NGINX virtual host configuration. The service should then be available at https://yourdomain/api/v1/.

The created files can be automatically deleted using the included `isimip-files-api-clean` script. To do so, add the following to the crontab of the `isimip` user (by using `crontab -e`):

```
# clean files everyday at 5 a.m.
0 5 * * * cd /home/isimip/api; /home/isimip/api/env/bin/isimip-files-api-clean
```
