from unittest.mock import Mock

import polars as pl

import regcraft.cli.join as cli


def test_join_lsr(runner, tmp_path, monkeypatch):
    epikur = tmp_path / "epikur.parquet"
    laegemiddel = tmp_path / "laegemiddel.parquet"
    output = tmp_path / "output.parquet"

    epikur.touch()
    laegemiddel.touch()

    lf = pl.LazyFrame({"value": [1, 2]})
    create_lsr = Mock(return_value=lf)
    write_parquet = Mock()

    monkeypatch.setattr(cli, "create_lsr", create_lsr)
    monkeypatch.setattr(cli, "write_parquet", write_parquet)

    result = runner.invoke(
        cli.join,
        ["lsr", str(epikur), str(laegemiddel), str(output)],
    )

    assert result.exit_code == 0
    create_lsr.assert_called_once_with(str(epikur), str(laegemiddel))
    write_parquet.assert_called_once_with(lf, str(output), collect=False)


def test_join_lsr_collect(runner, tmp_path, monkeypatch):
    epikur = tmp_path / "epikur.parquet"
    laegemiddel = tmp_path / "laegemiddel.parquet"
    output = tmp_path / "output.parquet"

    epikur.touch()
    laegemiddel.touch()

    lf = pl.LazyFrame({"value": [1]})
    monkeypatch.setattr(cli, "create_lsr", Mock(return_value=lf))
    write_parquet = Mock()
    monkeypatch.setattr(cli, "write_parquet", write_parquet)

    result = runner.invoke(
        cli.join,
        ["lsr", str(epikur), str(laegemiddel), str(output), "--collect"],
    )

    assert result.exit_code == 0
    write_parquet.assert_called_once_with(lf, str(output), collect=True)


def test_join_diag_adm_lpr2(runner, tmp_path, monkeypatch):
    lpr2_diag = tmp_path / "lpr2_diag.parquet"
    lpr2_adm = tmp_path / "lpr2_adm.parquet"
    output = tmp_path / "output.parquet"

    lpr2_diag.touch()
    lpr2_adm.touch()

    lf = pl.LazyFrame({"value": [1]})
    create_diag_adm = Mock(return_value=lf)
    write_parquet = Mock()

    monkeypatch.setattr(cli, "create_diag_adm", create_diag_adm)
    monkeypatch.setattr(cli, "write_parquet", write_parquet)

    result = runner.invoke(
        cli.join,
        [
            "diag-adm",
            str(output),
            "--lpr2-diag-path",
            str(lpr2_diag),
            "--lpr2-adm-path",
            str(lpr2_adm),
        ],
    )

    assert result.exit_code == 0
    create_diag_adm.assert_called_once_with(
        lpr2_diag=str(lpr2_diag),
        lpr2_adm=str(lpr2_adm),
        lpr3_diag=None,
        lpr3_adm=None,
    )
    write_parquet.assert_called_once_with(lf, str(output))


def test_join_diag_adm_lpr3(runner, tmp_path, monkeypatch):
    lpr3_diag = tmp_path / "lpr3_diag.parquet"
    lpr3_adm = tmp_path / "lpr3_adm.parquet"
    output = tmp_path / "output.parquet"

    lpr3_diag.touch()
    lpr3_adm.touch()

    lf = pl.LazyFrame({"value": [1]})
    create_diag_adm = Mock(return_value=lf)
    write_parquet = Mock()

    monkeypatch.setattr(cli, "create_diag_adm", create_diag_adm)
    monkeypatch.setattr(cli, "write_parquet", write_parquet)

    result = runner.invoke(
        cli.join,
        [
            "diag-adm",
            str(output),
            "--lpr3-diag-path",
            str(lpr3_diag),
            "--lpr3-adm-path",
            str(lpr3_adm),
        ],
    )

    assert result.exit_code == 0
    create_diag_adm.assert_called_once_with(
        lpr2_diag=None,
        lpr2_adm=None,
        lpr3_diag=str(lpr3_diag),
        lpr3_adm=str(lpr3_adm),
    )
    write_parquet.assert_called_once_with(lf, str(output))


def test_join_diag_adm_both_versions(runner, tmp_path, monkeypatch):
    paths = {
        name: tmp_path / f"{name}.parquet"
        for name in ["lpr2_diag", "lpr2_adm", "lpr3_diag", "lpr3_adm"]
    }
    for path in paths.values():
        path.touch()

    output = tmp_path / "output.parquet"
    lf = pl.LazyFrame({"value": [1]})

    create_diag_adm = Mock(return_value=lf)
    write_parquet = Mock()
    monkeypatch.setattr(cli, "create_diag_adm", create_diag_adm)
    monkeypatch.setattr(cli, "write_parquet", write_parquet)

    result = runner.invoke(
        cli.join,
        [
            "diag-adm",
            str(output),
            "--lpr2-diag-path",
            str(paths["lpr2_diag"]),
            "--lpr2-adm-path",
            str(paths["lpr2_adm"]),
            "--lpr3-diag-path",
            str(paths["lpr3_diag"]),
            "--lpr3-adm-path",
            str(paths["lpr3_adm"]),
        ],
    )

    assert result.exit_code == 0
    create_diag_adm.assert_called_once_with(
        **{name: str(path) for name, path in paths.items()}
    )
    write_parquet.assert_called_once_with(lf, str(output))


def test_join_diag_adm_requires_matching_lpr2_paths(runner, tmp_path):
    output = tmp_path / "output.parquet"
    diag = tmp_path / "lpr2_diag.parquet"
    diag.touch()

    result = runner.invoke(
        cli.join,
        ["diag-adm", str(output), "--lpr2-diag-path", str(diag)],
    )

    assert result.exit_code == 2
    assert (
        "--lpr2-diag-path and --lpr2-adm-path must be specified together."
        in result.output
    )


def test_join_diag_adm_requires_matching_lpr3_paths(runner, tmp_path):
    output = tmp_path / "output.parquet"
    diag = tmp_path / "lpr3_diag.parquet"
    diag.touch()

    result = runner.invoke(
        cli.join,
        ["diag-adm", str(output), "--lpr3-diag-path", str(diag)],
    )

    assert result.exit_code == 2
    assert (
        "--lpr3-diag-path and --lpr3-adm-path must be specified together."
        in result.output
    )


def test_join_diag_adm_requires_at_least_one_version(runner, tmp_path):
    output = tmp_path / "output.parquet"

    result = runner.invoke(cli.join, ["diag-adm", str(output)])

    assert result.exit_code == 2
    assert "Either lpr3 and or lpr2 paths must be specified." in result.output
