import dns.resolver
import logging
import time
import struct

# The names of the DNSKEY algorithm types
algorithm_names = {
    1: 'RSAMD5',
    2: 'DH',
    3: 'DSA',
    5: 'RSASHA1',
    6: 'DSA-NSEC3-SHA1',
    7: 'RSASHA1-NSEC3-SHA1',
    8: 'RSASHA256',
    10: 'RSASHA512',
    12: 'ECC-GOST',
    13: 'ECDSAP256SHA256',
    14: 'ECDSAP384SHA384'
}

# The algorithm numbers for RSA keys
rsa_algorithms = [1, 5, 7, 8, 10]


def scan(resolver, domain, db):
    """
    Scans the given domain name for its DNSKEY records
    """

    try:
        logging.debug(domain)
        rrset = resolver.query(domain, 'DNSKEY')
        db.dnskey.remove({'domain': domain})

        for rr in rrset:
            if not hasattr(rr, 'flags'):
                logging.warning('No `flags` attribute found in the RR record of domain %s' % domain)
                continue

            # Simplifying some of the raw information in the DNSKEY result
            is_zsk = (rr.flags & 0x100) > 0
            is_ksk = (rr.flags & 0x001) > 0
            is_revoked = (rr.flags & 0x80) > 0
            algorithm_name = 'unknown'
            if rr.algorithm in algorithm_names:
                algorithm_name = algorithm_names[rr.algorithm]

            obj = {
                'ttl': rrset.ttl,
                'time_added': time.time(),
                'domain': domain,
                'protocol': rr.protocol,
                'algorithm': rr.algorithm,
                'flags': rr.flags,
                'is_zsk': is_zsk,
                'is_ksk': is_ksk,
                'is_revoked': is_revoked,
                'algorithm_name': algorithm_name,
                'key': rr.key.encode("hex")
            }

            # If this is an RSA key, also parse the key itself
            if rr.algorithm in rsa_algorithms:
                # exp_len = struct.unpack('B', rr.key[0])[0]
                # obj['e'] = rr.key[1:1 + exp_len].encode("hex")
                # obj['N'] = rr.key[1 + exp_len:].encode("hex")

                key_ptr = rr.key
                (idx,) = struct.unpack('!B', key_ptr[0:1])
                key_ptr = key_ptr[1:]
                if idx == 0:
                    (idx,) = struct.unpack('!H', key_ptr[0:2])
                    key_ptr = key_ptr[2:]
                obj['e'] = key_ptr[0:idx].encode('hex')
                obj['N'] = key_ptr[idx:].encode('hex')
                # key_len = len(obj['N']) * 8

            db.dnskey.insert(obj)

    except dns.resolver.NoAnswer, e:
        logging.info('No DNSKEY entry for %s' % domain)
        raise dns.resolver.NXDOMAIN()
