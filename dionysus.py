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
    Dionysus - DNSSec scanner.
    """


@cli.command()
def scan():
    """
    Starts scanning.
    """

    core.dionysus.scan_domains()


@cli.command()
def run_server():
    """
    Runs the web-server.
    """

    core.dionysus.init()
    webapp.app.run_server()


@cli.group()
def manage():
    """
    Manage settings.
    """


@manage.command()
def init_db():
    """
    Initialises the database.
    """

    core.dal.create_database_indices()


@manage.command()
def reset_seeds_status():
    """
    Resets the status of all seeds to initial values (bad: False, last_scan: 0)
    """

    core.dal.reset_seeds_status(pymongo.MongoClient())


@cli.group()
def extract():
    """
    Extract DNS server info and SSL certifications from external files.
    """


@extract.command()
@click.argument('sonar_certificate_directory')
def sonar_certificates(sonar_certificate_directory):
    core.extractors.extract_sonar_certificates(sonar_certificate_directory)


@extract.command()
@click.argument('sonar_dns_file')
def sonar_dns_dnssec(sonar_dns_file):
    core.extractors.extract_sonar_dns_dnssec(sonar_dns_file)


@extract.command()
@click.argument('zone_file_path')
@click.argument('zone_file_origin')
def zone_file_ds(zone_file_path, zone_file_origin):
    core.extractors.extract_zone_file_ds(zone_file_path, zone_file_origin)


@cli.group()
def reports():
    """
    Create reports based on scan results.
    """


@reports.command()
def key_lengths():
    core.reports.key_lengths()


@reports.command()
@click.argument('moduli_file_path')
def create_moduli_file(moduli_file_path):
    core.reports.create_moduli_file(moduli_file_path)


@reports.command()
def duplicate_moduli():
    core.reports.duplicate_moduli()


@reports.command()
@click.argument('vuln_moduli_file_path')
@click.argument('gcd_file_path')
def vulnerable_moduli_info(vuln_moduli_file_path, gcd_file_path):
    core.reports.vulnerable_moduli_info(vuln_moduli_file_path, gcd_file_path)

if __name__ == '__main__':
    cli()
