from pymongo import MongoClient
import pymongo
from conf import *


def main():
    client = MongoClient(DATABASE_SERVER, DATABASE_PORT)

    # Creating indices for the seeds collection
    client.dionysus.seeds.create_index('domain')
    client.dionysus.seeds.create_index('bad')
    client.dionysus.seeds.create_index([('time_added', pymongo.ASCENDING)])
    client.dionysus.seeds.create_index([('last_scan', pymongo.ASCENDING)])
    client.dionysus.dnskey.create_index('domain')
    client.dionysus.dnskey.create_index('N')
    client.dionysus.dnskey.create_index('algorithm')

if __name__ == "__main__":
    main()
