import click
from werkzeug.security import generate_password_hash


@click.command()
@click.option('--password', type=str, default='password')
def cli(password):
    pw_hash = generate_password_hash(password)
    click.echo(click.style(f'password: { password }', fg='blue'))
    click.echo(click.style(pw_hash, fg='green'))

'''make SECRET_KEY
>>> import secrets
>>> secrets.token_hex()
'214112c18c87171faab453379569a4b99ae80559a9e4202707682fb0cfe5ab39'
'''

if __name__ == '__main__':
    cli()
