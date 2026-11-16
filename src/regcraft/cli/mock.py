import click

import regcraft.mock.registries as mock
from regcraft.io import write_parquet
from regcraft.mock.datasets import mock_delfi

OUTPUT_PATH = click.Path(
    file_okay=True,
    dir_okay=False,
    writable=True,
)

OUTPUT_DIR = click.Path(
    file_okay=False,
    dir_okay=True,
    writable=True,
)


@click.group()
def mock_cli():
    """Generate synthetic Danish registry data."""


@mock_cli.command()
@click.argument("output_path", type=OUTPUT_PATH)
@click.option("--nrows", default=100, type=click.IntRange(min=1))
@click.option("--seed", default=42, show_default=True, type=int)
def cpr(output_path: str, nrows: int, seed: int):
    """Generate synthetic CPR data."""
    write_parquet(mock.mock_cpr(nrows, seed), output_path)


@mock_cli.command()
@click.argument("output_path", type=OUTPUT_PATH)
@click.option("--nrows", default=10000, type=click.IntRange(min=1))
@click.option("--seed", default=42, show_default=True, type=int)
def lpr2diag(output_path: str, nrows: int, seed: int):
    """Generate synthetic LPR2 diagnosis data."""
    write_parquet(mock.mock_lpr2diag(nrows, seed), output_path)


@mock_cli.command()
@click.argument("output_path", type=OUTPUT_PATH)
@click.option("--nrows", default=10000, type=click.IntRange(min=1))
@click.option("--patients", default=100, type=click.IntRange(min=1))
@click.option("--seed", default=42, show_default=True, type=int)
def lpr2adm(output_path: str, nrows: int, patients: int, seed: int):
    """Generate synthetic LPR2 admission data."""
    write_parquet(mock.mock_lpr2adm(nrows, patients, seed), output_path)


@mock_cli.command()
@click.argument("output_path", type=OUTPUT_PATH)
@click.option("--nrows", default=10000, type=click.IntRange(min=1))
@click.option("--seed", default=42, show_default=True, type=int)
def lpr3diag(output_path: str, nrows: int, seed: int):
    """Generate synthetic LPR3 diagnosis data."""
    write_parquet(mock.mock_lpr3diag(nrows, seed), output_path)


@mock_cli.command()
@click.argument("output_path", type=OUTPUT_PATH)
@click.option("--nrows", default=10000, type=click.IntRange(min=1))
@click.option("--patients", default=100, type=click.IntRange(min=1))
@click.option("--seed", default=42, show_default=True, type=int)
def lpr3contact(output_path: str, nrows: int, patients: int, seed: int):
    """Generate synthetic LPR3 contact data."""
    write_parquet(mock.mock_lpr3contact(nrows, patients, seed), output_path)


@mock_cli.command()
@click.argument("output_path", type=OUTPUT_PATH)
@click.option("--nrows", default=10000, type=click.IntRange(min=1))
@click.option("--patients", default=100, type=click.IntRange(min=1))
@click.option("--seed", default=42, show_default=True, type=int)
def epikur(output_path: str, nrows: int, patients: int, seed: int):
    """Generate synthetic EPIKUR data."""
    write_parquet(mock.mock_epikur(nrows, patients, seed), output_path)


@mock_cli.command()
@click.argument("output_path", type=OUTPUT_PATH)
def laegemiddel(output_path: str):
    """Generate synthetic medication lookup data."""
    write_parquet(mock.mock_laegemiddel(), output_path)


@mock_cli.command()
@click.argument("output_dir", type=OUTPUT_DIR)
@click.option("--patients", default=100, type=click.IntRange(min=1))
@click.option("--events-per-modality", type=click.IntRange(min=1), default=10000)
@click.option("--seed", default=42, show_default=True, type=int)
def delfi(output_dir: str, patients: int, events_per_modality: int, seed: int):
    """Generate synthetic delfi dataset."""

    dataset = mock_delfi(patients, events_per_modality, seed)
    dataset.save(output_dir)
