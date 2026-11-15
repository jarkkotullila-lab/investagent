from pydantic import ValidationError

from investagent.prompts import build_research_v1_prompt
from investagent.providers import AIProvider
from investagent.schemas import ResearchAnalyzeRequest, ResearchAnalyzeResponse


class ResearchProviderResponseError(ValueError):
    """Raised when an AI provider response is invalid for the supplied research."""


class ResearchService:
    def __init__(self, provider: AIProvider) -> None:
        self._provider = provider

    async def analyze(self, request: ResearchAnalyzeRequest) -> ResearchAnalyzeResponse:
        raw_response = await self._provider.generate(build_research_v1_prompt(request))
        try:
            response = ResearchAnalyzeResponse.model_validate_json(raw_response)
        except ValidationError as error:
            raise ResearchProviderResponseError(
                "AI provider returned malformed research JSON."
            ) from error

        supplied_source_ids = {source.source_id for source in request.sources}
        if not response.source_references:
            raise ResearchProviderResponseError(
                "AI provider response must reference at least one supplied source."
            )
        if not set(response.source_references).issubset(supplied_source_ids):
            raise ResearchProviderResponseError(
                "AI provider response references a source ID absent from the request."
            )

        return response
