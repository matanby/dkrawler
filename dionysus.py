#! /usr/bin/env python

import click
import pymongo

import core.dionysus
import core.extractors
import core.reports
import core.dal
import webapp.app


@click.group()
def cli():
    """
    Dionysus - DNSSEC scanner.
    """


@cli.command()
def scan():
    """
    Start a new scan.
    """

    core.dionysus.scan_domains()


@cli.command()
def run_server():
    """
    Run the web-server and scans scheduler.
    """

    core.dionysus.init()
    webapp.app.run_server()


@cli.group()
def manage():
    """
    Manage settings.
    """


@manage.command()
def create_db_indices():
    """
    Create DB indices.
    """

    core.dal.create_database_indices()


@manage.command()
def reset_seeds_status():
    """
    Reset the status of all seeds to initial values (bad: False, last_scan: 0)
    """

    core.dal.reset_seeds_status(pymongo.MongoClient())


@cli.group()
def extract():
    """
    Extract DNS server info and SSL certifications from external files.
    """


@extract.command()
@click.argument('sonar_certificate_directory')
def sonar_ssl_certificates(sonar_certificates_directory):
    """
    Extract cryptographic data from Rapid7 Sonar SSL scan reports.
    :param sonar_certificates_directory: The path containing Rapid7 certificates.
    """

    core.extractors.extract_sonar_ssl_certificates(sonar_certificates_directory)


@extract.command()
@click.argument('sonar_dns_file')
def sonar_dns(sonar_dns_file):
    """
    Extract cryptographic data from Rapid7 Sonar DNS scan reports.
    :param sonar_dns_file: The path of Rapid7's DNS scan report.
    """

    core.extractors.extract_sonar_dns(sonar_dns_file)


@extract.command()
@click.argument('zone_file_path')
@click.argument('zone_file_origin')
def zone_file_ds(zone_file_path, zone_file_origin):
    """
    Extract DNS servers info from zone files.
    :param zone_file_path: The zone file's path.
    :param zone_file_origin: The zone file's origin.
    """

    core.extractors.extract_zone_file_ds(zone_file_path, zone_file_origin)


@cli.group()
def reports():
    """
    Create reports based on scan results.
    """


@reports.command()
def key_lengths():
    """
    Generate DNS key lengths report.
    """

    core.reports.key_lengths()


@reports.command()
def duplicate_moduli():
    """
    Generate duplicate DNS key moduli report.
    """

    core.reports.duplicate_moduli()


@reports.command()
def factorable_moduli():
    """
    Generate factorable DNS key moduli report.
    """

    core.reports.factorable_moduli()


@cli.group()
def export():
    """
    Export reports to CSV files.
    """


@export.command()
def key_lengths():
    """
    Export each of the key lengths reports to a CSV file.
    """

    core.reports.export_key_lengths_reports()


@export.command()
def duplicate_moduli():
    """
    Export each of the duplicate moduli reports to a CSV file.
    """

    core.reports.export_duplicate_moduli_reports()


@export.command()
def factorable_moduli():
    """
    Export each of the factorable moduli reports to a CSV file.
    """

    core.reports.export_factorable_moduli_reports()

if __name__ == '__main__':
    cli()
