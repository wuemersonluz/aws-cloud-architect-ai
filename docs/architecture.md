# Arquitetura

```
[Navegador]                    [Backend FastAPI]
   frontend/index.html   ──►    POST /recommend
                                     │
                                     ▼
                          ArchitectureAdvisor (interface)
                                     │
                                     ▼
                            RuleBasedAdvisor
                       (casa a descrição contra um
                        catálogo de padrões AWS)
```

## Por que uma interface (`ArchitectureAdvisor`) em vez de chamar a lógica direto?

O endpoint `/recommend` depende só do contrato `ArchitectureAdvisor.recommend(description) -> RecommendResponse`,
não de como a recomendação é gerada. Hoje isso é resolvido por `RuleBasedAdvisor` (correspondência de
palavra-chave contra um catálogo fixo, sem custo). Trocar por um motor baseado em LLM (ex: Claude) no
futuro é só implementar a mesma interface e trocar a instância em `main.py` — nenhuma outra parte do
sistema precisa mudar.

## O motor de regras (`RuleBasedAdvisor`)

1. Normaliza a descrição (remove acento, baixa caixa)
2. Procura por palavras-chave de cada padrão do catálogo (`knowledge_base.py`) na descrição
3. Um caso especial: "banco não relacional" contém a substring "relacional" — sem tratamento,
   isso dispararia RDS (SQL) por engano junto com DynamoDB. O advisor detecta essa negação
   explicitamente e remove o RDS do resultado nesse caso.
4. Se nada bater, cai num conjunto padrão serverless (API Gateway + Lambda + DynamoDB)
5. Ordena os serviços encontrados por "camada" (entrada → computação → dados → mensageria →
   observabilidade) pra montar um resumo de arquitetura em texto

## Limitações conhecidas

- Correspondência por palavra-chave, não NLP de verdade — frases muito indiretas ou fora do
  catálogo caem no fallback genérico
- Não considera custo, região, nem restrições de compliance
- Não gera diagrama visual, só a lista ordenada de serviços em texto
