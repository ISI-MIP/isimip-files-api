isimip-files-api
================

A webservice to asynchronously mask regions from NetCDF files, using [Flask](https://palletsprojects.com/p/flask/) and [RQ](https://python-rq.org/).

Setup
-----

The service needs [redis](https://redis.io/) to be set up and configured properly. With redit it is especially important to [guard it agains remote access](https://redis.io/topics/security).

The python dependencies can be installed (in a virtual environment) using:

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

The worker for the asynchronous jobs need to be started in a different terminal session using:

```
rq worker
```

Asynchronous jobs are created using a HTTP `POST` request to the root api entpoint. To mask everything but a bounding box in lat/lon use:

```
POST /
{
  "path": "path/to/file.nc",
  "task": "mask_bbox",
  "bbox": [south, north, west, east]
}
```

where `south`, `north`, `west`, `east` are floats and `path` is the path to the file on the server relative to `INPUT_PATH` given in `.env`. For a country use:

```
POST /
{
  "path": "path/to/file.nc",
  "task": "mask_country",
  "country": "deu"
}
```

for, e. g. Germany. To mask out all sea and antarctica data use:

```
POST /
{
  "path": "path/to/file.nc",
  "task": "mask_landonly"
}
```

The response is a JSON like this:

```
{
    "file_name": "isimip-download-1eff769a7edd0a8076f11dc85609f0090562a671.zip",
    "file_url": "https://files.isimip.org/api/v1/output/isimip-download-1eff769a7edd0a8076f11dc85609f0090562a671.zip",
    "id": "5741ca0e7f824d37ef23e107f5e5261a31e974a6",
    "job_url": "http://127.0.0.1:5000/5741ca0e7f824d37ef23e107f5e5261a31e974a6",
    "meta": {},
    "status": "queued",
    "ttl": 604800
}
```

Performing the initial request again, or performing a `GET` on the url given in `job_url`, will give an update on the job status, e.g.

```
{
    "file_name": "isimip-download-1eff769a7edd0a8076f11dc85609f0090562a671.zip",
    "file_url": "https://files.isimip.org/api/v1/output/isimip-download-1eff769a7edd0a8076f11dc85609f0090562a671.zip",
    "id": "5741ca0e7f824d37ef23e107f5e5261a31e974a6",
    "job_url": "http://127.0.0.1:5000/5741ca0e7f824d37ef23e107f5e5261a31e974a6",
    "meta": {"created_files": 1, "total_files": 1},
    "status": "finished",
    "ttl": 604800
}
```

When the job is finished, the resulting file is located at `file_name` relative to the path given in `OUTPUT_PATH` in `.env`. When `OUTPUT_PATH` is made public via a web server (e.g. NGINX, see below for deployment), the file can be downloaded under the URL given by `file_url`.

The following exaples can be used from the command line with [httpie](https://httpie.org/) or [curl](https://curl.haxx.se/):

```
http :5000 path=path/to/file.nc bbox=:"[0, 10, 0, 10]"
http :5000 path=path/to/file.nc country=deu
http :5000 path=path/to/file.nc landonly:=true

curl 127.0.0.1:5000 -H "Content-Type: application/json" -d '{"path": "path/to/file.nc", "task": "mask_bbox","bbox": [south, north, west, east]}'
curl 127.0.0.1:5000 -H "Content-Type: application/json" -d '{"path": "path/to/file.nc", "task": "mask_country", "country": "deu"}'
curl 127.0.0.1:5000 -H "Content-Type: application/json" -d '{"path": "path/to/file.nc", "task": "mask_landonly"}'
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
# in /etc/systemd/system/isimip-files-api.service

[Unit]
Description=pseudo-service to start/stop all isimip-files-api services

[Service]
Type=oneshot
ExecStart=/bin/true
RemainAfterExit=yes

[Install]
WantedBy=network.target
```

```
# in /etc/systemd/system/isimip-files-api-app.service

[Unit]
Description=isimip-api gunicorn daemon
PartOf=isimip-files-api.service
After=isimip-files-api.service

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
  "isimip_files_api:app:create_app()"'

ExecReload=/bin/sh -c '/usr/bin/pkill -HUP -F ${GUNICORN_PID_FILE}'

ExecStop=/bin/sh -c '/usr/bin/pkill -TERM -F ${GUNICORN_PID_FILE}'

[Install]
WantedBy=isimip-api.target
```

```
# in /etc/systemd/system/isimip-files-api-worker.service

[Unit]
Description=RQ worker for isimip-api
PartOf=isimip-files-api.service
After=isimip-files-api.service

[Service]
User=isimip
Group=isimip

WorkingDirectory=/home/isimip/api
Environment=LANG=en_US.UTF-8
Environment=LC_ALL=en_US.UTF-8
Environment=LC_LANG=en_US.UTF-8

ExecStart=/home/isimip/api/env/bin/rq worker -w 'isimip_files_api.worker.LogWorker'

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

to your NGINX virtual host configuration. The service should then be available at https://yourdomain/api/v1/.

The created files can be automatically deleted using the included `isimip-files-api-clean` script. To do so, add the following to the crontab of the `isimip` user (by using `crontab -e`):

```
# clean files everyday at 5 a.m.
0 5 * * * cd /home/isimip/api; /home/isimip/api/env/bin/isimip-files-api-clean
```
