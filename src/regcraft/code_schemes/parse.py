import polars as pl

from regcraft.registries.combine import DiagAdmCols, LsrCols


def format_icd10(icd_level: int):
    return _format_code(length=icd_level, col=DiagAdmCols.diag, prefix="ICD10", start=1)


def format_atc(atc_level: int):
    """Length is level + 1 (e.g. level 4: A10AB)"""
    return _format_code(length=atc_level + 1, col=LsrCols.atc, prefix="ATC")


def _format_code(
    length: int,
    col: str,
    prefix: str | None = None,
    start: int = 0,
    separator: str = " ",
):
    expr = pl.col(col).str.slice(start, length)
    if prefix is not None:
        expr = pl.concat_str([prefix, expr], separator=separator)
    return expr
