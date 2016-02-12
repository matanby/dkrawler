import sys
from itertools import izip
from pymongo import MongoClient

sys.path.insert(0, "..")
import conf


def main():

    if len(sys.argv) != 3:
        print "USAGE: %s <vulnerable_moduli_file> <gcds_file>" % sys.argv[0]
        return

    vuln_moduli_file_path = sys.argv[1]
    gcd_file_path = sys.argv[2]

    client = MongoClient(conf.DATABASE_SERVER, conf.DATABASE_PORT)
    vuln_moduli_file = open(vuln_moduli_file_path, 'r')
    gcd_file = open(gcd_file_path, 'r')

    for N_line, gcd_line in izip(vuln_moduli_file, gcd_file):
        N = N_line.strip()
        gcd = gcd_line.strip()
        cursor = client.dionysus.dnskey.find({'N': N})

        print "---------------------------------------------"
        print "N: %s" % N
        print "gcd: %s" % gcd
        for entry in cursor:
            print "Domain: %s" % entry['domain']

    vuln_moduli_file.close()
    gcd_file.close()


if __name__ == "__main__":
    main()
