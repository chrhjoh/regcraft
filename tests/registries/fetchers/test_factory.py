from enum import StrEnum, auto
from pathlib import Path

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from regcraft.registries.fetchers import factory
from regcraft.registries.fetchers.factory import (
    FetcherType,
    RegistryFetcher,
    RegistryVersion,
    default_scanner,
)


class DummyCols(StrEnum):
    id = auto()
    name = auto()


class DummyFetcher(RegistryFetcher[DummyCols]):
    cols = DummyCols

    def column_norm_mapping(self) -> dict[str, str]:
        return {
            "Raw ID": "id",
            "Raw Name": "name",
        }


@pytest.fixture
def csv_path(tmp_path: Path) -> Path:
    path = tmp_path / "test.csv"
    path.write_text("Raw ID;Raw Name\n1;Alice\n2;Bob\n")
    return path


def test_registry_version_from_path():
    assert (
        RegistryVersion.from_path("/data/2026-04-07/file.csv") == RegistryVersion.V2026
    )


def test_registry_version_from_path_invalid():
    with pytest.raises(ValueError):
        RegistryVersion.from_path("/data/2020-01-01/file.csv")


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("epikur.asc", FetcherType.EPIKUR),
        ("laegemiddeloplysninger.asc", FetcherType.LAEGEMIDDEL),
        ("t_person.asc", FetcherType.CPR),
        ("t_diag.asc", FetcherType.LPR2DIAG),
        ("t_adm.asc", FetcherType.LPR2ADM),
        ("diagnoser.asc", FetcherType.LPR3DIAG),
        ("kontakter.asc", FetcherType.LPR3CONTACT),
    ],
)
def test_fetcher_type_from_path(filename: str, expected: FetcherType):
    assert FetcherType.from_path(filename) == expected


def test_fetcher_type_from_path_invalid():
    with pytest.raises(ValueError):
        FetcherType.from_path("unknown.csv")


def test_default_scanner(csv_path: Path):
    result = default_scanner(str(csv_path)).collect()

    expected = pl.DataFrame(
        {
            "Raw ID": [1, 2],
            "Raw Name": ["Alice", "Bob"],
        }
    )

    assert_frame_equal(result, expected)


def test_fetcher_parse(csv_path: Path):
    result = DummyFetcher(RegistryVersion.V2026).parse(str(csv_path))

    expected = pl.DataFrame(
        {
            "id": [1, 2],
            "name": ["Alice", "Bob"],
        }
    )

    assert_frame_equal(result.collect(), expected)


def test_fetcher_rejects_invalid_version():
    class InvalidFetcher(DummyFetcher):
        def validate_version(self) -> bool:
            return False

    with pytest.raises(RuntimeError):
        InvalidFetcher(RegistryVersion.V2026)


@pytest.fixture
def _isolated_fetchers(monkeypatch):
    monkeypatch.setattr(factory, "Fetchers", {})


def test_fetcher_registration(_isolated_fetchers):
    @factory.fetcher(factory.FetcherType.CPR)
    class DummyFetcher(RegistryFetcher[DummyCols]):
        cols = DummyCols

        def column_norm_mapping(self) -> dict[str, str]:
            return {}

    assert factory.Fetchers[factory.FetcherType.CPR] is DummyFetcher
    assert factory.get_registryfetcher(factory.FetcherType.CPR) is DummyFetcher


def test_fetcher_registration_duplicate(_isolated_fetchers):
    @factory.fetcher(factory.FetcherType.CPR)
    class FirstFetcher(RegistryFetcher[DummyCols]):
        cols = DummyCols

        def column_norm_mapping(self) -> dict[str, str]:
            return {}

    with pytest.raises(ValueError, match="Already registered"):
        factory.fetcher(factory.FetcherType.CPR)(FirstFetcher)
