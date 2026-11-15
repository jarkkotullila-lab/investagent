from typing import Self

from pydantic import BaseModel, Field, model_validator


class ResearchSource(BaseModel):
    source_id: str = Field(min_length=1)
    text: str = Field(min_length=1)


class ResearchAnalyzeRequest(BaseModel):
    company_name: str = Field(min_length=1)
    sources: list[ResearchSource]

    @model_validator(mode="after")
    def source_ids_are_unique(self) -> Self:
        source_ids = [source.source_id for source in self.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("source IDs must be unique")
        return self


class ResearchAnalyzeResponse(BaseModel):
    company_name: str
    summary: str
    opportunities: list[str]
    risks: list[str]
    source_references: list[str]
