from collections.abc import Iterable
from enum import StrEnum, auto

import polars as pl

from regcraft.registries.fetchers.lsr import EpikurCols


class LsrCols(StrEnum):
    cpr_enc = auto()
    atc = auto()
    date = auto()


class DiagAdmCols(StrEnum):
    cpr_enc = auto()
    diag = auto()
    diag_type = auto()
    date_start = auto()
    date_end = auto()


def coallese_diag_adm_dates(
    default: str,
    fallback: str,
) -> pl.Expr:
    return pl.col(default).fill_null(pl.col(fallback))


def _join_select(
    lf1: pl.LazyFrame,
    lf2: pl.LazyFrame,
    on: str,
    select: Iterable[str],
):
    return lf1.join(lf2, on=on).select(select)


def join_lsr(epikur: pl.LazyFrame, laegemiddel: pl.LazyFrame, on=EpikurCols.item_id):
    return _join_select(epikur, laegemiddel, on, LsrCols)


def join_diag_adm(diagnoses: pl.LazyFrame, admin: pl.LazyFrame, on: str):
    return _join_select(diagnoses, admin, on, DiagAdmCols)
