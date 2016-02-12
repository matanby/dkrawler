import sys
import os
import time
import textwrap
from M2Crypto import X509
from pymongo import MongoClient

sys.path.insert(0, "..")
import conf

# The description of the seeds origin in the database
ORIGIN_DESCRIPTION = "SonarCertificate"

# The increments in which progress is printed
PRINT_STEP = 1000


def main():
    # Reading the commandline arguments
    if len(sys.argv) != 2:
        print "USAGE: %s <SONAR_CERTIFICATE_DIRECTORY>" % sys.argv[0]
        print "    [example: %s /path/to/sonar/certs/]" % sys.argv[0]
        return
    cert_dir_path = sys.argv[1]

    # Connecting to the database
    client = MongoClient(conf.DATABASE_SERVER, conf.DATABASE_PORT)

    # Going over each certificate file
    for cert_file_path in os.listdir(cert_dir_path):
        cert_file = open(os.path.join(cert_dir_path, cert_file_path), 'r')
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
                    'origin': ORIGIN_DESCRIPTION
                }

                client.dionysus.sslcerts.insert(cert_obj)
            except Exception, e:
                print 'Failed to parse certificate, skipping'

        cert_file.close()

if __name__ == "__main__":
    main()
