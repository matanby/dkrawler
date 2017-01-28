import logging


# The server on which the database is listening
DATABASE_SERVER = "localhost"

# The port on which the database is listening
DATABASE_PORT = 27017

# The number of greenlets in the scanning thread pool
GREENLETS_POOL_SIZE = 1024

# The maximal number of consecutive timeouts allowed
MAX_TIMEOUTS = 1

# The period, in seconds, after which seeds which have
# already been scanned are re-scanned
RESCAN_PERIOD = 3 * 24 * 60 * 60  # Three days

# A list of hours at which a scan will be initiated (daily)
DAILY_SCAN_TIMES = ['00:00']

# The interval, in seconds, at which seeds are polled
# when the seed database is empty
SEED_POLL_DELAY = 60  # One minute

# The log level used for the STDOUT stream
LOG_LEVEL_STDOUT = logging.INFO

# The log level used for the info file output stream
LOG_LEVEL_INFO_FILE_HANDLER = logging.DEBUG

# The log level used for the error file output stream
LOG_LEVEL_ERROR_FILE_HANDLER = logging.ERROR

# The info log file used
INFO_LOG_FILE_PATH = 'dkrawler.log'

# The error log file used
ERROR_LOG_FILE_PATH = 'dkrawler.err'

# The format of the log messages
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# The timeout, in seconds, for each query performed
QUERY_TIMEOUT = 7 

# The upper limit of the number of results that should
# be returned by the web app in a single query
WEB_RESULTS_LIMIT = 20

# The directory of the fastgcd binary
FASTGCD_DIR = '/opt/fastgcd/'

# The path of the input file for the fastgcd binary
FASTGCD_INPUT_FILE_PATH = FASTGCD_DIR + 'input_moduli.txt'

# The path of the output file for the fastgcd binary (containing the vulnerable moduli)
FASTGCD_OUTPUT_FILE_PATH = FASTGCD_DIR + 'vulnerable_moduli'

# The path of the output GCDs after computing the fastgcd
FASTGCD_GCD_FILE_PATH = FASTGCD_DIR + 'gcds'

# The host the web-server should bind to
WEB_SERVER_HOST = '0.0.0.0'

# The port the web-server should listen to
WEB_SERVER_PORT = 80

# The directory where exported factorable moduli reports will be saved
FACTORABLE_MODULI_REPORTS_EXPORT_DIR = 'factorable_moduli_reports'

# The directory where exported duplicate moduli reports will be saved
DUPLICATE_MODULI_REPORTS_EXPORT_DIR = 'duplicate_moduli_reports'

# The directory where exported key lengths reports will be saved
KEY_LENGTHS_REPORTS_EXPORT_DIR = 'key_lengths_reports'
