from collections.abc import Mapping

from .types import CodeMetadata, CodeType

ICD10_CHAPTERS = {
    1: ("A00", "B99", "Certain infectious and parasitic diseases"),
    2: ("C00", "D48", "Neoplasms"),
    3: ("D50", "D89", "Diseases of the blood and blood-forming organs"),
    4: ("E00", "E90", "Endocrine, nutritional and metabolic diseases"),
    5: ("F00", "F99", "Mental and behavioural disorders"),
    6: ("G00", "G99", "Diseases of the nervous system"),
    7: ("H00", "H59", "Diseases of the eye and adnexa"),
    8: ("H60", "H95", "Diseases of the ear and mastoid process"),
    9: ("I00", "I99", "Diseases of the circulatory system"),
    10: ("J00", "J99", "Diseases of the respiratory system"),
    11: ("K00", "K93", "Diseases of the digestive system"),
    12: ("L00", "L99", "Diseases of the skin and subcutaneous tissue"),
    13: ("M00", "M99", "Diseases of the musculoskeletal system"),
    14: ("N00", "N99", "Diseases of the genitourinary system"),
    15: ("O00", "O99", "Pregnancy, childbirth and the puerperium"),
    16: ("P00", "P96", "Certain conditions originating in the perinatal period"),
    17: ("Q00", "Q99", "Congenital malformations and chromosomal abnormalities"),
    18: ("R00", "R99", "Symptoms, signs and abnormal clinical findings"),
    19: (
        "S00",
        "T98",
        "Injury, poisoning and certain other consequences of external causes",
    ),
    20: ("V01", "Y98", "External causes of morbidity and mortality"),
    21: (
        "Z00",
        "Z99",
        "Factors influencing health status and contact with health services",
    ),
    22: ("U00", "U99", "Codes for special purposes"),
}


def icd10_chapter(code: str) -> CodeMetadata:
    code = code.strip().upper().replace(".", "")
    category = code[:3]

    chapter = next(
        (
            (index, description)
            for index, (start, end, description) in ICD10_CHAPTERS.items()
            if start <= category <= end
        ),
        (None, None),
    )

    return CodeMetadata(
        code,
        CodeType.ICD10,
        chapter[0],
        chapter[1],
    )


ATC_CHAPTERS: Mapping[str, tuple[int, str]] = {
    "A": (1, "Alimentary tract and metabolism"),
    "B": (2, "Blood and blood forming organs"),
    "C": (3, "Cardiovascular system"),
    "D": (4, "Dermatologicals"),
    "G": (5, "Genito-urinary system and sex hormones"),
    "H": (6, "Systemic hormonal preparations"),
    "J": (7, "Antiinfectives for systemic use"),
    "L": (8, "Antineoplastic and immunomodulating agents"),
    "M": (9, "Musculo-skeletal system"),
    "N": (10, "Nervous system"),
    "P": (11, "Antiparasitic products, insecticides and repellents"),
    "R": (12, "Respiratory system"),
    "S": (13, "Sensory organs"),
    "V": (14, "Various"),
}


def atc_chapter(code: str) -> CodeMetadata:
    """Map an ATC code to its chapter index and description."""
    code = code.strip().upper()
    chapter = ATC_CHAPTERS.get(code[0])

    return CodeMetadata(
        code,
        CodeType.ATC,
        chapter[0] if chapter is not None else None,
        chapter[1] if chapter is not None else None,
    )


def code_to_chapter(code: str, code_type: CodeType) -> CodeMetadata:
    match code_type:
        case CodeType.ATC:
            return atc_chapter(code)
        case CodeType.ICD10:
            return icd10_chapter(code)
