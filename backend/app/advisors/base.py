from abc import ABC, abstractmethod

from app.models import RecommendResponse


class ArchitectureAdvisor(ABC):
    """Contrato que qualquer motor de recomendação precisa seguir.

    O endpoint da API depende só desta interface, não da implementação
    concreta — RuleBasedAdvisor (sem custo, baseado em palavras-chave) pode
    ser trocado por um advisor baseado em LLM (ex: Claude) no futuro sem
    mudar nada no resto do sistema.
    """

    @abstractmethod
    def recommend(self, description: str) -> RecommendResponse:
        raise NotImplementedError
