import click

import regcraft.cli.combine as c
import regcraft.cli.dataset as d
import regcraft.cli.fetch as f


@click.group()
def cli():
    """Registry toolkit."""


cli.add_command(f.fetch)
cli.add_command(d.dataset)
cli.add_command(c.combine)
