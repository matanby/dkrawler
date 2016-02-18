import re
import os
import time
import textwrap
import gzip

from M2Crypto import X509
from pymongo import MongoClient

import conf
from core import dal


# The increments in which progress is printed
PRINT_STEP = 1000


def extract_sonar_certificates(sonar_certificate_directory):
    # Connecting to the database
    client = MongoClient(conf.DATABASE_SERVER, conf.DATABASE_PORT)

    # Going over each certificate file
    for cert_file_path in os.listdir(sonar_certificate_directory):
        cert_file = open(os.path.join(sonar_certificate_directory, cert_file_path), 'r')
        for raw_line in cert_file:
            certhash, cert = raw_line.split(',', 1)
            cert = "\n".join(textwrap.wrap(cert, 76))
            cert = "-----BEGIN CERTIFICATE-----\n{certtext}\n-----END CERTIFICATE-----".format(certtext=cert)

            try:
                x509 = X509.load_cert_string(cert, X509.FORMAT_PEM)
                pkey = x509.get_pubkey()
                cert_obj = {
                    'N': pkey.get_modulus().lower(),
                    'subject': x509.get_subject().as_text(),
                    'issuer': x509.get_issuer().as_text(),
                    'fingerprint': x509.get_fingerprint().lower(),
                    'time_added': time.time(),
                    'origin': 'SonarCertificate'
                }

                client.dionysus.sslcerts.insert(cert_obj)
            except Exception, e:
                print 'Failed to parse certificate, skipping'

        cert_file.close()


def extract_sonar_dns_dnssec(sonar_dns_file):
    # Connecting to the database
    client = MongoClient(conf.DATABASE_SERVER, conf.DATABASE_PORT)

    dns_file = gzip.open(sonar_dns_file, 'r')
    domains_added = 0
    for line in dns_file:
        # Parsing the line
        parts = line.split(",", 2)
        if len(parts) != 3:
            continue
        if parts[1] not in ("ds", "dnskey"):
            continue
        domain = parts[0]

        # Inserting the entry to the database
        domains_added += dal.insert_seed(client, domain, "SonarDNS")
        if domains_added % PRINT_STEP == 0:
            print '[+] Added %d domains...' % domains_added

    dns_file.close()
    print '[+] Done. Added %s domains.' % domains_added


def extract_zone_file_ds(zone_file_path, zone_file_origin):
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
        if zone_file_origin != '.' and not domain.endswith(zone_file_origin):
            domain = domain + "." + zone_file_origin

        # Inserting the entry to the database
        domains_added += dal.insert_seed(client, domain, 'ZoneFileDS')
        if domains_added % PRINT_STEP == 0:
            print '[+] Added %d domains...' % domains_added

    zone_file.close()
    print '[+] Done. Added %s domains.' % domains_added