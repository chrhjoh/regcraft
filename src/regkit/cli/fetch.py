import click

from regkit.io import write_parquet
from regkit.registries.fetchers.factory import (
    FetcherType,
    RegistryVersion,
    get_registryfetcher,
)


@click.command(help="Fetch and normalize Danish health registry")
@click.argument(
    "input_path",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
)
@click.argument(
    "output_path",
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
    ),
)
@click.option(
    "--version",
    "version",
    type=click.Choice(
        [version.value for version in RegistryVersion],
        case_sensitive=False,
    ),
    help="Registry version. (default: Inferred from path)",
)
@click.option(
    "--type",
    "fetcher_type",
    type=click.Choice(
        [version.value for version in FetcherType],
        case_sensitive=False,
    ),
    help="Registry type. (default: Inferred from path)",
)
def fetch(
    input_path: str,
    output_path: str,
    version: RegistryVersion | None,
    fetcher_type: FetcherType | None,
):
    version = version if version else RegistryVersion.from_path(input_path)
    fetcher_type = fetcher_type if fetcher_type else FetcherType.from_path(input_path)
    fetcher = get_registryfetcher(fetcher_type)(version=version)

    lf = fetcher.parse(input_path)

    write_parquet(lf, output_path)
