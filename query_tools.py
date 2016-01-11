import dns.resolver

def query_both(resolver, domain, qtype, qclass='IN'):

	#Trying once with EDNS0
	resolver.query(
