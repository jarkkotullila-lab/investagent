import json
import re
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, Field, model_validator

from investagent.schemas import ResearchAnalyzeResponse, ResearchSource

DATASET_PATH = Path(__file__).parent / "datasets" / "research_v1.json"
_PERCENTAGE_KEYWORD_PATTERN = re.compile(
    r"(?P<number>\d+(?:\.\d+)?)\s*(?:%|percent)",
    re.IGNORECASE,
)
_PERCENTAGE_EXPRESSION_PATTERN = re.compile(
    r"(?<![\w.])(?P<number>\d+(?:\.\d+)?)\s*(?:%|percent\b)(?!\w)",
    re.IGNORECASE,
)


class EvaluationCase(BaseModel):
    case_id: str
    company_name: str
    sources: list[ResearchSource]
    required_facts_or_keywords: list[str]
    forbidden_claims_or_keywords: list[str]
    expected_source_ids: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def expected_sources_exist(self) -> "EvaluationCase":
        source_ids = {source.source_id for source in self.sources}
        if not set(self.expected_source_ids).issubset(source_ids):
            raise ValueError("expected source IDs must exist in the case sources")
        return self


class EvaluationDataset(BaseModel):
    dataset_version: str
    description: str
    cases: list[EvaluationCase] = Field(min_length=1)


@dataclass(frozen=True)
class EvaluationResult:
    case_id: str
    passed: bool
    failures: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvaluationReport:
    dataset_version: str
    results: tuple[EvaluationResult, ...]

    @property
    def passed_count(self) -> int:
        return sum(result.passed for result in self.results)

    @property
    def score(self) -> float:
        if not self.results:
            return 0.0
        return self.passed_count / len(self.results)


def load_evaluation_dataset(path: Path = DATASET_PATH) -> EvaluationDataset:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return EvaluationDataset.model_validate(payload)


def _contains_keyword(text: str, keyword: str) -> bool:
    percentage_keyword = _PERCENTAGE_KEYWORD_PATTERN.fullmatch(keyword)
    if percentage_keyword is not None:
        expected_number = percentage_keyword.group("number")
        return any(
            match.group("number") == expected_number
            for match in _PERCENTAGE_EXPRESSION_PATTERN.finditer(text)
        )
    return keyword.casefold() in text.casefold()


def evaluate_case(case: EvaluationCase, response: object) -> EvaluationResult:
    try:
        validated_response = ResearchAnalyzeResponse.model_validate(response)
    except (ValueError, TypeError):
        return EvaluationResult(
            case_id=case.case_id,
            passed=False,
            failures=("invalid response schema",),
        )

    input_source_ids = {source.source_id for source in case.sources}
    response_source_ids = set(validated_response.source_references)
    failures: list[str] = []

    if validated_response.company_name != case.company_name:
        failures.append("response company name does not match the case")
    if not response_source_ids.issubset(input_source_ids):
        failures.append("response references an unknown source ID")
    if not set(case.expected_source_ids).issubset(response_source_ids):
        failures.append("response is missing an expected source reference")

    response_text = " ".join(
        [
            validated_response.company_name,
            validated_response.summary,
            *validated_response.opportunities,
            *validated_response.risks,
        ]
    ).casefold()
    for required in case.required_facts_or_keywords:
        if not _contains_keyword(response_text, required):
            failures.append(f"missing required keyword: {required}")
    for forbidden in case.forbidden_claims_or_keywords:
        if _contains_keyword(response_text, forbidden):
            failures.append(f"contains forbidden claim/keyword: {forbidden}")

    return EvaluationResult(
        case_id=case.case_id,
        passed=not failures,
        failures=tuple(failures),
    )
