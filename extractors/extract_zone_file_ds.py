import sys
import re
from pymongo import MongoClient

sys.path.insert(0, "..")
import conf
import dal

# The description of the seeds origin in the database
ORIGIN_DESCRIPTION = "ZoneFileDS"

# The increments in which progress is printed
PRINT_STEP = 1000


def main():

    # Reading the commandline arguments
    if len(sys.argv) != 3:
        print "USAGE: %s <ZONE_FILE_PATH> <ZONE_FILE_ORIGIN>" % sys.argv[0]
        print "    [example: %s com.zone.txt com]" % sys.argv[0]
        return
    zone_file_path = sys.argv[1]
    zone_origin = sys.argv[2].lower()

    # Connecting to the database
    client = MongoClient(conf.DATABASE_SERVER, conf.DATABASE_PORT)

    # Parsing each DS entry in the zone file, and extracting the domain name from it
    # Since the zone files are so large, dnspython fails to handle them...
    # Luckily, the only records we're interested in are DS records (or, equivalently,
    # RRSIG records which sign the DS records).
    # In any case, we can just manually parse these lines
    zone_file = open(zone_file_path, 'r')
    domains_added = 0
    for line in zone_file:

        # Is this a DS record?
        match = re.match("^(\S+)\s+(\d+\s+)?(IN\s+)?DS\s+.*", line)
        if not match:
            continue
        domain = match.group(1).lower()

        # Canonicalizing the domain name
        if domain.endswith('.'):
            domain = domain[:-1]
        if zone_origin != '.' and not domain.endswith(zone_origin):
            domain = domain + "." + zone_origin

        # Inserting the entry to the database
        domains_added += dal.insert_seed(client, domain, ORIGIN_DESCRIPTION)
        if domains_added % PRINT_STEP == 0:
            print '[+] Added %d domains...' % domains_added

    zone_file.close()
    print '[+] Done. Added %s domains.' % domains_added

if __name__ == "__main__":
    main()
