import fractions

from pymongo.mongo_client import MongoClient

import conf


def hex_to_int(hex_str):
    hex_str = hex_str.split("0x", 1)[-1]
    return int('0x' + hex_str, 0)


def is_even(moduli_hex_str):
    return hex_to_int(moduli_hex_str) % 2 == 0


def is_shared(moduli_hex_str):
    moduli_hex_str = moduli_hex_str.split("0x", 1)[-1]
    db = MongoClient(conf.DATABASE_SERVER, conf.DATABASE_PORT)
    res = db.dionysus.dnskey.find_one({'N': moduli_hex_str})
    return res is not None


def is_factorable(moduli_hex_str):
    moduli = hex_to_int(moduli_hex_str)
    db = MongoClient(conf.DATABASE_SERVER, conf.DATABASE_PORT)
    cursor = db.dionysus.dnskey.find({}, {'N': 1})
    for dnskey in cursor:
        if 'N' not in dnskey:
            continue
        other_moduli = hex_to_int(dnskey['N'])
        gcd = fractions.gcd(moduli, other_moduli)
        if gcd > 1 and gcd != moduli:
            return True
    return False
