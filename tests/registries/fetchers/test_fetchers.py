from pathlib import Path

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from regcraft.registries.columns import (
    CprCols,
    EpikurCols,
    LaegemiddelCols,
    Lpr2AdmCols,
    Lpr2DiagCols,
    Lpr3ContactCols,
    Lpr3DiagCols,
)
from regcraft.registries.fetchers.cpr import CprRegistryFetcher
from regcraft.registries.fetchers.factory import RegistryVersion
from regcraft.registries.fetchers.lpr import (
    Lpr2AdmRegistryFetcher,
    Lpr2DiagRegistryFetcher,
    Lpr3ContactRegistryFetcher,
    Lpr3DiagRegistryFetcher,
)
from regcraft.registries.fetchers.lsr import (
    EpikurRegistryFetcher,
    LaegemiddelRegistryFetcher,
)


def test_lpr2_adm_post_rename():
    fetcher = Lpr2AdmRegistryFetcher(RegistryVersion.V2026)

    lf = pl.DataFrame({"cpr_enc": ["A", "B"]}).lazy()

    result = fetcher._post_rename(lf).collect()

    expected = pl.DataFrame(
        {
            "cpr_enc": ["A", "B"],
            "lpr_origin": ["LPR2", "LPR2"],
            "contact_type": pl.Series([None, None], dtype=pl.String),
        }
    )

    assert_frame_equal(result, expected)


def test_lpr3_diag_post_rename():
    fetcher = Lpr3DiagRegistryFetcher(RegistryVersion.V2026)

    lf = pl.DataFrame(
        {
            "diag": ["A", "B", "C"],
            "senere_afkraeftet": ["nej", "ja", "NEJ"],
        }
    ).lazy()

    result = fetcher._post_rename(lf).collect()

    assert result["diag"].to_list() == ["A", "C"]
    assert result["diag_additional"].to_list() == [None, None]


def test_lpr3_contact_post_rename():
    fetcher = Lpr3ContactRegistryFetcher(RegistryVersion.V2026)

    lf = pl.DataFrame({"cpr_enc": ["A", "B"]}).lazy()

    result = fetcher._post_rename(lf).collect()

    assert result["cpr_enc"].to_list() == ["A", "B"]
    assert result["patient_type"].to_list() == [None, None]


def test_laegemiddel_scan_2026(tmp_path: Path):
    path = tmp_path / "laegemiddel.uniqDelim"
    path.write_text(
        "vnr¤atc¤other\n123¤A01¤unused\n456¤B02¤unused\n",
        encoding="utf-8-sig",
    )

    fetcher = LaegemiddelRegistryFetcher(RegistryVersion.V2026)

    result = fetcher._scan_file(str(path)).collect()

    expected = pl.DataFrame(
        {
            "vnr": [123, 456],  # Is converted only through parse
            "atc": ["A01", "B02"],
        }
    )

    assert_frame_equal(result, expected)


def test_laegemiddel_scan_2026_rejects_asc(tmp_path: Path):
    path = tmp_path / "laegemiddel.asc"
    path.touch()

    fetcher = LaegemiddelRegistryFetcher(RegistryVersion.V2026)

    with pytest.raises(ValueError, match="separator is not unique"):
        fetcher._scan_file(str(path))


@pytest.mark.parametrize(
    ("fetcher_cls", "expected_cols", "expected_mapping"),
    [
        (
            CprRegistryFetcher,
            CprCols,
            {
                "cpr_enc": "cpr_enc",
                "D_FODDATO": "birthdate",
                "C_STATUS": "status_code",
                "D_STATUS_HEN_START": "status_date",
                "C_KON": "sex",
            },
        ),
        (
            Lpr2DiagRegistryFetcher,
            Lpr2DiagCols,
            {
                "V_RECNUM": "record_number",
                "C_DIAGTYPE": "diag_type",
                "C_DIAG": "diag",
                "C_TILDIAG": "diag_additional",
            },
        ),
        (
            Lpr2AdmRegistryFetcher,
            Lpr2AdmCols,
            {
                "cpr_enc": "cpr_enc",
                "D_INDDTO": "date_start",
                "D_UDDTO": "date_end",
                "K_RECNUM": "record_number",
                "C_PATTYPE": "patient_type",
            },
        ),
        (
            Lpr3DiagRegistryFetcher,
            Lpr3DiagCols,
            {
                "dw_ek_kontakt": "record_number",
                "diagnosetype": "diag_type",
                "diagnosekode": "diag",
                "lprindberetningssystem": "lpr_origin",
            },
        ),
        (
            Lpr3ContactRegistryFetcher,
            Lpr3ContactCols,
            {
                "cpr_enc": "cpr_enc",
                "dato_start": "date_start",
                "dato_slut": "date_end",
                "dw_ek_kontakt": "record_number",
                "kontakttype": "contact_type",
            },
        ),
        (
            LaegemiddelRegistryFetcher,
            LaegemiddelCols,
            {
                "atc": "atc",
                "vnr": "item_id",
            },
        ),
        (
            EpikurRegistryFetcher,
            EpikurCols,
            {
                "cpr_enc": "cpr_enc",
                "eksd": "date",
                "vnr": "item_id",
            },
        ),
    ],
)
def test_fetcher_configuration(fetcher_cls, expected_cols, expected_mapping):
    fetcher = fetcher_cls(RegistryVersion.V2026)

    assert fetcher.cols is expected_cols
    assert fetcher.column_norm_mapping() == expected_mapping
