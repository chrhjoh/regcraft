from enum import StrEnum, auto

import polars as pl

from regcraft.registries.columns import CprCols
from regcraft.registries.combine import DiagAdmCols, LsrCols


class Split(StrEnum):
    TRAIN = auto()
    VAL = auto()
    TEST = auto()


class LongEhrCols(StrEnum):
    token = auto()
    date = auto()
    age_days = auto()
    patient_id = auto()


def filter_by_occurrence(lf: pl.LazyFrame, min_count: int, col: str = "token"):
    allowed_tokens = (
        lf.group_by(col)
        .len("n")
        .filter(pl.col.n.ge(min_count))
        .collect()
        .get_column(col)
    )
    return lf.filter(pl.col(col).is_in(allowed_tokens))


def split_dataset(
    lf: pl.LazyFrame, val: float, test: float, seed: int | None = None
) -> dict[Split, pl.LazyFrame]:
    if val + test >= 1:
        raise ValueError()
    lf = (
        lf.with_columns(
            pl.int_range(pl.len()).shuffle(seed=seed).truediv(pl.len()).alias("_prob")
        )
        .with_columns(
            pl.when(pl.col("_prob") < val)
            .then(pl.lit(Split.VAL.value))
            .when(pl.col("_prob") < val + test)
            .then(pl.lit(Split.TEST.value))
            .otherwise(pl.lit(Split.TRAIN.value))
            .alias("split")
        )
        .drop("_prob")
    )
    splits = {}
    if val > 0:
        splits[Split.VAL] = lf.filter(pl.col.split.eq(Split.VAL.value)).drop("split")
    if test > 0:
        splits[Split.TEST] = lf.filter(pl.col.split.eq(Split.TEST.value)).drop("split")
    if val + test != 1:
        splits[Split.TRAIN] = lf.filter(pl.col.split.eq(Split.TRAIN.value)).drop(
            "split"
        )

    return splits


def common_cpr_filters(cpr: pl.LazyFrame, included_status_codes: list[int] | None):
    """Filters null birthdates and common status"""
    included_status_codes = included_status_codes or [1, 80, 90]

    return cpr.filter(
        pl.col(CprCols.status_code).is_in(included_status_codes)
        & pl.col(CprCols.birthdate).is_not_null()
    )


def filter_study_age(
    cpr: pl.LazyFrame,
    year: int,
    day: int = 1,
    month: int = 1,
    min_age: int = 0,
    max_age: int = 120,
):
    """Only include if age is between min and max at reference date"""
    return cpr.filter(
        pl.date(year=year, month=month, day=day)
        .sub(pl.col(CprCols.birthdate))
        .dt.total_days()
        .is_between(min_age * 365.25, max_age * 365.25)
    )


def common_lsr_filter(lsr: pl.LazyFrame):
    """Only include atc codes of length 7"""
    return lsr.filter(pl.col(LsrCols.atc).str.len_chars().eq(7))


def common_diag_adm_filter(
    diag_adm: pl.LazyFrame,
    included_diag_types: list[str] | None = None,
    excluded_chapters: list[str] | None = None,
    icd10_only: bool = True,
):
    """Subset by Chapters and Diagnosis Types"""
    diag = DiagAdmCols.diag
    if excluded_chapters is None:
        excluded_chapters = ["R", "S", "T"]

    if included_diag_types is None:
        included_diag_types = ["A", "B"]
    diag_adm = diag_adm.filter(
        pl.col(DiagAdmCols.diag_type).str.to_uppercase().is_in(included_diag_types)
        & pl.col(diag)
        .str.slice(0, 2)
        .is_in(["D" + c for c in excluded_chapters])
        .not_()
    )
    if icd10_only:
        diag_adm = diag_adm.filter(pl.col(diag).str.slice(0, 1).eq("D"))
    return diag_adm
