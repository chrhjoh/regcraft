from unittest.mock import Mock

import polars as pl
import pytest

import regcraft.cli.mock as cli


@pytest.mark.parametrize(
    ("command", "generator", "options", "expected_args"),
    [
        ("cpr", "mock_cpr", ["--nrows", "20", "--seed", "7"], (20, 7)),
        ("lpr2diag", "mock_lpr2diag", ["--nrows", "20", "--seed", "7"], (20, 7)),
        (
            "lpr2adm",
            "mock_lpr2adm",
            ["--nrows", "20", "--patients", "5", "--seed", "7"],
            (20, 5, 7),
        ),
        ("lpr3diag", "mock_lpr3diag", ["--nrows", "20", "--seed", "7"], (20, 7)),
        (
            "lpr3contact",
            "mock_lpr3contact",
            ["--nrows", "20", "--patients", "5", "--seed", "7"],
            (20, 5, 7),
        ),
        (
            "epikur",
            "mock_epikur",
            ["--nrows", "20", "--patients", "5", "--seed", "7"],
            (20, 5, 7),
        ),
    ],
)
def test_registry_mock_commands(
    runner, tmp_path, monkeypatch, command, generator, options, expected_args
):
    output = tmp_path / "output.parquet"
    lf = pl.LazyFrame({"value": [1]})

    generate = Mock(return_value=lf)
    write = Mock()

    monkeypatch.setattr(cli.mock, generator, generate)
    monkeypatch.setattr(cli, "write_parquet", write)

    result = runner.invoke(cli.mock_cli, [command, str(output), *options])

    assert result.exit_code == 0, result.output
    generate.assert_called_once_with(*expected_args)
    write.assert_called_once_with(lf, str(output))


def test_laegemiddel(runner, tmp_path, monkeypatch):
    output = tmp_path / "output.parquet"
    lf = pl.LazyFrame({"value": [1]})

    generate = Mock(return_value=lf)
    write = Mock()

    monkeypatch.setattr(cli.mock, "mock_laegemiddel", generate)
    monkeypatch.setattr(cli, "write_parquet", write)

    result = runner.invoke(cli.mock_cli, ["laegemiddel", str(output)])

    assert result.exit_code == 0, result.output
    generate.assert_called_once_with()
    write.assert_called_once_with(lf, str(output))


def test_delfi(runner, tmp_path, monkeypatch):
    output = tmp_path / "output"
    dataset = Mock()

    generate = Mock(return_value=dataset)
    monkeypatch.setattr(cli, "mock_delfi", generate)

    result = runner.invoke(
        cli.mock_cli,
        [
            "delfi",
            str(output),
            "--patients",
            "20",
            "--events-per-modality",
            "50",
            "--seed",
            "7",
        ],
    )

    assert result.exit_code == 0, result.output
    generate.assert_called_once_with(20, 50, 7)
    dataset.save.assert_called_once_with(str(output))


@pytest.mark.parametrize(
    ("command", "options"),
    [
        ("cpr", ["--nrows", "0"]),
        ("lpr2diag", ["--nrows", "0"]),
        ("lpr2adm", ["--patients", "0"]),
        ("lpr3diag", ["--nrows", "0"]),
        ("lpr3contact", ["--patients", "0"]),
        ("epikur", ["--nrows", "0"]),
        ("delfi", ["--events-per-modality", "0"]),
    ],
)
def test_mock_commands_reject_nonpositive_values(runner, tmp_path, command, options):
    result = runner.invoke(
        cli.mock_cli,
        [command, str(tmp_path / "output"), *options],
    )

    assert result.exit_code == 2
