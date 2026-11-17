from unittest.mock import Mock, call

import polars as pl

import regcraft.cli.dataset as cli


def test_build_delfi(runner, tmp_path, monkeypatch):
    cpr_path = tmp_path / "cpr.parquet"
    lsr_path = tmp_path / "lsr.parquet"
    output_dir = tmp_path / "output"

    cpr_path.touch()
    lsr_path.touch()

    cpr = pl.LazyFrame({"patient_id": ["A"]})
    lsr = pl.LazyFrame({"patient_id": ["A"]})
    dataset = Mock()

    scan_parquet = Mock(side_effect=[cpr, lsr])
    build = Mock(return_value=dataset)

    monkeypatch.setattr(cli.pl, "scan_parquet", scan_parquet)
    monkeypatch.setattr(cli, "build_delfi_dataset", build)

    result = runner.invoke(
        cli.dataset,
        [
            "delfi",
            str(cpr_path),
            str(output_dir),
            "--lsr-path",
            str(lsr_path),
            "--atc-token-level",
            "5",
            "--val-percent",
            "0.15",
        ],
    )

    assert result.exit_code == 0, result.output

    assert scan_parquet.call_args_list == [
        call(str(cpr_path)),
        call(str(lsr_path)),
    ]

    build.assert_called_once_with(
        cpr=cpr,
        lsr=lsr,
        diag_adms=None,
        atc_token_level=5,
        icd10_token_level=3,
        min_atc_tokens=5,
        min_icd10_tokens=5,
        val_percent=0.15,
        test_percent=0.2,
    )

    dataset.save.assert_called_once_with(str(output_dir))


def test_build_delfi_with_both_sources(runner, tmp_path, monkeypatch):
    cpr_path = tmp_path / "cpr.parquet"
    lsr_path = tmp_path / "lsr.parquet"
    diag_path = tmp_path / "diag.parquet"

    for path in [cpr_path, lsr_path, diag_path]:
        path.touch()

    frames = [
        pl.LazyFrame({"patient_id": ["A"]}),
        pl.LazyFrame({"patient_id": ["A"]}),
        pl.LazyFrame({"patient_id": ["A"]}),
    ]

    scan_parquet = Mock(side_effect=frames)
    build = Mock(return_value=Mock())

    monkeypatch.setattr(cli.pl, "scan_parquet", scan_parquet)
    monkeypatch.setattr(cli, "build_delfi_dataset", build)

    result = runner.invoke(
        cli.dataset,
        [
            "delfi",
            str(cpr_path),
            str(tmp_path / "output"),
            "--lsr-path",
            str(lsr_path),
            "--diag-adm-path",
            str(diag_path),
        ],
    )

    assert result.exit_code == 0, result.output

    build.assert_called_once_with(
        cpr=frames[0],
        lsr=frames[1],
        diag_adms=frames[2],
        atc_token_level=4,
        icd10_token_level=3,
        min_atc_tokens=5,
        min_icd10_tokens=5,
        val_percent=0.1,
        test_percent=0.2,
    )


def test_build_delfi_requires_source(runner, tmp_path, monkeypatch):
    cpr_path = tmp_path / "cpr.parquet"
    cpr_path.touch()

    build = Mock()
    monkeypatch.setattr(cli, "build_delfi_dataset", build)

    result = runner.invoke(
        cli.dataset,
        ["delfi", str(cpr_path), str(tmp_path / "output")],
    )

    assert result.exit_code == 2
    assert "Either lsr_path or diag_adm_path must be specified" in result.output
    build.assert_not_called()
