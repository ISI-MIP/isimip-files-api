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
