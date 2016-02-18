import time
import pymongo

import conf


def create_database_indices():
    """
    Creates indexes on the database collections.
    """

    client = pymongo.MongoClient(conf.DATABASE_SERVER, conf.DATABASE_PORT)

    # Create indices for the seeds collection
    client.dionysus.seeds.create_index('domain')
    client.dionysus.seeds.create_index('bad')
    client.dionysus.seeds.create_index([('time_added', pymongo.ASCENDING)])
    client.dionysus.seeds.create_index([('last_scan', pymongo.ASCENDING)])

    # Create indices for the dnskey collection
    client.dionysus.dnskey.create_index('domain')
    client.dionysus.dnskey.create_index('N')
    client.dionysus.dnskey.create_index('algorithm')


def insert_seed(client, domain, origin):
    """
    Inserts the given (FQDN) domain as a scanning seed, from the given origin.
    Returns true IFF the seed was inserted
    """

    # Checking if the seed already exists
    if client.dionysus.seeds.find_one({'domain': domain}):
        return False

    client.dionysus.seeds.insert_one({
        'domain': domain,
        'time_added': time.time(),
        'origin': origin,
        'bad': False,
        'last_scan': 0
    })

    return True


def update_seed(client, domain, is_bad):
    """
    Updates the status of the given seed
    """

    client.dionysus.seeds.update_one({'domain': domain}, {'$set': {'last_scan': time.time(), 'bad': is_bad}})
