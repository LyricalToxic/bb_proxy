import click

from cmdline.commands import ghelpers, gsql


@click.group()
def cli():
    """
        Guide for how to fill db tables. For this purpose use sql command:

            python bbcli.py sql --help

        There are a few additional commands that generate sql queries.

        1. First of all use `insert_comrade` to insert comrade.

            Specify option "--help" for more details, then specify required options with your data.
            Execute generated string in db console.
            Copy id of inserted row.

        2. Use `insert_proxy` to insert proxy.

            Specify option "--help" for more details, then specify required options with your data.
            Execute generated string in db console.
            Copy id of inserted row.

        3. Use `insert_proxy_comrade` to insert proxy comrade with your limit.

            Specify option "--help" for more details, then specify required options with your data.
            Pass ids as option that was copy previously.
            Execute generated string in db console.
            Copy id of inserted row.

        4. Use `select_statistic` to see aggregated statistics.

            Specify option "--help" for more details, then specify required options with your data.
            Pass id from the third point as option.
    """


@click.command("echo")
@click.argument("message", nargs=-1)
def echo(message):
    print(message)


def _init():
    cli.add_command(echo)
    cli.add_command(ghelpers)
    cli.add_command(gsql)
    cli()


if __name__ == '__main__':
    _init()
