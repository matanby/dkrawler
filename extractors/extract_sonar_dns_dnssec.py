import sys, re
from pymongo import MongoClient

sys.path.insert(0, "..")
import conf
import dal

#The description of the seeds origin in the database
ORIGIN_DESCRIPTION = "SonarDNS"

#The increments in which progress is printed
PRINT_STEP = 1000

def main():

	#Reading the commandline arguments
	if len(sys.argv) != 2:
		print "USAGE: %s <SONAR_DNS_FILE>" % sys.argv[0]
		print "    [example: %s /path/to/sonar/dns.txt]" % sys.argv[0]
		return
	dns_file_path = sys.argv[1]

	#Connecting to the database
	client = MongoClient(conf.DATABASE_SERVER, conf.DATABASE_PORT)

	dns_file = open(dns_file_path, 'r')
	domains_added = 0
	for line in dns_file:	
	
		#Parsing the line
		parts = line.split(",", 2)
		if len(parts) != 3:
			continue
		if parts[1] not in ("ds", "dnskey"):
			continue
		domain = parts[0]

		#Inserting the entry to the database 
		domains_added += dal.insert_seed(client, domain, ORIGIN_DESCRIPTION)
		if domains_added % PRINT_STEP == 0:
			print '[+] Added %d domains...' % domains_added

	dns_file.close()
	print '[+] Done. Added %s domains.' % domains_added

if __name__ == "__main__":
	main()
