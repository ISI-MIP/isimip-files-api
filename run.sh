#!/bin/bash

# set environment variables for `flask run` and `rq worker` for development
# in productione, the variables should be set in systemd or docker files
export FLASK_APP=isimip_files_api.app
export FLASK_ENV=development
export RQ_WORKER_CLASS=isimip_files_api.worker.Worker

case $1 in

  server)
    flask run
    ;;

  worker)
    rq worker
    ;;

  *)
    echo "usage: ../run.sh server|worker"
    ;;

esac
