import re
import unicodedata

from app.advisors.base import ArchitectureAdvisor
from app.knowledge_base import FALLBACK_SERVICES, KNOWLEDGE_BASE, ServicePattern
from app.models import RecommendResponse, ServiceRecommendation


def _fold(text: str) -> str:
    """Remove acentos e baixa a caixa, pra 'não relacional' bater com 'nao relacional'."""
    normalized = unicodedata.normalize("NFD", text)
    without_accents = "".join(c for c in normalized if unicodedata.category(c) != "Mn")
    return without_accents.lower()


class RuleBasedAdvisor(ArchitectureAdvisor):
    """Casa a descrição do usuário contra um catálogo de padrões AWS conhecidos.

    Simples de propósito: correspondência de palavra-chave, não NLP. Serve
    como ponto de partida rápido e gratuito — ver ArchitectureAdvisor sobre
    como substituir isso por um motor baseado em LLM depois.
    """

    def recommend(self, description: str) -> RecommendResponse:
        folded = _fold(description)

        matched: list[ServicePattern] = [
            pattern
            for pattern in KNOWLEDGE_BASE
            if any(re.search(rf"\b{re.escape(_fold(kw))}", folded) for kw in pattern.keywords)
        ]

        # "banco não relacional" contém "banco de dados" como substring — sem esse
        # ajuste, o gatilho genérico do RDS dispara junto com o do DynamoDB, mesmo a
        # frase descrevendo o oposto de um banco relacional.
        if re.search(r"\bnao relacional\b", folded):
            matched = [p for p in matched if p.service != "Amazon RDS"]

        used_fallback = len(matched) == 0
        services = matched if matched else list(FALLBACK_SERVICES)
        services = sorted(services, key=lambda p: p.layer)

        return RecommendResponse(
            matched_services=[
                ServiceRecommendation(service=p.service, category=p.category, why=p.why) for p in services
            ],
            architecture_summary=self._build_summary(services, used_fallback),
            used_fallback=used_fallback,
        )

    @staticmethod
    def _build_summary(services: list[ServicePattern], used_fallback: bool) -> str:
        if not services:
            return "Não encontrei nenhum padrão conhecido nessa descrição — tente detalhar mais o problema."

        chain = " → ".join(p.service for p in services)
        prefix = (
            "Não encontrei palavras-chave específicas, então aqui vai um ponto de partida serverless comum: "
            if used_fallback
            else "Com base na descrição, uma arquitetura possível segue este fluxo: "
        )
        return prefix + chain
