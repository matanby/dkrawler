import pymongo
import sys

sys.path.insert(0, "..")
import conf


def main():
    client = pymongo.MongoClient(conf.DATABASE_SERVER, conf.DATABASE_PORT)
    cursor = client.dionysus.dnskey.find()

    # Creating a key length histogram
    N_lengths = {}
    for entry in cursor:
        if 'N' not in entry:
            continue
        N_len = len(entry['N'])
        if N_len not in N_lengths:
            N_lengths[N_len] = 1
        else:
            N_lengths[N_len] += 1

    # Printing the actual key length histogram, sorted
    for length in sorted(N_lengths.keys()):
        print "%d bits : %d" % (length * 4, N_lengths[length])

if __name__ == "__main__":
    main()
