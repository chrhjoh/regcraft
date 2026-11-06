from typing import Any

import click
import polars as pl

from regkit.io import write_parquet
from regkit.registries.columns import Lpr2AdmCols
from regkit.registries.combine import join_diag_adm, join_lsr


@click.group()
def combine() -> None:
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


@combine.command("lsr", help="Create combined version of Epikur and Laegemiddelinfo")
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
    lsr = _load_join(epikur_path, laegemiddel_path, join_lsr)

    write_parquet(lsr, output_path, collect=collect)


@combine.command(
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

    diag_adm_parts = []
    if lpr2_diag_path is not None and lpr2_adm_path is not None:
        diag_adm_parts.append(
            _load_join(
                lpr2_diag_path,
                lpr2_adm_path,
                join_diag_adm,
                on=Lpr2AdmCols.record_number,
            )
        )

    if lpr3_diag_path is not None and lpr3_adm_path is not None:
        diag_adm_parts.append(
            _load_join(
                lpr3_diag_path,
                lpr3_adm_path,
                join_diag_adm,
                on=Lpr2AdmCols.record_number,
            )
        )

    if len(diag_adm_parts) == 2:
        diag_adm = pl.concat(diag_adm_parts)
    else:
        diag_adm = diag_adm_parts[0]

    write_parquet(diag_adm, output_path)


def _load_join(lf1_path: str, lf2_path: str, join_fn: Any, **kwargs) -> pl.LazyFrame:
    lf1 = pl.scan_parquet(lf1_path)
    lf2 = pl.scan_parquet(lf2_path)
    return join_fn(lf1, lf2, **kwargs)
