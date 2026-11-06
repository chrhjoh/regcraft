import click
import polars as pl

from regkit.datasets.delfi import build_delfi_dataset


@click.group()
def dataset() -> None:
    """Build commonly used dataset formats for EHR machine learning models"""


@dataset.command("delfi", help="Build Delfi dataset")
@click.argument(
    "cpr_path",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
)
@click.argument(
    "output_dir",
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
    ),
)
@click.option(
    "--lsr-path",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option(
    "--diag-adm-path",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option("--atc-token-level", type=int, default=4, show_default=True)
@click.option("--icd10-token-level", type=int, default=3, show_default=True)
@click.option("--min-atc-tokens", type=int, default=5, show_default=True)
@click.option("--min-icd10-tokens", type=int, default=5, show_default=True)
@click.option("--val-percent", type=float, default=0.1, show_default=True)
@click.option("--test-percent", type=float, default=0.2, show_default=True)
def build_delfi(
    cpr_path: str,
    output_dir: str,
    lsr_path: str | None,
    diag_adm_path: str | None,
    atc_token_level: int,
    icd10_token_level: int,
    min_atc_tokens: int,
    min_icd10_tokens: int,
    val_percent: float,
    test_percent: float,
):
    cpr = pl.scan_parquet(cpr_path)
    if lsr_path is None and diag_adm_path is None:
        raise click.UsageError("Either lsr_path or diag_adms_path must be specified")
    lsr = pl.scan_parquet(lsr_path) if lsr_path else None
    diag_adms = pl.scan_parquet(diag_adm_path) if diag_adm_path else None
    dataset = build_delfi_dataset(
        cpr=cpr,
        lsr=lsr,
        diag_adms=diag_adms,
        atc_token_level=atc_token_level,
        icd10_token_level=icd10_token_level,
        min_atc_tokens=min_atc_tokens,
        min_icd10_tokens=min_icd10_tokens,
        val_percent=val_percent,
        test_percent=test_percent,
    )
    dataset.save(output_dir)
