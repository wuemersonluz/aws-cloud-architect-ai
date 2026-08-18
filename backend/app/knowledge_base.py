"""Catálogo de padrões AWS usado pelo RuleBasedAdvisor.

Cada padrão tem palavras-chave em PT-BR/EN que, se aparecerem na descrição do
usuário, indicam que aquele serviço provavelmente faz parte da arquitetura.
Isso é propositalmente simples (correspondência de texto, não NLP de verdade)
— é o ponto de partida rápido e sem custo. Um ArchitectureAdvisor baseado em
LLM (ver advisors/base.py) pode substituir isso depois sem mudar o resto do
sistema, já que os dois implementam a mesma interface.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ServicePattern:
    service: str
    category: str
    keywords: tuple[str, ...]
    why: str
    # Ordem de exibição sugerida (menor = mais "próximo do usuário" na arquitetura)
    layer: int


KNOWLEDGE_BASE: tuple[ServicePattern, ...] = (
    ServicePattern(
        service="Amazon CloudFront",
        category="Entrega de conteúdo",
        keywords=("cdn", "distribuição global", "baixa latência", "cache de conteúdo", "site estático"),
        why="Distribui conteúdo com baixa latência via edge locations, cacheando respostas perto do usuário final.",
        layer=0,
    ),
    ServicePattern(
        service="Amazon API Gateway",
        category="Ponto de entrada",
        keywords=("api", "rest", "endpoint", "http", "graphql"),
        why="Expõe endpoints HTTP gerenciados com autenticação, throttling e integração nativa com Lambda.",
        layer=1,
    ),
    ServicePattern(
        service="Application Load Balancer",
        category="Ponto de entrada",
        keywords=("balanceador de carga", "load balancer", "alta disponibilidade", "múltiplas instâncias"),
        why="Distribui tráfego HTTP(S) entre múltiplas instâncias/containers, com health checks automáticos.",
        layer=1,
    ),
    ServicePattern(
        service="AWS Lambda",
        category="Computação",
        keywords=("serverless", "função", "sob demanda", "processamento em segundo plano", "background", "processa"),
        why="Executa código sob demanda sem gerenciar servidor — cobra só pelo tempo de execução, ideal para cargas variáveis.",
        layer=2,
    ),
    ServicePattern(
        service="Amazon ECS / Fargate",
        category="Computação",
        keywords=("container", "docker", "microsserviço", "microservico"),
        why="Roda containers gerenciados sem precisar administrar servidores (Fargate) ou com controle total do cluster (EC2).",
        layer=2,
    ),
    ServicePattern(
        service="Amazon EC2",
        category="Computação",
        keywords=("servidor", "máquina virtual", "vm", "instância dedicada"),
        why="Máquina virtual com controle total do sistema operacional — use quando precisar de software que não roda bem em container/serverless.",
        layer=2,
    ),
    ServicePattern(
        service="Amazon RDS",
        category="Banco de dados",
        # "relacional" sozinho colidiria com "banco NÃO relacional" (a frase de
        # gatilho do DynamoDB) — usar só frases compostas evita o falso positivo.
        keywords=("banco de dados", "sql", "postgres", "mysql", "banco relacional"),
        why="Banco relacional gerenciado (backups, patch, replicação automáticos) — para dados estruturados com relações entre tabelas.",
        layer=3,
    ),
    ServicePattern(
        service="Amazon DynamoDB",
        category="Banco de dados",
        keywords=("nosql", "banco não relacional", "chave-valor", "alta escala", "milhões de registros"),
        why="Banco NoSQL totalmente gerenciado, escala horizontalmente sem esforço — bom para acesso por chave em grande volume.",
        layer=3,
    ),
    ServicePattern(
        service="Amazon ElastiCache",
        category="Cache",
        keywords=("cache", "redis", "memcached", "sessão", "resposta rápida"),
        why="Cache em memória gerenciado — reduz carga do banco e acelera leituras repetidas.",
        layer=3,
    ),
    ServicePattern(
        service="Amazon S3",
        category="Armazenamento",
        keywords=("upload", "arquivo", "imagem", "vídeo", "storage", "armazenamento", "backup", "site estático"),
        why="Armazenamento de objetos durável e barato — para arquivos, mídia, backups ou hospedar site estático.",
        layer=3,
    ),
    ServicePattern(
        service="Amazon SQS",
        category="Mensageria",
        keywords=("fila", "queue", "assíncrono", "assincrono", "desacoplar", "processamento em lote", "batch"),
        why="Fila gerenciada que desacopla produtor e consumidor — absorve picos e garante que nenhuma mensagem se perca.",
        layer=4,
    ),
    ServicePattern(
        service="Amazon SNS",
        category="Mensageria",
        keywords=("notificação", "notificacao", "email", "sms", "push", "alerta", "múltiplos consumidores"),
        why="Publica uma mensagem pra múltiplos destinos (fila, e-mail, SMS, Lambda) de uma vez só — padrão pub/sub.",
        layer=4,
    ),
    ServicePattern(
        service="AWS Step Functions",
        category="Orquestração",
        keywords=("fluxo de trabalho", "workflow", "etapas", "orquestração", "orquestracao", "pipeline"),
        why="Orquestra múltiplas etapas (Lambdas, tarefas) como uma máquina de estados visual, com retry e tratamento de erro nativos.",
        layer=4,
    ),
    ServicePattern(
        service="Amazon Cognito",
        category="Autenticação",
        keywords=("login", "autenticação", "autenticacao", "usuário", "usuario", "cadastro", "signup"),
        why="Gerencia cadastro, login e controle de acesso de usuários sem precisar construir isso do zero.",
        layer=2,
    ),
    ServicePattern(
        service="Amazon SageMaker",
        category="Machine Learning",
        keywords=("machine learning", "ia", "inteligência artificial", "modelo", "previsão", "previsao", "treinar"),
        why="Plataforma gerenciada para treinar, hospedar e servir modelos de machine learning.",
        layer=2,
    ),
    ServicePattern(
        service="Amazon CloudWatch",
        category="Observabilidade",
        keywords=("monitoramento", "logs", "métricas", "metricas", "alarme", "observabilidade"),
        why="Coleta logs e métricas de todos os outros serviços, permitindo alarmes e dashboards de saúde do sistema.",
        layer=5,
    ),
)

# Usado quando nenhuma palavra-chave bate — um ponto de partida serverless
# genérico, sensato para "preciso de um backend" sem mais detalhes.
FALLBACK_SERVICES: tuple[ServicePattern, ...] = tuple(
    p for p in KNOWLEDGE_BASE if p.service in ("Amazon API Gateway", "AWS Lambda", "Amazon DynamoDB")
)
