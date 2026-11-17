import polars as pl
import pytest

from regcraft.registries.columns import (
    BaseCols,
    CprCols,
    DiagAdmCols,
    EpikurCols,
    LaegemiddelCols,
    Lpr2AdmCols,
    Lpr2DiagCols,
    Lpr3ContactCols,
    Lpr3DiagCols,
    LsrCols,
)


def test_base_cols_schema():
    with pytest.raises(NotImplementedError):
        BaseCols.schema()


@pytest.mark.parametrize(
    ("cols", "expected"),
    [
        (
            CprCols,
            {
                "cpr_enc": pl.Utf8,
                "birthdate": pl.Date,
                "status_code": pl.Int16,
                "status_date": pl.Date,
                "sex": pl.Utf8,
            },
        ),
        (
            Lpr2DiagCols,
            {
                "record_number": pl.Int32,
                "diag_type": pl.Utf8,
                "diag": pl.Utf8,
                "diag_additional": pl.Utf8,
            },
        ),
        (
            Lpr2AdmCols,
            {
                "cpr_enc": pl.Utf8,
                "date_start": pl.Date,
                "date_end": pl.Date,
                "record_number": pl.Int32,
                "patient_type": pl.Utf8,
                "lpr_origin": pl.Utf8,
                "contact_type": pl.Utf8,
            },
        ),
        (
            Lpr3DiagCols,
            {
                "record_number": pl.Int32,
                "diag_type": pl.Utf8,
                "diag": pl.Utf8,
                "lpr_origin": pl.Utf8,
                "diag_additional": pl.Utf8,
            },
        ),
        (
            Lpr3ContactCols,
            {
                "cpr_enc": pl.Utf8,
                "date_start": pl.Date,
                "date_end": pl.Date,
                "record_number": pl.Int32,
                "patient_type": pl.Utf8,
                "contact_type": pl.Utf8,
            },
        ),
        (
            LaegemiddelCols,
            {
                "atc": pl.Utf8,
                "item_id": pl.Int32,
            },
        ),
        (
            EpikurCols,
            {
                "cpr_enc": pl.Utf8,
                "date": pl.Date,
                "item_id": pl.Int32,
            },
        ),
        (
            LsrCols,
            {
                "cpr_enc": pl.Utf8,
                "atc": pl.Utf8,
                "date": pl.Date,
            },
        ),
        (
            DiagAdmCols,
            {
                "cpr_enc": pl.Utf8,
                "diag": pl.Utf8,
                "diag_type": pl.Utf8,
                "date_start": pl.Date,
                "date_end": pl.Date,
            },
        ),
    ],
)
def test_registry_schema(cols, expected):
    assert cols.schema() == pl.Schema(expected)
