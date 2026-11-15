import json

import httpx
import pytest

import evaluation.runner as evaluation_runner
from evaluation.evaluator import (
    EvaluationCase,
    EvaluationDataset,
    EvaluationReport,
    EvaluationResult,
    evaluate_case,
    load_evaluation_dataset,
)
from investagent.ollama import OllamaProvider


@pytest.fixture
def first_case():
    return load_evaluation_dataset().cases[0]


def _passing_response(case: EvaluationCase) -> dict[str, object]:
    return {
        "company_name": case.company_name,
        "summary": " ".join(case.required_facts_or_keywords),
        "opportunities": [],
        "risks": [],
        "source_references": case.expected_source_ids,
    }


def test_versioned_dataset_contains_synthetic_cases() -> None:
    dataset = load_evaluation_dataset()

    assert dataset.dataset_version == "research_v1"
    assert len(dataset.cases) >= 2
    assert all("Example " in case.company_name for case in dataset.cases)


def test_evaluator_passes_valid_response(first_case: EvaluationCase) -> None:
    result = evaluate_case(first_case, _passing_response(first_case))

    assert result.passed
    assert result.failures == ()


def test_evaluator_fails_invalid_response_schema(first_case: EvaluationCase) -> None:
    result = evaluate_case(first_case, {"company_name": first_case.company_name})

    assert not result.passed
    assert result.failures == ("invalid response schema",)


def test_evaluator_fails_when_company_name_does_not_match(
    first_case: EvaluationCase,
) -> None:
    response = _passing_response(first_case)
    response["company_name"] = "Example Harbor Tools"

    result = evaluate_case(first_case, response)

    assert not result.passed
    assert "response company name does not match the case" in result.failures


def test_evaluator_fails_unknown_and_missing_expected_source_ids(
    first_case: EvaluationCase,
) -> None:
    response = _passing_response(first_case)
    response["source_references"] = ["unknown-source"]

    result = evaluate_case(first_case, response)

    assert not result.passed
    assert "response references an unknown source ID" in result.failures
    assert "response is missing an expected source reference" in result.failures


def test_evaluator_fails_when_required_facts_are_missing(first_case: EvaluationCase) -> None:
    response = _passing_response(first_case)
    response["summary"] = "A generic synthetic summary."

    result = evaluate_case(first_case, response)

    assert not result.passed
    assert any("missing required keyword" in failure for failure in result.failures)


def test_evaluator_fails_when_forbidden_claim_is_present(first_case: EvaluationCase) -> None:
    response = _passing_response(first_case)
    response["risks"] = ["Revenue doubled."]

    result = evaluate_case(first_case, response)

    assert not result.passed
    assert "contains forbidden claim/keyword: revenue doubled" in result.failures


@pytest.mark.parametrize(
    ("keyword", "summary", "matches"),
    [
        ("10 percent", "Costs decreased by 10 percent.", True),
        (
            "10 percent",
            "Unit manufacturing costs have decreased by 10% in a hypothetical test period.",
            True,
        ),
        ("10 percent", "Costs decreased by 10 %.", True),
        ("10%", "Costs decreased by 10 percent.", True),
        ("10 %", "Costs decreased by 10%.", True),
        ("10 percent", "Costs decreased by 100 percent.", False),
        ("10 percent", "Costs decreased by 15 percent.", False),
        ("10 percent", "Costs decreased by 110 percent.", False),
        ("10 percent", "Costs decreased by 10.5 percent.", False),
        ("10 percent", "Costs decreased by 10 percentage points.", False),
    ],
)
def test_evaluator_percentage_keyword_matching_respects_value_and_boundaries(
    first_case: EvaluationCase,
    keyword: str,
    summary: str,
    matches: bool,
) -> None:
    case = first_case.model_copy(
        update={
            "required_facts_or_keywords": [keyword],
            "forbidden_claims_or_keywords": [],
        }
    )
    response = _passing_response(case)
    response["summary"] = summary

    result = evaluate_case(case, response)

    assert result.passed is matches


def test_evaluator_normalizes_percentage_in_forbidden_keywords(
    first_case: EvaluationCase,
) -> None:
    case = first_case.model_copy(
        update={
            "required_facts_or_keywords": [],
            "forbidden_claims_or_keywords": ["10 percent"],
        }
    )
    response = _passing_response(case)
    response["summary"] = "Costs decreased by 10 %."

    result = evaluate_case(case, response)

    assert not result.passed
    assert result.failures == ("contains forbidden claim/keyword: 10 percent",)


def test_evaluator_preserves_case_insensitive_ordinary_keyword_matching(
    first_case: EvaluationCase,
) -> None:
    case = first_case.model_copy(
        update={
            "required_facts_or_keywords": ["revenue grew"],
            "forbidden_claims_or_keywords": [],
        }
    )
    response = _passing_response(case)
    response["summary"] = "REVENUE GREW in the synthetic test period."

    result = evaluate_case(case, response)

    assert result.passed


def test_evaluation_report_aggregates_case_results() -> None:
    report = EvaluationReport(
        dataset_version="research_v1",
        results=(
            EvaluationResult("case-one", True),
            EvaluationResult("case-two", False, ("missing fact",)),
        ),
    )

    assert report.passed_count == 1
    assert report.score == 0.5


@pytest.mark.parametrize(
    ("argv", "shows_response"),
    [
        ([], False),
        (["--show-response"], True),
    ],
)
def test_live_runner_shows_response_only_when_requested(
    first_case: EvaluationCase,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    argv: list[str],
    shows_response: bool,
) -> None:
    invalid_but_well_formed_response = {
        "company_name": first_case.company_name,
        "summary": "A generic synthetic summary.",
        "opportunities": [],
        "risks": [],
        "source_references": first_case.expected_source_ids,
    }

    def handle(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"response": json.dumps(invalid_but_well_formed_response)},
        )

    provider = OllamaProvider(
        base_url="http://127.0.0.1:11434",
        model="qwen2.5:3b",
        timeout=1,
        transport=httpx.MockTransport(handle),
    )
    dataset = EvaluationDataset(
        dataset_version="research_v1",
        description="Synthetic test dataset.",
        cases=[first_case],
    )

    async def ollama_is_available(_provider: OllamaProvider) -> bool:
        return True

    monkeypatch.setattr(
        evaluation_runner,
        "create_ai_provider_from_environment",
        lambda: provider,
    )
    monkeypatch.setattr(evaluation_runner, "load_evaluation_dataset", lambda: dataset)
    monkeypatch.setattr(evaluation_runner, "_ollama_is_available", ollama_is_available)

    exit_code = evaluation_runner.main(argv)
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "FAIL synthetic-cedar-works" in output
    assert ("RESPONSE synthetic-cedar-works:" in output) is shows_response
    assert ("A generic synthetic summary." in output) is shows_response


def test_live_runner_skips_without_provider(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        evaluation_runner,
        "create_ai_provider_from_environment",
        lambda: None,
    )

    assert evaluation_runner.main([]) == 0
    assert "SKIPPED:" in capsys.readouterr().out


def test_live_runner_skips_when_ollama_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    provider = OllamaProvider(
        base_url="http://127.0.0.1:11434",
        model="qwen2.5:3b",
        timeout=1,
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json={"models": []})
        ),
    )

    async def unavailable(_provider: OllamaProvider) -> bool:
        return False

    monkeypatch.setattr(
        evaluation_runner,
        "create_ai_provider_from_environment",
        lambda: provider,
    )
    monkeypatch.setattr(evaluation_runner, "_ollama_is_available", unavailable)

    assert evaluation_runner.main([]) == 0
    assert "SKIPPED: local Ollama is unavailable" in capsys.readouterr().out
