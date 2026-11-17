from unittest.mock import Mock

import polars as pl

import regcraft.cli.fetch as cli
from regcraft.registries.fetchers.factory import FetcherType, RegistryVersion


def test_fetch_command(runner, tmp_path, monkeypatch):
    input_path = tmp_path / "input.csv"
    output_path = tmp_path / "output.parquet"
    input_path.touch()

    version = RegistryVersion.V2026
    fetcher_type = FetcherType.LPR2DIAG

    version_from_path = Mock(return_value=RegistryVersion.V2026)
    type_from_path = Mock(return_value=FetcherType.LPR2DIAG)

    lf = pl.LazyFrame({"value": [1, 2, 3]})
    fetcher = Mock()
    fetcher.parse.return_value = lf

    fetcher_factory = Mock(return_value=fetcher)
    get_fetcher = Mock(return_value=fetcher_factory)
    write_parquet_mock = Mock()

    monkeypatch.setattr(cli, "get_registryfetcher", get_fetcher)
    monkeypatch.setattr(cli, "write_parquet", write_parquet_mock)
    monkeypatch.setattr(RegistryVersion, "from_path", version_from_path)
    monkeypatch.setattr(FetcherType, "from_path", type_from_path)
    result = runner.invoke(
        cli.fetch,
        [str(input_path), str(output_path)],
    )

    assert result.exit_code == 0, result.output
    version_from_path.assert_called_once_with(str(input_path))
    type_from_path.assert_called_once_with(str(input_path))
    get_fetcher.assert_called_once_with(fetcher_type)
    fetcher_factory.assert_called_once_with(version=version)
    fetcher.parse.assert_called_once_with(str(input_path))
    write_parquet_mock.assert_called_once_with(lf, str(output_path))


def test_fetch_command_with_options(runner, tmp_path, monkeypatch):
    input_path = tmp_path / "input.csv"
    output_path = tmp_path / "output.parquet"
    input_path.touch()

    lf = pl.LazyFrame({"value": [1]})
    fetcher = Mock()
    fetcher.parse.return_value = lf

    fetcher_factory = Mock(return_value=fetcher)
    get_fetcher = Mock(return_value=fetcher_factory)
    write_parquet_mock = Mock()

    monkeypatch.setattr(cli, "get_registryfetcher", get_fetcher)
    monkeypatch.setattr(cli, "write_parquet", write_parquet_mock)

    result = runner.invoke(
        cli.fetch,
        [
            str(input_path),
            str(output_path),
            "--version",
            RegistryVersion.V2026.value,
            "--type",
            FetcherType.LPR2DIAG.value,
        ],
    )

    assert result.exit_code == 0, result.output
    get_fetcher.assert_called_once_with(FetcherType.LPR2DIAG)
    fetcher_factory.assert_called_once_with(version=RegistryVersion.V2026)
    fetcher.parse.assert_called_once_with(str(input_path))
    write_parquet_mock.assert_called_once_with(lf, str(output_path))


def test_fetch_command_rejects_missing_input(runner, tmp_path):
    output_path = tmp_path / "output.parquet"

    result = runner.invoke(
        cli.fetch,
        [str(tmp_path / "missing.csv"), str(output_path)],
    )

    assert result.exit_code == 2
    assert "does not exist" in result.output
