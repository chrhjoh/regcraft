from pathlib import Path

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from regcraft.io import write_parquet, write_sharded_parquet, write_txt


@pytest.fixture
def lazyframe() -> pl.LazyFrame:
    return pl.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "value": ["a", "b", "c", "d", "e"],
        }
    ).lazy()


def test_write_sharded_parquet(lazyframe: pl.LazyFrame, tmp_path: Path):
    output_dir = tmp_path / "nested" / "output"

    write_sharded_parquet(lazyframe, output_dir, shard_size=2)

    files = sorted(output_dir.glob("*.parquet"))

    assert len(files) == 3
    assert [pl.read_parquet(f).height for f in files] == [2, 2, 1]

    result = pl.concat([pl.read_parquet(f) for f in files])
    assert_frame_equal(result, lazyframe.collect())


def test_write_sharded_parquet_empty(tmp_path: Path):
    lf = pl.DataFrame(schema={"id": pl.Int64, "value": pl.String}).lazy()

    output_dir = tmp_path / "output"

    write_sharded_parquet(lf, output_dir)

    assert output_dir.exists()
    assert list(output_dir.glob("*.parquet")) == []


@pytest.mark.parametrize("shard_size", [0, -1])
def test_write_sharded_parquet_invalid_shard_size(
    lazyframe: pl.LazyFrame, tmp_path: Path, shard_size: int
):
    with pytest.raises(ValueError, match="shard_size must be positive"):
        write_sharded_parquet(lazyframe, tmp_path, shard_size=shard_size)


@pytest.mark.parametrize("collect", [False, True])
def test_write_parquet(lazyframe: pl.LazyFrame, tmp_path: Path, collect: bool):
    output_path = tmp_path / "nested" / "output.parquet"

    write_parquet(lazyframe, str(output_path), collect=collect)

    assert output_path.exists()
    assert_frame_equal(
        pl.read_parquet(output_path),
        lazyframe.collect(),
    )


def test_write_txt(tmp_path: Path):
    output_path = tmp_path / "nested" / "output.txt"

    write_txt(["first", "second", "third"], str(output_path))

    assert output_path.exists()
    assert output_path.read_text() == "first\nsecond\nthird"


def test_write_txt_custom_separator(tmp_path: Path):
    output_path = tmp_path / "output.txt"

    write_txt(["first", "second", "third"], str(output_path), separator=",")

    assert output_path.read_text() == "first,second,third"


def test_write_txt_empty(tmp_path: Path):
    output_path = tmp_path / "output.txt"

    write_txt([], str(output_path))

    assert output_path.read_text() == ""
