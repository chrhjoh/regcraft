from datetime import date, timedelta

import polars as pl
import pytest
from polars.testing import assert_frame_equal, assert_schema_equal

from regcraft.mock.registries import (
    ATCS,
    ITEM_IDS,
    mock_cpr,
    mock_epikur,
    mock_laegemiddel,
    mock_lpr2adm,
    mock_lpr2diag,
    mock_lpr3contact,
    mock_lpr3diag,
)
from regcraft.registries.columns import (
    CprCols,
    EpikurCols,
    LaegemiddelCols,
    Lpr2AdmCols,
    Lpr2DiagCols,
    Lpr3ContactCols,
    Lpr3DiagCols,
)


def test_mock_cpr():
    df = mock_cpr(100).collect()
    birthdates = df[CprCols.birthdate].to_list()

    assert df.height == 100
    assert df.schema == CprCols.schema()
    assert df[CprCols.cpr_enc].n_unique() == 100
    assert all(date(1940, 1, 1) <= d <= date(2012, 1, 1) for d in birthdates)
    assert set(df[CprCols.status_code].unique().to_list()) <= {1, 30, 80, 90}
    assert set(df[CprCols.sex].unique().to_list()) <= {"M", "F"}

    alive = df.filter(pl.col(CprCols.status_code) == 1)
    deceased = df.filter(pl.col(CprCols.status_code) != 1)

    assert alive[CprCols.status_date].null_count() == alive.height
    assert deceased[CprCols.status_date].null_count() == 0


def test_mock_cpr_reproducible():
    assert_frame_equal(mock_cpr(100).collect(), mock_cpr(100).collect())


def test_mock_lpr2diag():
    df = mock_lpr2diag(100).collect()

    assert df.height == 100
    assert df.schema == Lpr2DiagCols.schema()
    assert set(df[Lpr2DiagCols.diag].unique().to_list()) <= {
        "DE10",
        "DC15",
        "Y213",
        "12345",
        "DA100",
    }
    assert set(df[Lpr2DiagCols.diag_type].unique().to_list()) <= {"A", "B", "C", "M"}
    assert df[Lpr2DiagCols.record_number].to_list() == list(range(100))


def test_mock_lpr2diag_reproducible():
    assert_frame_equal(mock_lpr2diag(100).collect(), mock_lpr2diag(100).collect())


def test_mock_lpr2adm():
    df = mock_lpr2adm(100, patients=5).collect()
    start_dates = df[Lpr2AdmCols.date_start].to_list()
    end_dates = df[Lpr2AdmCols.date_end].to_list()

    assert df.height == 100
    assert_schema_equal(df.schema, Lpr2AdmCols.schema())
    assert set(df[Lpr2AdmCols.cpr_enc].unique().to_list()) == {
        "Patient0",
        "Patient1",
        "Patient2",
        "Patient3",
        "Patient4",
    }
    assert set(df[Lpr2AdmCols.patient_type].unique().to_list()) <= {"In", "Out"}
    assert set(df[Lpr2AdmCols.contact_type].unique().to_list()) <= {
        "Physical",
        "Virtual",
    }
    assert set(df[Lpr2AdmCols.lpr_origin].unique().to_list()) == {"LPR2"}
    assert all(date(2000, 1, 1) <= d <= date(2024, 12, 31) for d in start_dates)
    assert all(
        date(2000, 1, 1) + timedelta(days=14)
        <= d
        <= date(2024, 12, 31) + timedelta(days=14)
        for d in end_dates
    )


def test_mock_lpr2adm_patient_assignment():
    df = mock_lpr2adm(5, patients=["A", "B"]).collect()

    assert df[Lpr2AdmCols.cpr_enc].to_list() == ["A", "B", "A", "B", "A"]


def test_mock_lpr2adm_empty_patients():
    with pytest.raises(ValueError, match="patients cannot be empty"):
        mock_lpr2adm(5, patients=[])


def test_mock_lpr3diag():
    df = mock_lpr3diag(100).collect()

    assert df.height == 100
    assert df.schema == Lpr3DiagCols.schema()
    assert set(df[Lpr3DiagCols.lpr_origin].unique().to_list()) <= {"LPR3", "Other"}


def test_mock_lpr3diag_reproducible():
    assert_frame_equal(mock_lpr3diag(100).collect(), mock_lpr3diag(100).collect())


def test_mock_lpr3contact():
    df = mock_lpr3contact(100, patients=5).collect()

    assert df.height == 100
    assert df.schema == Lpr3ContactCols.schema()
    assert set(df[Lpr3ContactCols.cpr_enc].unique().to_list()) == {
        "Patient0",
        "Patient1",
        "Patient2",
        "Patient3",
        "Patient4",
    }
    assert set(df[Lpr3ContactCols.patient_type].unique().to_list()) <= {"In", "Out"}
    assert set(df[Lpr3ContactCols.contact_type].unique().to_list()) <= {
        "Physical",
        "Virtual",
    }


def test_mock_lpr3contact_patient_assignment():
    df = mock_lpr3contact(5, patients=["A", "B"]).collect()

    assert df[Lpr3ContactCols.cpr_enc].to_list() == ["A", "B", "A", "B", "A"]


def test_mock_epikur():
    df = mock_epikur(100, patients=5).collect()
    dates = df[EpikurCols.date].to_list()

    assert df.height == 100
    assert set(df.columns) == {
        EpikurCols.cpr_enc,
        EpikurCols.item_id,
        EpikurCols.date,
    }
    assert set(df[EpikurCols.cpr_enc].unique().to_list()) == {
        "Patient0",
        "Patient1",
        "Patient2",
        "Patient3",
        "Patient4",
    }
    assert set(df[EpikurCols.item_id].unique().to_list()) <= set(ITEM_IDS)
    assert all(date(2000, 1, 1) <= d <= date(2024, 12, 31) for d in dates)


def test_mock_epikur_reproducible():
    assert_frame_equal(
        mock_epikur(100, patients=5).collect(),
        mock_epikur(100, patients=5).collect(),
    )


def test_mock_laegemiddel():
    df = mock_laegemiddel().collect()

    assert df.height == len(ATCS)
    assert_schema_equal(df.schema, LaegemiddelCols.schema())
    assert df[LaegemiddelCols.item_id].to_list() == ITEM_IDS
    assert df[LaegemiddelCols.atc].to_list() == ATCS
