import sys
from conf import *
from pymongo import MongoClient

def main():

	client = MongoClient(DATABASE_SERVER, DATABASE_PORT)
	cursor = client.dionysus.dnskey.find({'N':{'$exists':True}})
	N_map = {}
	for entry in cursor:
		N = entry['N']
		if not N in N_map:
			N_map[N] = 1
		else:
			N_map[N] += 1

	for N in N_map:
		if N_map[N] > 1:
			print "---------------------------------------------"
			print "Duplicate modulus!"
			print N
			print "Found in:"
			cursor = client.dionysus.dnskey.find({'N':N})
			for entry in cursor:
				print entry['domain']

if __name__ == "__main__":
	main()
