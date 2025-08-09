import click
from werkzeug.security import generate_password_hash


@click.command()
@click.option('--password', type=str, default='mockturtle')
def cli(password):
    pw_hash = generate_password_hash(password)
    click.echo(click.style(f'password: { password }', fg='blue'))
    click.echo(click.style(pw_hash, fg='green'))

if __name__ == '__main__':
    cli()
