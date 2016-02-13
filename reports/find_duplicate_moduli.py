#! /usr/bin/env python

import sys
from pymongo import MongoClient

sys.path.insert(0, "..")
import conf


def main():
    client = MongoClient(conf.DATABASE_SERVER, conf.DATABASE_PORT)
    cursor = client.dionysus.dnskey.find({'N': {'$exists': True}})
    N_map = {}
    for entry in cursor:
        N = entry['N']
        if N not in N_map:
            N_map[N] = 1
        else:
            N_map[N] += 1

    for N in N_map:
        if N_map[N] > 1:
            print "---------------------------------------------"
            print "Duplicate modulus!"
            print N
            print "Found in:"
            cursor = client.dionysus.dnskey.find({'N': N})
            for entry in cursor:
                print entry['domain']

if __name__ == "__main__":
    main()
