import polars as pl
import pytest

from regcraft.code_schemes.parse import format_atc, format_icd10
from regcraft.registries.columns import DiagAdmCols, LsrCols


@pytest.mark.parametrize(
    ("level", "include_dot", "prefix", "expected"),
    [
        (3, True, "", "E11"),
        (4, True, "ICD10", "ICD10 E11.9"),
        (5, True, "ICD10", "ICD10 E11.90"),
        (5, False, "ICD10", "ICD10 E1190"),
        (4, False, "", "E119"),
    ],
)
def test_format_icd10(level, include_dot, prefix, expected):
    df = pl.DataFrame({DiagAdmCols.diag: ["DE11.90"]})

    result = df.select(format_icd10(level, include_dot, prefix)).to_series()

    assert result.item() == expected


@pytest.mark.parametrize(
    ("level", "prefix", "expected"),
    [
        (1, "", "A"),
        (2, "ATC", "ATC A10"),
        (4, "ATC", "ATC A10AB"),
        (5, "CUSTOM", "CUSTOM A10AB01"),
    ],
)
def test_format_atc(level, prefix, expected):
    df = pl.DataFrame({LsrCols.atc: ["A10AB01"]})

    result = df.select(format_atc(level, prefix)).to_series()

    assert result.item() == expected


@pytest.mark.parametrize(
    ("column", "formatter"),
    [
        (DiagAdmCols.diag, format_icd10(4, prefix="ICD10")),
        (LsrCols.atc, format_atc(4, prefix="ATC")),
    ],
)
def test_formatters_preserve_null(column, formatter):
    df = pl.DataFrame({column: [None]}, schema={column: pl.String})

    result = df.select(formatter).to_series()

    assert result.item() is None
