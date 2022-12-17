import click

from cmdline.commands.validators import Password
from utils.project.func.password_hashing import hash_password


@click.group()
def helpers():
    """ Helper group command"""


@click.command("epass")
@click.argument("--password", type=Password())
def encode_password(password):
    hashed_password = hash_password(password)
    message = f"Password ({password}) converted to:\n{hashed_password}\n*You can save this hash to table."
    click.echo(message)


def get_helpers_group():
    helpers.add_command(encode_password)
    return helpers
