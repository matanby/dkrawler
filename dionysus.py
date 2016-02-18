import click
import core.dionysus
import core.reports
import core.dal


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


@cli.group()
def manage():
    """
    Manage settings.
    """


@manage.command()
def init_db():
    """
    Initialises the database.
    :return:
    """
    core.dal.create_database_indices()


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
