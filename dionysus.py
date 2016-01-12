import sys, random, time, logging
import dns
import dns.resolver
import dns.exception
from pymongo import MongoClient
from multiprocessing import Pool
from conf import *
import scanners
import dal

#The shared database client used
DB_CLIENT = None

def configure_logging():
	'''
	Configuring the loggers used
	'''	
	logger = logging.root
	logger.setLevel(LOG_LEVEL)
	fh = logging.FileHandler(LOG_FILE_PATH)
	fh.setLevel(LOG_LEVEL)
	ch = logging.StreamHandler()
	ch.setLevel(LOG_LEVEL)
	formatter = logging.Formatter(LOG_FORMAT)
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
			logging.warning('Got %d timeouts when querying %s' % (num_timeouts, domain))
			if num_timeouts == MAX_TIMEOUTS:
				raise

def scan_domain(domain):

	#After forking, the DB_CLIENT might not be set
	global DB_CLIENT
	if DB_CLIENT == None:
		DB_CLIENT = MongoClient(DATABASE_SERVER, DATABASE_PORT)

	dns_resolver = dns.resolver.Resolver()
	dns_resolver.use_edns(0,0,4096)
	dns_resolver.timeout = QUERY_TIMEOUT
	dns_resolver.lifetime = QUERY_TIMEOUT
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
	client = MongoClient(DATABASE_SERVER, DATABASE_PORT)

	#Creating the thread pool to which the scans are distributed
	pool = Pool(processes=THREAD_POOL_SIZE)

	#Adding a scan task for each seed
	logging.info('Searching for seeds')
#	cursor = client.dionysus.seeds.find({'last_scan':{'$lt':time.time() - RESCAN_PERIOD},
#										 'bad': False});
	cursor = client.dionysus.seeds.find({'bad': False});
	logging.info('Found %d seeds' % cursor.count())
	for seed in cursor:
		domain = str(seed['domain'])
		if not client.dionysus.dnskey.find_one({'domain':domain}):
			pool.apply_async(scan_domain, (domain,))

	#Waiting for the scan to end
	pool.close()
	pool.join()

if __name__ == "__main__":
	main()
