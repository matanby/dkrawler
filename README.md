# **DKrawler: DNSSEC Crawler and Vulnerability Analyzer**

The goal of this project is to assess the security posture of the current DNSSEC infrastructure by analysing the security status of deployed DNSSEC cryptographic keys.

In order to assess the strength of the deployed public keys, we needed to develop an infrastructure which can be used to rapidly collect key material from the DNSSEC infrastructure. This resulted in the development of a fast, configurable, non-blocking crawler we have dubbed “DKrawler (DNSSEC Keys Crawler)”.

The infrastructure is written in Python and allows the definition of different pluggable modules called “scanners”, which operate in a non-blocking manner using “greenlets” in order to send requests and analyse their responses. 
These responses are fed into a MongoDB document database in order to facilitate fast insertion and retrieval.

In order to speed up the collection of DNS keys, we have collected the names of zones which are “DNSSEC enabled”, to be used as “crawling seeds”, from various different sources:
The “Sonar DNS” project - a project which performs daily scans of various internet protocols, among which, a full scan of all DNS resource records in all the known zones.
TLD zone files - We have acquired the current TLD zone files for the zones “com”, “org”, “info” and “net”, and have added all the DNSSEC enabled zones mentioned in the zone files.

The system periodically scans the DNS hierarchy using the given scanning seeds in order to collect key material, and inserts it into the database. 
When resource records for keys expire, they are automatically re-scanned and the new keys are inserted into the database (thus making sure that when a key rotation occurs, the updated key will be saved).
Moreover, when a scan is completed, it’s results are automatically analysed by executing different reports, and storing their results in the database as well.

Finally, in order to enable easy interrogation of the scanning process, we have developed a web-application (based on the “Flask” infrastructure) which allows the user to quickly gage the state of the system without having to delve into the command-line interface.

We have made the source code publicly available on GitHub: https://github.com/matanby/dkrawler.
