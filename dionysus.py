#! /usr/bin/env python

import time
import logging

import dns
import dns.resolver
import dns.exception
from pymongo import MongoClient
import eventlet

import conf
import scanners
import dal

# The shared database client used
DB_CLIENT = None


def configure_logging():
    """
    Configuring the loggers used
    """

    logger = logging.root
    logger.setLevel(conf.LOG_LEVEL)
    fh = logging.FileHandler(conf.LOG_FILE_PATH)
    fh.setLevel(conf.LOG_LEVEL)
    ch = logging.StreamHandler()
    ch.setLevel(conf.LOG_LEVEL)
    formatter = logging.Formatter(conf.LOG_FORMAT)
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(fh)


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


def scan_domain(domain):
    # After forking, the DB_CLIENT might not be set
    global DB_CLIENT
    if DB_CLIENT is None:
        DB_CLIENT = MongoClient(conf.DATABASE_SERVER, conf.DATABASE_PORT)

    dns_resolver = dns.resolver.Resolver()
    dns_resolver.use_edns(0, 0, 4096)
    dns_resolver.timeout = conf.QUERY_TIMEOUT
    dns_resolver.lifetime = conf.QUERY_TIMEOUT
    bad_seed = False
    for scan_func in scanners.scan_functions:
        try:
            exec_retry_scan(scan_func, dns_resolver, domain, DB_CLIENT)
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

    dal.update_seed(DB_CLIENT, domain, bad_seed)


def main():
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
    domains_to_scan = []
    for seed in cursor:
        domain = str(seed['domain'])
        if not client.dionysus.dnskey.find_one({'domain': domain}):
            domains_to_scan.append(domain)
            pool.spawn(scan_domain, domain)

    # Waiting for the scan to end
    pool.waitall()

    scan_time = time.time() - scan_start_time
    logging.info('Total scan time: %s seconds' % scan_time)


if __name__ == "__main__":
    main()
