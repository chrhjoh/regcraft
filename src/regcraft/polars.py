import polars as pl


def convert_dates(
    lf: pl.LazyFrame,
    expr: str = "^.*date.*$",
    format: str | None = None,
    strict: bool = True,
):
    return lf.with_columns(pl.col(expr).str.to_date(format, strict=strict))


def coallese_dates(
    default: str,
    fallback: str,
) -> pl.Expr:
    return pl.col(default).fill_null(pl.col(fallback))
