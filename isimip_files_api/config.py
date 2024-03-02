'''
this file contains the default configuration, which can be overridden by

* environment variables prefixed with 'FLASK_', either in the environment or a .env file
* a config.toml file at the root of the repository or at a location given by FLASK_CONFIG
'''

# flask environment
ENV = 'production'  # choose from 'production', 'development', 'testing'

# enable Cross-Origin Resource Sharing (CORS)
CORS = True

# log level and (optional) path to flask.log
LOG_LEVEL = 'ERROR'
LOG_PATH = None

# the base url the api is running on, in production this will be something like https://api.example.com/api/v2
BASE_URL = 'http://127.0.0.1:5000'

# the output url the download packages will be available on
OUTPUT_URL = 'http://127.0.0.1/api/output/'

# input path to the NetCDF files to process
INPUT_PATH = 'input'

# temporary path to store interim files
TMP_PATH = 'tmp'

# output path to store the created download packages, this directory should be exposed on OUTPUT_URL
OUTPUT_PATH = 'output'

# output prefix to be prepended to the job ID to create the filename for the download package
OUTPUT_PREFIX = 'download-'

# maximal number of files to process in one job
MAX_FILES = 32

# list of commands which can be executed
COMMANDS = [
    'isimip_files_api.commands.cdo.CdoCommand',
    'isimip_files_api.commands.python.create_mask.CreateMaskCommand',
    'isimip_files_api.commands.ncks.NcksCommand'
]

# maximum number of commands which can be performed
MAX_COMMANDS = 8

# list of operations which can be performed
OPERATIONS = [
    'isimip_files_api.operations.cdo.SelectBBoxOperation',
    'isimip_files_api.operations.cdo.SelectCountryOperation',
    'isimip_files_api.operations.cdo.SelectPointOperation',
    'isimip_files_api.operations.cdo.MaskBBoxOperation',
    'isimip_files_api.operations.cdo.MaskMaskOperation',
    'isimip_files_api.operations.cdo.MaskCountryOperation',
    'isimip_files_api.operations.cdo.MaskLandonlyOperation',
    'isimip_files_api.operations.cdo.ComputeMeanOperation',
    'isimip_files_api.operations.cdo.OutputCsvOperation',
    'isimip_files_api.operations.python.create_mask.CreateMaskOperation',
    'isimip_files_api.operations.ncks.CutOutBBoxOperation'
]

# maximum number of operations which can be performed
MAX_OPERATIONS = 16

# the tag which designates global files, this tag will be replaced by the region
# specifier of the operations, if set to None, the region will be appended
GLOBAL_TAG = '_global_'

# the cdo binary on the system, e.g. /usr/bin/cdo
CDO_BIN = 'cdo'

# the ncks binary on the system, e.g. /usr/bin/ncks
NCKS_BIN = 'ncks'

# the binary used to create masks from geojson and shapefiles,
# shipped with this software and located in scripts/create_mask.py
CREATE_MASK_BIN = 'create-mask'

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

# redis configuration
REDIS_URL = 'redis://localhost:6379'

# configuration for the worker
WORKER_TIMEOUT = 180
WORKER_LOG_FILE = None
WORKER_LOG_LEVEL = 'ERROR'
WORKER_TTL = 86400  # one day
WORKER_FAILURE_TTL = 86400  # one day
WORKER_RESULT_TTL = 604800  # one week
