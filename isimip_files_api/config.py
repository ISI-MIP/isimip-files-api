'''
this file contains the default configuration, which can be overridden by

* environment variables prefixed with 'FLASK_', either in the environment or a .env file
* a config.toml file at the root of the repository or at a location given by FLASK_CONFIG
'''

# flask environment
ENV = 'production'  # choose from 'production', 'development', 'testing'

# enable Cross-Origin Resource Sharing (CORS)
CORS = True

# toml config file
CONFIG = '../config.toml'

# log level and (optional) path to flask.log
LOG_LEVEL = 'ERROR'
LOG_PATH = None

# the base url the api is running on, in production this will be something like https://api.example.com/api/v1
BASE_URL = 'http://127.0.0.1:5000'

# the output url the download packages will be available on
OUTPUT_URL = 'http://127.0.0.1/api/output/'

# input path to the NetCDF files to process
INPUT_PATH = '..'

# output path to store the created download packages, this directory should be exposed on OUTPUT_URL
OUTPUT_PATH = '..'

# output prefix to be prepended to the job ID to create the filename for the download package
OUTPUT_PREFIX = 'download-'

# maximal number of files to process in one job
MAX_FILES = 32

# list of tasks which can be performed
TASKS = [
    'cutout_bbox',
    'mask_bbox',
    'mask_country',
    'mask_landonly',
    'select_bbox',
    'select_country',
    'select_point'
]

# the tag which designates global files
GLOBAL_TAG = '_global_'

# list of the allowed resolution tags per task
RESOLUTION_TAGS = {
    'cutout_bbox': ['30arcsec', '90arcsec', '300arcsec', '1800arcsec',
                    '15arcmin', '30arcmin', '60arcmin', '120arcmin'],
    'mask_bbox': ['15arcmin', '30arcmin', '60arcmin', '120arcmin'],
    'mask_country': ['30arcmin'],
    'mask_landonly': ['30arcmin'],
    'select_bbox': ['15arcmin', '30arcmin', '60arcmin', '120arcmin'],
    'select_country': ['30arcmin'],
    'select_point': ['15arcmin', '30arcmin', '60arcmin', '120arcmin']
}

# list of the concrete number of gridpoints for each resolution tag
RESOLUTIONS = {
    '30arcsec': (20880, 43200),
    '90arcsec': (6960, 14400),
    '300arcsec': (2088, 4320),
    '1800arcsec': (348, 720),
    '15arcmin': (720, 1440),
    '30arcmin': (360, 720),
    '60arcmin': (180, 360),
    '120arcmin': (90, 180)
}

# the cdo binary on the system, e.g. /usr/bin/cdo
CDO_BIN = 'cdo'

# the ncks binary on the system, e.g. /usr/bin/ncks
NCKS_BIN = 'ncks'

# special settings for the countries
COUNTRYMASKS_FILE_PATH = 'countrymasks.nc'
COUNTRYMASKS_COUNTRIES = [
    'AFG', 'ALB', 'DZA', 'AND', 'AGO', 'ATG', 'ARG', 'ARM', 'AUS', 'AUT',
    'AZE', 'BHS', 'BHR', 'BGD', 'BRB', 'BLR', 'BEL', 'BLZ', 'BEN', 'BTN',
    'BOL', 'BIH', 'BWA', 'BRA', 'BRN', 'BGR', 'BFA', 'BDI', 'KHM', 'CMR',
    'CAN', 'CPV', 'CSID', 'CYM', 'CAF', 'TCD', 'CHL', 'CHN', 'COL', 'COM',
    'COG', 'CRI', 'HRV', 'CUB', 'CYP', 'CZE', 'CIV', 'PRK', 'COD', 'DNK',
    'DJI', 'DMA', 'DOM', 'ECU', 'EGY', 'SLV', 'GNQ', 'ERI', 'EST', 'ETH',
    'FLK', 'FRO', 'FJI', 'FIN', 'FRA', 'GUF', 'PYF', 'ATF', 'GAB', 'GMB',
    'GEO', 'DEU', 'GHA', 'GRC', 'GRL', 'GRD', 'GLP', 'GUM', 'GTM', 'GIN',
    'GNB', 'GUY', 'HTI', 'HMD', 'HND', 'HKG', 'HUN', 'ISL', 'IND', 'IOSID',
    'IDN', 'IRN', 'IRQ', 'IRL', 'IMN', 'ISR', 'ITA', 'JAM', 'JKX', 'JPN',
    'JOR', 'KAZ', 'KEN', 'KIR', 'KWT', 'KGZ', 'LAO', 'LVA', 'LBN', 'LSO',
    'LBR', 'LBY', 'LTU', 'LUX', 'MDG', 'MWI', 'MYS', 'MLI', 'MLT', 'MTQ',
    'MRT', 'MUS', 'MYT', 'MEX', 'FSM', 'MDA', 'MNG', 'MNE', 'MAR', 'MOZ',
    'MMR', 'NAM', 'NPL', 'NLD', 'ANT', 'NCL', 'NZL', 'NIC', 'NER', 'NGA',
    'NIU', 'NOR', 'OMN', 'PSID', 'PAK', 'PLW', 'PSE', 'PAN', 'PNG', 'PRY',
    'PER', 'PHL', 'POL', 'PRT', 'PRI', 'QAT', 'KOR', 'ROU', 'RUS', 'RWA',
    'REU', 'LCA', 'SPM', 'VCT', 'WSM', 'STP', 'SAU', 'SEN', 'SRB', 'SLE',
    'SGP', 'SVK', 'SVN', 'SLB', 'SOM', 'ZAF', 'SGS', 'SSD', 'ESP', 'LKA',
    'SDN', 'SUR', 'SJM', 'SWZ', 'SWE', 'CHE', 'SYR', 'TWN', 'TJK', 'THA',
    'MKD', 'TLS', 'TGO', 'TON', 'TTO', 'TUN', 'TUR', 'TKM', 'GBR', 'UGA',
    'UKR', 'ARE', 'TZA', 'VIR', 'USA', 'URY', 'UZB', 'VUT', 'VEN', 'VNM',
    'ESH', 'YEM', 'ZMB', 'ZWE'
]

# special settings for the land sea mask
LANDSEAMASK_FILE_PATH = 'landseamask.nc'

# configuration for the worker
WORKER_TIMEOUT = 180
WORKER_LOG_FILE = None
WORKER_LOG_LEVEL = 'ERROR'
WORKER_TTL = 86400  # one day
WORKER_FAILURE_TTL = 86400  # one day
WORKER_RESULT_TTL = 604800  # one week
