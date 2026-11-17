import pytest

from regcraft.code_schemes.chapters import (
    atc_chapter,
    code_to_chapter,
    icd10_chapter,
)
from regcraft.code_schemes.types import CodeMetadata, CodeType


def test_icd10_chapter_normalises_code():
    result = icd10_chapter("  e11.9 ")

    assert result.code == "E119"
    assert result.category == 4


@pytest.mark.parametrize("code", ["XY100", "123", "E1", "E110XYZ", "E11.9.1"])
def test_icd10_chapter_invalid_code(code):
    with pytest.raises(ValueError, match="Invalid ICD-10 code"):
        icd10_chapter(code)


@pytest.mark.parametrize(
    ("code", "chapter", "description"),
    [
        ("A", 1, "Alimentary tract and metabolism"),
        ("B", 2, "Blood and blood forming organs"),
        ("C", 3, "Cardiovascular system"),
        ("J", 7, "Antiinfectives for systemic use"),
        ("N", 10, "Nervous system"),
        ("V", 14, "Various"),
    ],
)
def test_atc_chapter(code, chapter, description):
    result = atc_chapter(code)

    assert result == CodeMetadata(code, CodeType.ATC, chapter, description)


def test_atc_chapter_normalises_code():
    result = atc_chapter(" j01ca04 ")

    assert result.code == "J01CA04"
    assert result.category == 7


@pytest.mark.parametrize("code", ["XYZ1234", "123", "A1", "A123456", "A12.3"])
def test_atc_chapter_invalid_code(code):
    with pytest.raises(ValueError, match="Invalid ATC code"):
        atc_chapter(code)


@pytest.mark.parametrize(
    ("code", "code_type", "expected_type", "expected_chapter"),
    [
        ("E11.9", CodeType.ICD10, CodeType.ICD10, 4),
        ("A10BA02", CodeType.ATC, CodeType.ATC, 1),
    ],
)
def test_code_to_chapter(code, code_type, expected_type, expected_chapter):
    result = code_to_chapter(code, code_type)

    assert result.code == code.upper().replace(".", "")
    assert result.code_type == expected_type
    assert result.category == expected_chapter


@pytest.mark.parametrize(
    ("code", "code_type", "error"),
    [
        ("XY100", CodeType.ICD10, "Invalid ICD-10 code"),
        ("XYZ1234", CodeType.ATC, "Invalid ATC code"),
    ],
)
def test_code_to_chapter_invalid_code(code, code_type, error):
    with pytest.raises(ValueError, match=error):
        code_to_chapter(code, code_type)
