from collections.abc import Iterable
from typing import Any

import polars as pl

from regcraft.registries.columns import (
    DiagAdmCols,
    Lpr2AdmCols,
    Lpr3ContactCols,
    LsrCols,
)
from regcraft.registries.fetchers.lsr import EpikurCols


def _join_select(
    lf1: pl.LazyFrame,
    lf2: pl.LazyFrame,
    on: str,
    select: Iterable[str],
) -> pl.LazyFrame:
    return lf1.join(lf2, on=on).select(select)


def _load_join(
    lf1: str | pl.LazyFrame, lf2: str | pl.LazyFrame, join_fn: Any, **kwargs
) -> pl.LazyFrame:
    lf1 = pl.scan_parquet(lf1) if isinstance(lf1, str) else lf1
    lf2 = pl.scan_parquet(lf2) if isinstance(lf2, str) else lf2
    return join_fn(lf1, lf2, **kwargs)


def join_lsr(
    epikur: pl.LazyFrame, laegemiddel: pl.LazyFrame, on: str = EpikurCols.item_id
) -> pl.LazyFrame:
    return _join_select(epikur, laegemiddel, on, LsrCols)


def join_diag_adm(
    diagnoses: pl.LazyFrame, admin: pl.LazyFrame, on: str
) -> pl.LazyFrame:
    return _join_select(diagnoses, admin, on, DiagAdmCols)


def create_lsr(
    epikur: pl.LazyFrame | str, laegemiddel: pl.LazyFrame | str
) -> pl.LazyFrame:
    return _load_join(epikur, laegemiddel, join_lsr)


def create_diag_adm(
    lpr2_diag: str | pl.LazyFrame | None,
    lpr2_adm: str | pl.LazyFrame | None,
    lpr3_diag: str | pl.LazyFrame | None,
    lpr3_adm: str | pl.LazyFrame | None,
) -> pl.LazyFrame:

    diag_adm_parts = []
    if lpr2_diag is not None and lpr2_adm is not None:
        diag_adm_parts.append(
            _load_join(
                lpr2_diag,
                lpr2_adm,
                join_diag_adm,
                on=Lpr2AdmCols.record_number,
            )
        )

    if lpr3_diag is not None and lpr3_adm is not None:
        diag_adm_parts.append(
            _load_join(
                lpr3_diag,
                lpr3_adm,
                join_diag_adm,
                on=Lpr3ContactCols.record_number,
            )
        )

    if len(diag_adm_parts) == 2:
        diag_adm = pl.concat(diag_adm_parts)
    elif len(diag_adm_parts) == 0:
        raise RuntimeError(
            "At least either both lpr2 or both lpr3 arguments must be supplied"
        )
    else:
        diag_adm = diag_adm_parts[0]
    return diag_adm
