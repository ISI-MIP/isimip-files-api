import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path().cwd() / '.env')

LOG_FILE = os.getenv('LOG_FILE')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'ERROR')

BASE_URL = os.getenv('BASE_URL', 'http://127.0.0.1:5000').rstrip('/')
OUTPUT_URL = os.getenv('OUTPUT_URL', 'http://127.0.0.1/api/output/').rstrip('/')

INPUT_PATH = Path(os.getenv('INPUT_PATH', 'input'))
OUTPUT_PATH = Path(os.getenv('OUTPUT_PATH', 'output'))
OUTPUT_PREFIX = os.getenv('OUTPUT_PREFIX', 'isimip-files-api-')

CDO_BIN = os.getenv('CDO_BIN', 'cdo')
NCKS_BIN = os.getenv('NCKS_BIN', 'ncks')

CORS = os.getenv('CORS', '').upper() in ['TRUE', 1]
GLOBAL = os.getenv('GLOBAL', '_global_')
MAX_FILES = int(os.getenv('MAX_FILES', '32'))

WORKER_TIMEOUT = int(os.getenv('WORKER_TIMEOUT', '180'))
WORKER_LOG_FILE = os.getenv('WORKER_LOG_FILE')
WORKER_LOG_LEVEL = os.getenv('WORKER_LOG_LEVEL', 'ERROR')
WORKER_TTL = int(os.getenv('RESULT_TTL', '86400'))          # one day
WORKER_FAILURE_TTL = int(os.getenv('WORKER_FAILURE_TTL', '86400'))  # one day
WORKER_RESULT_TTL = int(os.getenv('WORKER_RESULT_TTL', '604800'))  # one week

RESOLUTIONS = {
    '30arcsec': (20880, 43200),
    '90arcsec': (6960, 14400),
    '300arcsec': (2088, 4320),
    '1800arcsec': (348, 720),
    '30arcmin': (360, 720),
    '60arcmin': (180, 360),
    '120arcmin': (90, 180)
}

TASKS = {
    'cutout_bbox': ['30arcsec', '90arcsec', '300arcsec', '1800arcsec', '30arcmin', '60arcmin', '120arcmin'],
    'mask_bbox': ['30arcmin', '60arcmin', '120arcmin'],
    'mask_country': ['30arcmin'],
    'mask_landonly': ['30arcmin'],
    'select_bbox': ['30arcmin'],
    'select_country': ['30arcmin', '60arcmin', '120arcmin'],
    'select_point': ['30arcmin', '60arcmin', '120arcmin']
}

COUNTRYMASKS_FILE_PATH = Path(os.getenv('COUNTRYMASKS_FILE_PATH', 'countrymasks.nc'))
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

LANDSEAMASK_FILE_PATH = Path(os.getenv('LANDSEAMASK_FILE_PATH', 'landseamask.nc'))
