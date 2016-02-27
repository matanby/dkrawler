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
    """
    Extract cryptographic data from Rapid7 Sonar SSL scan reports.
    """

    core.extractors.extract_sonar_certificates(sonar_certificate_directory)


@extract.command()
@click.argument('sonar_dns_file')
def sonar_dns_dnssec(sonar_dns_file):
    """
    Extract cryptographic data from Rapid7 Sonar DNS scan reports.
    """

    core.extractors.extract_sonar_dns_dnssec(sonar_dns_file)


@extract.command()
@click.argument('zone_file_path')
@click.argument('zone_file_origin')
def zone_file_ds(zone_file_path, zone_file_origin):
    """
    Extract DNS servers info from zone files.
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


if __name__ == '__main__':
    cli()
