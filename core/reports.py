import time
from datetime import datetime
import os
import itertools
import conf
import subprocess

from dal import db


def key_lengths():
    cursor = db.dnskey.find()

    # Creating a key length histogram
    n_lengths = {}
    for entry in cursor:
        if 'N' not in entry:
            continue

        n_len = len(entry['N']) * 4
        n_lengths.setdefault(n_len, 0)
        n_lengths[n_len] += 1

        if n_len <= 768:
            entry['is_factorable'] = True
            entry.save()

    # Printing the actual key length histogram, sorted
    for length in sorted(n_lengths.keys()):
        print "%d bits : %d" % (length, n_lengths[length])

    db.key_lengths.insert_one({
        'creation_time': time.time(),
        'n_lengths': {str(k): v for k, v in n_lengths.iteritems()}
    })


def duplicate_moduli():
    cursor = db.dnskey.find({'N': {'$exists': True}})
    n_map = {}

    for entry in cursor:
        n = entry['N']
        n_map.setdefault(n, 0)
        n_map[n] += 1

    duplicates = {}

    for n in n_map:
        if n_map[n] > 1:
            print "---------------------------------------------"
            print "Duplicate modulus!"
            print n
            print "Found in:"
            duplicates[n] = []
            cursor = db.dnskey.find({'N': n})
            for entry in cursor:
                print entry['domain']
                duplicates[n].append(entry['domain'])
                entry['is_shared'] = True
                entry.save()

    db.duplicate_moduli.insert_one({
        'creation_time': time.time(),
        'duplicates': duplicates,
    })


def factorable_moduli():
    # Creating the moduli file
    moduli_file = open(conf.FASTGCD_INPUT_FILE_PATH, 'w')
    cursor = db.dnskey.find({'N': {'$exists': True}})
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
        cursor = db.dnskey.find({'N': n})
    
        # Collecting the affected domains
        domains = []
        for entry in cursor:
            domains.append(entry['domain'])
            entry['is_factorable'] = True
            entry.save()

        results.append({
            'n': n,
            'gcd': gcd,
            'domains': domains,
        })

    vuln_moduli_file.close()
    gcd_file.close()

    db.factorable_moduli.insert_one({
        'creation_time': time.time(),
        'results': results,
    })


def export_key_lengths_reports():
    reports = db.key_lengths.find({})

    if not os.path.exists(conf.KEY_LENGTHS_REPORTS_EXPORT_DIR):
        os.makedirs(conf.KEY_LENGTHS_REPORTS_EXPORT_DIR)

    for report in reports:
        formatted_time = datetime.fromtimestamp(report['creation_time']).strftime('%Y%m%d_%H%M%S')
        filename = '%s.csv' % formatted_time
        filepath = os.path.join(conf.KEY_LENGTHS_REPORTS_EXPORT_DIR, filename)
        n_lengths = report['n_lengths']

        with open(filepath, 'w') as f:
            f.write('N Length,Total Count\n')

            for n_length, total_count in n_lengths.iteritems():
                f.write('%s,%s\n' % (n_length, total_count))


def export_duplicate_moduli_reports():
    reports = db.duplicate_moduli.find({})

    if not os.path.exists(conf.DUPLICATE_MODULI_REPORTS_EXPORT_DIR):
        os.makedirs(conf.DUPLICATE_MODULI_REPORTS_EXPORT_DIR)

    for report in reports:
        formatted_time = datetime.fromtimestamp(report['creation_time']).strftime('%Y%m%d_%H%M%S')
        filename = '%s.csv' % formatted_time
        filepath = os.path.join(conf.DUPLICATE_MODULI_REPORTS_EXPORT_DIR, filename)
        duplicates = report['duplicates']

        with open(filepath, 'w') as f:
            f.write('domain,N\n')

            for n in duplicates.keys():
                for domain in duplicates[n]:
                    f.write('%s,%s\n' % (domain, n))


def export_factorable_moduli_reports():
    reports = db.factorable_moduli.find({})

    if not os.path.exists(conf.FACTORABLE_MODULI_REPORTS_EXPORT_DIR):
        os.makedirs(conf.FACTORABLE_MODULI_REPORTS_EXPORT_DIR)

    for report in reports:
        formatted_time = datetime.fromtimestamp(report['creation_time']).strftime('%Y%m%d_%H%M%S')
        filename = '%s.csv' % formatted_time
        filepath = os.path.join(conf.FACTORABLE_MODULI_REPORTS_EXPORT_DIR, filename)
        results = report['results']

        with open(filepath, 'w') as f:
            f.write('domain,N,gcd\n')

            for result in results:
                for domain in result['domains']:
                    f.write('%s,%s,%s\n' % (domain, result['n'], result['gcd']))
