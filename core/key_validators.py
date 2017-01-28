import fractions

import conf
from dal import db


def hex_to_int(hex_str):
    hex_str = hex_str.split("0x", 1)[-1]
    return int('0x' + hex_str, 0)


def is_even(modulus_hex_str):
    return hex_to_int(modulus_hex_str) % 2 == 0


def is_shared(modulus_hex_str):
    modulus_hex_str = modulus_hex_str.split("0x", 1)[-1]
    res = db.dnskey.find_one({'N': modulus_hex_str})
    return res is not None


def is_factorable(modulus_hex_str):
    moduli = hex_to_int(modulus_hex_str)
    cursor = db.dnskey.find({}, {'N': 1})
    for dnskey in cursor:
        if 'N' not in dnskey:
            continue
        other_moduli = hex_to_int(dnskey['N'])
        gcd = fractions.gcd(moduli, other_moduli)
        if gcd > 1 and gcd != moduli:
            return True
    return False
