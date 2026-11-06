import os
from collections.abc import Iterable
from pathlib import Path

import polars as pl


def write_sharded_parquet(
    lf: pl.LazyFrame,
    output_dir: str | Path,
    shard_size: int = 100_000,
) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = lf.collect()

    for i, offset in enumerate(range(0, df.height, shard_size)):
        df.slice(offset, shard_size).write_parquet(output_dir / f"part-{i:05d}.parquet")


def write_parquet(lf: pl.LazyFrame, output_path: str, collect: bool = False):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if collect:
        lf.collect().write_parquet(output_path)
    else:
        lf.sink_parquet(output_path)


def write_txt(lines: Iterable[str], output_path: str, separator="\n"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as fh:
        fh.write(separator.join(lines))
