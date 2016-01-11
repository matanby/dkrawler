import sys, os
from pymongo import MongoClient
from conf import *

def main():
	if len(sys.argv) != 2:
		print "USAGE: %s <MODULI_FILE>" % sys.argv[0]
		return
	moduli_file_path = sys.argv[1]
	client = MongoClient(DATABASE_SERVER, DATABASE_PORT)
	moduli_file = open(moduli_file_path, 'w')
	cursor = client.dionysus.dnskey.find({'N':{'$exists':True}})
	for entry in cursor:
		moduli_file.write(entry['N'])
		moduli_file.write('\n')
	moduli_file.close()

	#After the file is created, filter it through sort-uniq
	os.system('cat %s | sort | uniq > %s_' % (moduli_file_path, moduli_file_path))
	os.system('rm %s' % moduli_file_path)
	os.system('mv %s_ %s' % (moduli_file_path, moduli_file_path))

if __name__ == "__main__":
	main()
