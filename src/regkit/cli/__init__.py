import click

import regkit.cli.combine as c
import regkit.cli.dataset as d
import regkit.cli.fetch as f


@click.group()
def cli():
    """Registry toolkit."""


cli.add_command(f.fetch)
cli.add_command(d.dataset)
cli.add_command(c.combine)
