import click

import regcraft.cli.combine as c
import regcraft.cli.dataset as d
import regcraft.cli.fetch as f
import regcraft.cli.mock as m


@click.group()
def cli():
    """Registry toolkit."""


cli.add_command(f.fetch)
cli.add_command(d.dataset)
cli.add_command(c.combine)
cli.add_command(m.mock_cli, name="mock")
