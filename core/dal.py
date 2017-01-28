import time
import pymongo

import conf


db = pymongo.MongoClient(conf.DATABASE_SERVER, conf.DATABASE_PORT).dkrawler


def create_database_indices():
    """
    Creates indexes on the database collections.
    """

    # Create indices for the seeds collection
    db.seeds.create_index('domain')
    db.seeds.create_index('bad')
    db.seeds.create_index([('time_added', pymongo.ASCENDING)])
    db.seeds.create_index([('last_scan', pymongo.ASCENDING)])

    # Create indices for the dnskey collection
    db.dnskey.create_index('domain')
    db.dnskey.create_index([('N', pymongo.HASHED)])
    db.dnskey.create_index('algorithm')

    # Create indices for the scans collection
    db.scans.create_index([('start_time', pymongo.DESCENDING)])

    # Create indices for the key_lengths collection
    db.key_lengths.create_index([('creation_time', pymongo.DESCENDING)])

    # Create indices for the duplicate_moduli collection
    db.duplicate_moduli.create_index([('creation_time', pymongo.DESCENDING)])

    # Create indices for the factorable_moduli collection
    db.factorable_moduli.create_index([('creation_time', pymongo.DESCENDING)])


def insert_seed(domain, origin):
    """
    Inserts the given (FQDN) domain as a scanning seed, from the given origin.
    Returns true IFF the seed was inserted
    """

    # Checking if the seed already exists
    if db.seeds.find_one({'domain': domain}):
        return False

    db.seeds.insert_one({
        'domain': domain,
        'time_added': time.time(),
        'origin': origin,
        'bad': False,
        'last_scan': 0
    })

    return True


def update_seed(domain, is_bad):
    """
    Updates the status of the given seed
    """

    db.seeds.update_one({'domain': domain}, {'$set': {'last_scan': time.time(), 'bad': is_bad}})


def reset_seeds_status():
    """
    Resets the status of all seeds to initial values (bad: False, last_scan: 0)
    """

    print db.seeds.update_many({}, {'$set': {'bad': False, 'last_scan': 0}})
