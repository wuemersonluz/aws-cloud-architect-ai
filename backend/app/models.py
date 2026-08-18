from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    description: str = Field(
        ...,
        min_length=5,
        description="Descrição em texto livre do problema/sistema que precisa de arquitetura AWS.",
        examples=["Preciso de uma API que recebe upload de imagens e processa em segundo plano"],
    )


class ServiceRecommendation(BaseModel):
    service: str
    category: str
    why: str


class RecommendResponse(BaseModel):
    matched_services: list[ServiceRecommendation]
    architecture_summary: str
    used_fallback: bool
