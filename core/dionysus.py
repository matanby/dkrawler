import logging
import threading
import time

import dns
import dns.exception
import dns.resolver
import eventlet
from pymongo import MongoClient
import schedule

import conf
import dal
import scanners
from core import reports

SCHEDULER_THREAD = None
LOGGER_INITIALIZED = False


def init():
    # Initialize the logger
    configure_logging()

    # Configure the scan scheduler
    configure_scheduler()


def configure_scheduler():
    global SCHEDULER_THREAD

    if SCHEDULER_THREAD is not None:
        return

    # Schedule future scan procedures
    for hour in conf.DAILY_SCAN_TIMES:
        schedule.every().day.at(hour).do(scan_domains)
        schedule.every().day.at(hour).do(generate_reports)

    def scan_scheduler():
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception, e:
                logging.error('Error while running a scheduled scan: %s' % e)

    SCHEDULER_THREAD = threading.Thread(target=scan_scheduler)
    SCHEDULER_THREAD.start()


def configure_logging():
    """
    Configuring the loggers used
    """

    global LOGGER_INITIALIZED

    if LOGGER_INITIALIZED:
        return

    formatter = logging.Formatter(conf.LOG_FORMAT)

    ifh = logging.FileHandler(conf.INFO_LOG_FILE_PATH)
    ifh.setLevel(conf.LOG_LEVEL_INFO_FILE_HANDLER)
    ifh.setFormatter(formatter)

    efh = logging.FileHandler(conf.ERROR_LOG_FILE_PATH)
    efh.setLevel(conf.LOG_LEVEL_ERROR_FILE_HANDLER)
    efh.setFormatter(formatter)

    sh = logging.StreamHandler()
    sh.setLevel(conf.LOG_LEVEL_STDOUT)
    sh.setFormatter(formatter)

    logger = logging.root
    logger.setLevel(logging.DEBUG)
    logger.addHandler(sh)
    logger.addHandler(ifh)
    logger.addHandler(efh)

    LOGGER_INITIALIZED = True


def exec_retry_scan(scan_func, dns_resolver, domain, client):
    num_timeouts = 0
    while True:
        try:
            scan_func(dns_resolver, domain, client)
            return
        except dns.exception.Timeout as e:
            num_timeouts += 1
            logging.debug('Got %d timeouts when querying %s' % (num_timeouts, domain))
            if num_timeouts == conf.MAX_TIMEOUTS:
                raise


def scan_domain(client, domain):
    dns_resolver = dns.resolver.Resolver()
    dns_resolver.use_edns(0, 0, 4096)
    dns_resolver.timeout = conf.QUERY_TIMEOUT
    dns_resolver.lifetime = conf.QUERY_TIMEOUT
    bad_seed = False
    for scan_func in scanners.scan_functions:
        try:
            exec_retry_scan(scan_func, dns_resolver, domain, client)
        except dns.resolver.NXDOMAIN as e:
            logging.warning('Got NXDomain when trying to scan %s, marking bad seed' % domain)
            bad_seed = True
            break
        except dns.resolver.YXDOMAIN as e:
            logging.warning('Got YXDomain when trying to scan %s, marking bad seed' % domain)
            bad_seed = True
            break
        except dns.resolver.NoNameservers as e:
            logging.warning('No NS for %s, marking bad seed' % domain)
            bad_seed = True
            break
        except dns.resolver.NoAnswer as e:
            logging.warning('No answer received for %s, skipping' % domain)
        except dns.exception.Timeout as e:
            logging.warning('Got timeout when querying %s, skipping' % domain)
        except Exception, ex:
            logging.exception('Unexpected exception when querying %s' % domain)

    dal.update_seed(client, domain, bad_seed)


def scan_domains():
    configure_logging()
    client = MongoClient(conf.DATABASE_SERVER, conf.DATABASE_PORT)

    # Monkey patch system libraries to behave be non-blocking.
    eventlet.monkey_patch()

    # Creating greenlets pool to which the scans are distributed
    pool = eventlet.GreenPool(conf.GREENLETS_POOL_SIZE)

    # Adding a scan task for each seed
    logging.info('Searching for seeds')

    scan_start_time = time.time()

    cursor = client.dionysus.seeds.find({
        'last_scan': {'$lt': time.time() - conf.RESCAN_PERIOD},
        'bad': False
    })

    logging.info('Found %d seeds' % cursor.count())
    scan_id = client.dionysus.scans.insert_one({
        'start_time': time.time(),
        'end_time': -1,
        'number_of_domains': cursor.count(),
    }).inserted_id

    for seed in cursor:
        domain = str(seed['domain'])
        # if not client.dionysus.dnskey.find_one({'domain': domain}):
        pool.spawn(scan_domain, client, domain)

    # Waiting for the scan to end
    pool.waitall()

    scan_end_time = time.time()
    client.dionysus.scans.update_one({'_id': scan_id}, {'$set': {'end_time': scan_end_time}})

    scan_time = scan_end_time - scan_start_time
    logging.info('Total scan time: %s seconds' % scan_time)


def generate_reports():
    reports.key_lengths()
    reports.duplicate_moduli()
    reports.factorable_moduli()
