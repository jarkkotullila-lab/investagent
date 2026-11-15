import argparse
import asyncio
from collections.abc import Sequence

import httpx

from evaluation.evaluator import (
    EvaluationDataset,
    EvaluationReport,
    EvaluationResult,
    evaluate_case,
    load_evaluation_dataset,
)
from investagent.configuration import (
    AIConfigurationError,
    create_ai_provider_from_environment,
)
from investagent.ollama import OllamaProvider
from investagent.providers import AIProviderError
from investagent.research_service import ResearchProviderResponseError, ResearchService
from investagent.schemas import ResearchAnalyzeRequest, ResearchAnalyzeResponse


async def _ollama_is_available(provider: OllamaProvider) -> bool:
    try:
        async with httpx.AsyncClient(timeout=3, trust_env=False) as client:
            response = await client.get(f"{provider.base_url}/api/tags")
            response.raise_for_status()
    except (httpx.RequestError, httpx.HTTPStatusError):
        return False
    return True


async def _run_cases(
    provider: OllamaProvider,
    dataset: EvaluationDataset,
    show_response: bool = False,
) -> EvaluationReport | None:
    service = ResearchService(provider)
    case_results: list[tuple[EvaluationResult, ResearchAnalyzeResponse | None]] = []

    for case in dataset.cases:
        request = ResearchAnalyzeRequest(
            company_name=case.company_name,
            sources=case.sources,
        )
        try:
            response = await service.analyze(request)
        except ResearchProviderResponseError:
            case_results.append(
                (
                    EvaluationResult(
                        case_id=case.case_id,
                        passed=False,
                        failures=(
                            "provider output failed schema or source-reference validation",
                        ),
                    ),
                    None,
                )
            )
        except AIProviderError:
            for result, evaluated_response in case_results:
                _print_result(result, evaluated_response, show_response)
            print(f"FAIL {case.case_id}: local provider request failed.")
            print("Aggregate score: not calculated (live evaluation was incomplete).")
            return None
        else:
            case_results.append((evaluate_case(case, response), response))

    report = EvaluationReport(
        dataset_version=dataset.dataset_version,
        results=tuple(result for result, _ in case_results),
    )
    for result, response in case_results:
        _print_result(result, response, show_response)
    print(
        f"LIVE OLLAMA aggregate: {report.passed_count}/{len(report.results)} "
        f"passed ({report.score:.0%}) — {report.dataset_version}"
    )
    return report


def _print_result(
    result: EvaluationResult,
    response: ResearchAnalyzeResponse | None = None,
    show_response: bool = False,
) -> None:
    status = "PASS" if result.passed else "FAIL"
    print(f"{status} {result.case_id}")
    for failure in result.failures:
        print(f"  - {failure}")
    if show_response and response is not None:
        print(f"RESPONSE {result.case_id}:")
        print(response.model_dump_json(indent=2))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the live local Ollama evaluation.")
    parser.add_argument(
        "--show-response",
        action="store_true",
        help="print each evaluated response (use only with synthetic, non-sensitive data)",
    )
    args = parser.parse_args(argv)

    dataset = load_evaluation_dataset()
    try:
        provider = create_ai_provider_from_environment()
    except AIConfigurationError:
        print("ERROR: AI provider configuration is invalid.")
        return 2
    if provider is None:
        print("SKIPPED: AI provider is disabled; no live evaluation score was produced.")
        return 0
    if not isinstance(provider, OllamaProvider):
        print("ERROR: evaluation runner supports only the local Ollama provider.")
        return 2
    if not asyncio.run(_ollama_is_available(provider)):
        print("SKIPPED: local Ollama is unavailable; no live evaluation score was produced.")
        return 0

    report = asyncio.run(_run_cases(provider, dataset, show_response=args.show_response))
    if report is None:
        return 2
    return 0 if report.score == 1.0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
