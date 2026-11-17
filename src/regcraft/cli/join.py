import click

from regcraft.io import write_parquet
from regcraft.registries.joins import (
    create_diag_adm,
    create_lsr,
)


@click.group()
def join() -> None:
    """Create long versions of LSR and Diag Adms"""


_input_file = click.Path(
    exists=True,
    file_okay=True,
    dir_okay=False,
)

_output_file = click.Path(
    exists=False,
    file_okay=True,
    dir_okay=False,
)


@join.command("lsr", help="Create combined version of Epikur and Laegemiddelinfo")
@click.argument("epikur_path", type=_input_file)
@click.argument("laegemiddel_path", type=_input_file)
@click.argument("output_path", type=_output_file)
@click.option(
    "--collect",
    is_flag=True,
    default=False,
    help="Collect result before writing output",
)
def lsr(epikur_path: str, laegemiddel_path: str, output_path: str, collect: bool):
    lsr = create_lsr(epikur_path, laegemiddel_path)

    write_parquet(lsr, output_path, collect=collect)


@join.command(
    "diag-adm", help="Create combined version of Diag and Adms for LPR2 and LPR3"
)
@click.argument("output_path", type=_output_file)
@click.option("--lpr2-diag-path", type=_input_file)
@click.option("--lpr2-adm-path", type=_input_file)
@click.option("--lpr3-diag-path", type=_input_file)
@click.option("--lpr3-adm-path", type=_input_file)
def diag_adm(
    output_path: str,
    lpr2_diag_path: str | None = None,
    lpr2_adm_path: str | None = None,
    lpr3_adm_path: str | None = None,
    lpr3_diag_path: str | None = None,
):
    def _raise_specify_both_usage_error(arg1: str, arg2: str):
        raise click.UsageError(f"{arg1} and {arg2} must be specified together.")

    if (lpr2_diag_path is None) != (lpr2_adm_path is None):
        _raise_specify_both_usage_error("--lpr2-diag-path", "--lpr2-adm-path")
    elif (lpr3_diag_path is None) != (lpr3_adm_path is None):
        _raise_specify_both_usage_error("--lpr3-diag-path", "--lpr3-adm-path")
    elif lpr2_diag_path is None and lpr3_diag_path is None:
        raise click.UsageError("Either lpr3 and or lpr2 paths must be specified.")

    diag_adm = create_diag_adm(
        lpr2_diag=lpr2_diag_path,
        lpr2_adm=lpr2_adm_path,
        lpr3_diag=lpr3_diag_path,
        lpr3_adm=lpr3_adm_path,
    )
    write_parquet(diag_adm, output_path)
