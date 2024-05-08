FROM python:3.12-slim-bookworm

RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y build-essential cdo nco libgdal-dev

WORKDIR /api

COPY pyproject.toml pyproject.toml
COPY isimip_files_api isimip_files_api

RUN pip3 install .

CMD ["gunicorn", "-b", "0.0.0.0:5000", "isimip_files_api.app:create_app()"]
