from pymongo import MongoClient
import os
import itertools

import conf


def key_lengths():
    client = MongoClient(conf.DATABASE_SERVER, conf.DATABASE_PORT)
    cursor = client.dionysus.dnskey.find()

    # Creating a key length histogram
    n_lengths = {}
    for entry in cursor:
        if 'N' not in entry:
            continue
        n_len = len(entry['N'])
        if n_len not in n_lengths:
            n_lengths[n_len] = 1
        else:
            n_lengths[n_len] += 1

    # Printing the actual key length histogram, sorted
    for length in sorted(n_lengths.keys()):
        print "%d bits : %d" % (length * 4, n_lengths[length])


def create_moduli_file(moduli_file_path):
    client = MongoClient(conf.DATABASE_SERVER, conf.DATABASE_PORT)
    moduli_file = open(moduli_file_path, 'w')
    cursor = client.dionysus.dnskey.find({'N': {'$exists': True}})
    for entry in cursor:
        moduli_file.write(entry['N'])
        moduli_file.write('\n')
    moduli_file.close()

    # After the file is created, filter it through sort-uniq
    os.system('cat %s | sort | uniq > %s_' % (moduli_file_path, moduli_file_path))
    os.system('rm %s' % moduli_file_path)
    os.system('mv %s_ %s' % (moduli_file_path, moduli_file_path))


def duplicate_moduli():
    client = MongoClient(conf.DATABASE_SERVER, conf.DATABASE_PORT)
    cursor = client.dionysus.dnskey.find({'N': {'$exists': True}})
    n_map = {}

    for entry in cursor:
        n = entry['N']
        if n not in n_map:
            n_map[n] = 1
        else:
            n_map[n] += 1

    for n in n_map:
        if n_map[n] > 1:
            print "---------------------------------------------"
            print "Duplicate modulus!"
            print n
            print "Found in:"
            cursor = client.dionysus.dnskey.find({'N': n})
            for entry in cursor:
                print entry['domain']


def vulnerable_moduli_info(vuln_moduli_file_path, gcd_file_path):
    client = MongoClient(conf.DATABASE_SERVER, conf.DATABASE_PORT)
    vuln_moduli_file = open(vuln_moduli_file_path, 'r')
    gcd_file = open(gcd_file_path, 'r')

    for n_line, gcd_line in itertools.izip(vuln_moduli_file, gcd_file):
        n = n_line.strip()
        gcd = gcd_line.strip()
        cursor = client.dionysus.dnskey.find({'N': n})

        print "---------------------------------------------"
        print "N: %s" % n
        print "gcd: %s" % gcd
        for entry in cursor:
            print "Domain: %s" % entry['domain']

    vuln_moduli_file.close()
    gcd_file.close()

