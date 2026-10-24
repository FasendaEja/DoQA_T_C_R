"""Тесты для загрузчика правил."""

import pytest
from pathlib import Path
from services.rules_loader import RulesLoader


@pytest.fixture
def temp_rules_file(tmp_path):
    """Создание временного файла правил."""
    rules_file = tmp_path / "test_rules.md"
    rules_file.write_text(
        "# Правила DoQA v1.10.0\n\n"
        "## 1. Название\n\n"
        "Запрещены стоп-слова: проверка, тестирование\n\n"
        "## 2. Описание\n\n"
        "Описание обязательно\n",
        encoding="utf-8",
    )
    return rules_file


@pytest.fixture
def temp_scoring_config(tmp_path):
    """Создание временного файла конфигурации оценки."""
    config_file = tmp_path / "test_scoring.yaml"
    config_file.write_text(
        "weights:\n"
        "  title: 10\n"
        "  description: 15\n"
        "  preconditions: 10\n"
        "  test_ 10\n"
        "  step_instructions: 25\n"
        "  expected_results: 20\n"
        "  overall_coherence: 5\n"
        "\n"
        "severity_coefficients:\n"
        "  error: 0.0\n"
        "  no_issues: 1.0\n"
        "  recommendation: 0.9\n"
        "  warning: 0.6\n"
        "\n"
        "pass_threshold: 90\n",
        encoding="utf-8",
    )
    return config_file


def test_load_rules_success(temp_rules_file):
    """Тест успешной загрузки правил."""
    loader = RulesLoader(rules_path=str(temp_rules_file))
    rules = loader.load_rules()
    
    assert "Правила DoQA v1.10.0" in rules
    assert "Запрещены стоп-слова" in rules
    assert len(rules) > 0


def test_load_rules_file_not_found():
    """Тест обработки отсутствующего файла."""
    loader = RulesLoader(rules_path="/nonexistent/rules.md")
    
    with pytest.raises(FileNotFoundError):
        loader.load_rules()


def test_load_rules_caching(temp_rules_file):
    """Тест кэширования правил."""
    loader = RulesLoader(rules_path=str(temp_rules_file))
    
    # Первая загрузка
    rules1 = loader.load_rules()
    
    # Вторая загрузка (должна быть из кэша)
    rules2 = loader.load_rules()
    
    assert rules1 == rules2
    assert loader._rules_cache is not None


def test_load_rules_force_reload(temp_rules_file):
    """Тест принудительной перезагрузки."""
    loader = RulesLoader(rules_path=str(temp_rules_file))
    
    # Первая загрузка
    rules1 = loader.load_rules()
    
    # Изменение файла
    temp_rules_file.write_text("Новые правила\n", encoding="utf-8")
    
    # Загрузка с force_reload
    rules2 = loader.load_rules(force_reload=True)
    
    assert rules1 != rules2
    assert "Новые правила" in rules2


def test_load_scoring_config(temp_scoring_config):
    """Тест загрузки конфигурации оценки."""
    loader = RulesLoader(scoring_config_path=str(temp_scoring_config))
    config = loader.load_scoring_config()
    
    assert "weights" in config
    assert "severity_coefficients" in config
    assert config["weights"]["title"] == 10
    assert config["pass_threshold"] == 90


def test_get_rules_version(temp_rules_file):
    """Тест получения версии правил."""
    loader = RulesLoader(rules_path=str(temp_rules_file))
    version = loader.get_rules_version()
    
    assert "v1.10.0" in version or "hash:" in version


def test_invalidate_cache(temp_rules_file):
    """Тест сброса кэша."""
    loader = RulesLoader(rules_path=str(temp_rules_file))
    
    # Загрузка правил
    loader.load_rules()
    assert loader._rules_cache is not None
    
    # Сброс кэша
    loader.invalidate_cache()
    assert loader._rules_cache is None
    assert loader._rules_hash is None
