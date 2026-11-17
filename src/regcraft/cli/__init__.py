import click

import regcraft.cli.dataset as d
import regcraft.cli.fetch as f
import regcraft.cli.join as j
import regcraft.cli.mock as m


@click.group()
def cli():
    """Registry toolkit."""


cli.add_command(f.fetch)
cli.add_command(d.dataset)
cli.add_command(j.join)
cli.add_command(m.mock_cli, name="mock")
