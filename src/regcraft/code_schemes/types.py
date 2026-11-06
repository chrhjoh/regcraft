from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

type CodeQuery = Callable[[str], CodeMetadata]


class CodeType(Enum):
    ICD10 = 0
    ATC = 1


@dataclass
class CodeMetadata:
    code: str
    code_type: CodeType
    category: int | None = None
    description: str | None = None
