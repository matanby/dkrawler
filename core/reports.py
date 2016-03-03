import time
from pymongo import MongoClient
import os
import itertools
import conf
import subprocess


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

    client.dionysus.key_lengths.insert_one({
        'creation_time': time.time(),
        'n_lengths': {str(k * 4): v for k, v in n_lengths.iteritems()}
    })


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

    duplicates = {}

    for n in n_map:
        if n_map[n] > 1:
            print "---------------------------------------------"
            print "Duplicate modulus!"
            print n
            print "Found in:"
            duplicates[n] = []
            cursor = client.dionysus.dnskey.find({'N': n})
            for entry in cursor:
                print entry['domain']
                duplicates[n].append(entry['domain'])

    client.dionysus.duplicate_moduli.insert_one({
        'creation_time': time.time(),
        'duplicates': duplicates,
    })


def factorable_moduli():
    # Creating the moduli file
    client = MongoClient(conf.DATABASE_SERVER, conf.DATABASE_PORT)
    moduli_file = open(conf.FASTGCD_INPUT_FILE_PATH, 'w')
    cursor = client.dionysus.dnskey.find({'N': {'$exists': True}})
    for entry in cursor:
        moduli_file.write(entry['N'])
        moduli_file.write('\n')
    moduli_file.close()

    # After the file is created, filter it through sort-uniq
    os.system('cat %s | sort | uniq > %s_' % (conf.FASTGCD_INPUT_FILE_PATH, conf.FASTGCD_INPUT_FILE_PATH))
    os.system('rm %s' % conf.FASTGCD_INPUT_FILE_PATH)
    os.system('mv %s_ %s' % (conf.FASTGCD_INPUT_FILE_PATH, conf.FASTGCD_INPUT_FILE_PATH))

    # Executing fastgcd and waiting for it to complete
    proc = subprocess.Popen([conf.FASTGCD_DIR + 'fastgcd', conf.FASTGCD_INPUT_FILE_PATH], cwd=conf.FASTGCD_DIR)
    proc.wait()

    # Now that the process has completed, read the moduli and GCDs from the result files,
    # and insert them into the database
    vuln_moduli_file = open(conf.FASTGCD_OUTPUT_FILE_PATH, 'r')
    gcd_file = open(conf.FASTGCD_GCD_FILE_PATH, 'r')

    results = []

    for n_line, gcd_line in itertools.izip(vuln_moduli_file, gcd_file):
        n = n_line.strip()
        gcd = gcd_line.strip()
        cursor = client.dionysus.dnskey.find({'N': n})
    
        # Collecting the affected domains
        domains = []
        for entry in cursor:
            domains.append(entry['domain'])

        results.append({
            'n': n,
            'gcd': gcd,
            'domains': domains,
        })

    vuln_moduli_file.close()
    gcd_file.close()

    client.dionysus.factorable_moduli.insert_one({
        'creation_time': time.time(),
        'results': results,
    })

