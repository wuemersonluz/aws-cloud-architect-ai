from app.advisors.rule_based import RuleBasedAdvisor


def test_recommend_matches_upload_and_background_processing():
    advisor = RuleBasedAdvisor()
    result = advisor.recommend(
        "Preciso de uma API que recebe upload de imagens e processa em segundo plano"
    )

    services = {s.service for s in result.matched_services}
    assert "Amazon API Gateway" in services
    assert "Amazon S3" in services
    assert "AWS Lambda" in services
    assert result.used_fallback is False


def test_recommend_matches_relational_database():
    advisor = RuleBasedAdvisor()
    result = advisor.recommend("Quero um banco de dados relacional para minha aplicação")

    services = {s.service for s in result.matched_services}
    assert "Amazon RDS" in services


def test_recommend_is_accent_insensitive():
    with_accent = RuleBasedAdvisor().recommend("banco não relacional de alta escala")
    without_accent = RuleBasedAdvisor().recommend("banco nao relacional de alta escala")

    services_with = {s.service for s in with_accent.matched_services}
    services_without = {s.service for s in without_accent.matched_services}
    assert services_with == services_without
    assert "Amazon DynamoDB" in services_with


def test_recommend_does_not_confuse_non_relational_with_relational():
    # "banco não relacional" contém a palavra "relacional" — sem tratamento
    # específico, isso dispararia RDS (SQL) por engano junto com DynamoDB.
    advisor = RuleBasedAdvisor()
    result = advisor.recommend("Preciso de um banco de dados não relacional de alta escala")

    services = {s.service for s in result.matched_services}
    assert "Amazon DynamoDB" in services
    assert "Amazon RDS" not in services


def test_recommend_falls_back_when_nothing_matches():
    advisor = RuleBasedAdvisor()
    result = advisor.recommend("blablabla xyzxyz sem sentido nenhum aqui")

    assert result.used_fallback is True
    assert len(result.matched_services) > 0


def test_recommend_orders_services_by_architecture_layer():
    advisor = RuleBasedAdvisor()
    result = advisor.recommend("API com fila para desacoplar processamento assíncrono e banco não relacional")

    services = [s.service for s in result.matched_services]
    # API Gateway (entrada) deve vir antes de SQS (mensageria, camada mais interna)
    assert services.index("Amazon API Gateway") < services.index("Amazon SQS")
