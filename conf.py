import logging


# The server on which the database is listening
DATABASE_SERVER = "localhost"


# The port on which the database is listening
DATABASE_PORT = 27017


# The number of threads in the scanning thread pool
THREAD_POOL_SIZE = 256


# The maximal number of consecutive timeouts allowed
MAX_TIMEOUTS = 1


# The period, in seconds, after which seeds which have already been scanned are re-scanned
RESCAN_PERIOD = 3 * 24 * 60 * 60 #Three days


# The interval, in seconds, at which seeds are polled when the seed database is empty
SEED_POLL_DELAY = 60 # One minute


# The log level used
LOG_LEVEL = logging.DEBUG


# The log file used
LOG_FILE_PATH = 'dionysus.log'


# The format of the log messages
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


# The timeout, in seconds, for each query performed
QUERY_TIMEOUT = 7 
