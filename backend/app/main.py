from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.advisors import ArchitectureAdvisor, RuleBasedAdvisor
from app.models import RecommendRequest, RecommendResponse

app = FastAPI(
    title="AWS Cloud Architect AI",
    description="Sugere quais serviços AWS usar a partir da descrição de um problema.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # projeto de aprendizado local — restringir se for exposto publicamente
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trocar por outra implementação de ArchitectureAdvisor (ex: baseada em Claude)
# não exige mudar nada abaixo — o endpoint depende só da interface.
advisor: ArchitectureAdvisor = RuleBasedAdvisor()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/recommend", response_model=RecommendResponse)
def recommend(request: RecommendRequest) -> RecommendResponse:
    return advisor.recommend(request.description)
