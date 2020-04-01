#!/usr/bin/env python
import os
from pathlib import Path

from redis import Redis
from rq.exceptions import NoSuchJobError
from rq.job import Job

from .settings import OUTPUT_PATH
from .utils import get_hash

redis = Redis()


def clean():
    for root, dirs, files in os.walk(OUTPUT_PATH, topdown=False):
        root_path = Path(root)

        for file_name in files:
            file_path = root_path / file_name

            # construct relative path and job_id
            path = root_path.relative_to(OUTPUT_PATH) / file_name
            job_id = get_hash(path)

            # check if there is a job for this
            try:
                Job.fetch(job_id, connection=redis)
            except NoSuchJobError:
                os.remove(file_path)

        # remove empty directories
        for dir_name in dirs:
            dir_path = root_path / dir_name
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
