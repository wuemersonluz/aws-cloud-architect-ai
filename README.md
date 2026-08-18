# AWS Cloud Architect AI

Ferramenta que sugere quais serviços AWS usar a partir da descrição de um problema em texto livre.

Descreve o que seu sistema precisa fazer ("preciso de uma API que recebe upload de imagens e
processa em segundo plano") e ela devolve uma sugestão de arquitetura: quais serviços usar, em
que ordem se conectam, e por que cada um faz sentido ali.

---

## Como funciona

```
Você descreve o problema
        │
        ▼
POST /recommend (FastAPI)
        │
        ▼
Motor de recomendação casa a descrição contra um catálogo de ~15 padrões AWS conhecidos
        │
        ▼
Lista de serviços sugeridos + explicação de cada um + resumo do fluxo
```

O motor de recomendação (`RuleBasedAdvisor`) é baseado em regras — sem custo, sem chave de API,
mas construído atrás de uma interface (`ArchitectureAdvisor`) pensada pra ser substituída por um
motor baseado em LLM (Claude) depois, sem precisar mudar o resto do sistema. Detalhes em
[docs/architecture.md](docs/architecture.md).

---

## Como rodar

**Backend:**

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate        # Windows — no Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000
```

**Frontend:** abra `frontend/index.html` direto no navegador (sem build, sem dependência).

Teste rápido pela API:

```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"description": "Preciso de uma API que recebe upload de imagens e processa em segundo plano"}'
```

---

## Testes

```bash
cd backend
pytest -v
```

9 testes cobrindo o motor de recomendação (incluindo um caso de falso positivo real: "banco não
relacional" sendo confundido com "relacional" por conter a palavra como substring) e a API.

---

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `backend/app/advisors/` | Interface `ArchitectureAdvisor` + implementação `RuleBasedAdvisor` |
| `backend/app/knowledge_base.py` | Catálogo de padrões AWS (serviço, categoria, palavras-chave, explicação) |
| `backend/app/main.py` | API FastAPI (`POST /recommend`) |
| `backend/tests/` | Testes automatizados |
| `frontend/` | Interface (HTML/CSS/JS puro, sem build) |
| `docs/` | Arquitetura e decisões técnicas |
| `infrastructure/` | Planejado — Terraform/CDK pra hospedar isso na própria AWS |

---

## Roadmap

- [ ] Motor de recomendação baseado em LLM (Claude), implementando a mesma interface `ArchitectureAdvisor`
- [ ] Diagrama visual da arquitetura sugerida (não só texto)
- [ ] Deploy real na AWS (Lambda + API Gateway + S3/CloudFront) via Terraform
