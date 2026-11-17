from polars.testing import assert_frame_equal

from regcraft.datasets.delfi import DelfiDataset
from regcraft.datasets.utils import Split
from regcraft.mock.datasets import mock_delfi


def test_mock_delfi():
    dataset = mock_delfi(patients=100, events_per_modality=20)

    assert isinstance(dataset, DelfiDataset)

    assert set(dataset.sequences) == set(Split)
    assert set(dataset.covariates) == set(Split)

    assert dataset.token_attributes.collect().height > 0
    assert dataset.feature_map.collect().height > 0
    assert len(list(dataset.candidate_texts)) > 0

    for split, sequences in dataset.sequences.items():
        df = sequences.collect()

        assert df.height > 0
        assert {"patient_id", "event_texts", "times_days"} <= set(df.columns)

        covariates = dataset.covariates[split].collect()
        assert set(covariates["patient_id"].unique().to_list()) <= set(
            df["patient_id"].to_list()
        )


def test_mock_delfi_reproducible():
    first = mock_delfi(patients=100, events_per_modality=100)
    second = mock_delfi(patients=100, events_per_modality=100)

    for split in Split:
        assert_frame_equal(
            first.sequences[split].collect(),
            second.sequences[split].collect(),
        )
        assert_frame_equal(
            first.covariates[split].collect(),
            second.covariates[split].collect(),
        )

    assert_frame_equal(
        first.token_attributes.collect(),
        second.token_attributes.collect(),
    )
    assert_frame_equal(
        first.feature_map.collect(),
        second.feature_map.collect(),
    )
    assert list(first.candidate_texts) == list(second.candidate_texts)
