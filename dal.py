import time


def update_seed(client, domain, is_bad):
    """
    Updates the status of the given seed
    """
    client.dionysus.seeds.update_one({'domain': domain}, {'$set': {'last_scan': time.time(), 'bad': is_bad}})


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
