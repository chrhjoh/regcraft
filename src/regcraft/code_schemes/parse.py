import polars as pl

from regcraft.registries.columns import DiagAdmCols, LsrCols


def format_icd10(
    icd_level: int,
    include_dot: bool = True,
    prefix: str = "",
):
    expr = pl.col(DiagAdmCols.diag).str.replace(r"\.", "").str.slice(1, icd_level)

    if include_dot and icd_level > 3:
        expr = pl.concat_str([expr.str.slice(0, 3), pl.lit("."), expr.str.slice(3)])

    return _add_prefix(expr, prefix)


def format_atc(atc_level: int, prefix: str = ""):
    """Length is level + 1 (e.g. level 4: A10AB)."""
    lengths = {1: 1, 2: 3, 3: 4, 4: 5, 5: 7}
    expr = pl.col(LsrCols.atc).str.slice(0, lengths.get(atc_level, None))
    return _add_prefix(expr, prefix)


def _format_code(
    length: int,
    col: str,
    start: int = 0,
):
    return pl.col(col).str.slice(start, length)


def _add_prefix(expr: pl.Expr, prefix: str):
    if not prefix:
        return expr
    return pl.concat_str([pl.lit(prefix), expr], separator=" ")
