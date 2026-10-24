"""Тесты для DoQA адаптера в mock-режиме."""

import pytest
from integrations.doqa.doqa_api_adapter import DoQAAPIAdapter


@pytest.fixture
def mock_adapter():
    """Создание адаптера в mock-режиме."""
    return DoQAAPIAdapter(mode="mock")


@pytest.fixture
def dry_run_adapter():
    """Создание адаптера в dry-run режиме."""
    return DoQAAPIAdapter(mode="dry-run")


def test_mock_get_test_case(mock_adapter):
    """Тест получения тест-кейса в mock-режиме."""
    case = mock_adapter.get_test_case(case_id="123", space_id="456")
    
    assert case is not None
    assert case["id"] == "123"
    assert "title" in case
    assert "steps" in case


def test_mock_export_test_cases(mock_adapter):
    """Тест экспорта тест-кейсов в mock-режиме."""
    result = mock_adapter.export_test_cases(space_id="456")
    
    assert result is not None
    assert isinstance(result, bytes)


def test_mock_create_test_case(mock_adapter):
    """Тест создания тест-кейса в mock-режиме."""
    case_ {
        "title": "Новый кейс",
        "description": "Описание",
    }
    
    case_id = mock_adapter.create_test_case(case_data)
    
    assert case_id is not None
    assert isinstance(case_id, str)


def test_mock_update_test_case(mock_adapter):
    """Тест обновления тест-кейса в mock-режиме."""
    case_ {
        "title": "Обновлённый кейс",
    }
    
    success = mock_adapter.update_test_case(case_id="123", case_data=case_data)
    
    assert success is True


def test_mock_set_status(mock_adapter):
    """Тест установки статуса в mock-режиме."""
    success = mock_adapter.set_status(case_id="123", status="review")
    
    assert success is True


def test_mock_archive_test_case(mock_adapter):
    """Тест архивирования тест-кейса в mock-режиме."""
    success = mock_adapter.archive_test_case(case_id="123")
    
    assert success is True


def test_dry_run_get_test_case(dry_run_adapter):
    """Тест получения тест-кейса в dry-run режиме."""
    case = dry_run_adapter.get_test_case(case_id="123", space_id="456")
    
    # В dry-run режиме возвращается None
    assert case is None


def test_dry_run_export_test_cases(dry_run_adapter):
    """Тест экспорта тест-кейсов в dry-run режиме."""
    result = dry_run_adapter.export_test_cases(space_id="456")
    
    # В dry-run режиме возвращается None
    assert result is None


def test_dry_run_create_test_case(dry_run_adapter):
    """Тест создания тест-кейса в dry-run режиме."""
    case_ {"title": "Тест"}
    case_id = dry_run_adapter.create_test_case(case_data)
    
    # В dry-run режиме возвращается None
    assert case_id is None


def test_mock_mode_fallback():
    """Тест переключения в mock при отсутствии контракта."""
    # Создаём адаптер в real режиме без заполненного контракта
    adapter = DoQAAPIAdapter(mode="real")
    
    # Должен переключиться в mock
    assert adapter.mode == "mock"


def test_mock_test_case_structure(mock_adapter):
    """Тест структуры мок-данных тест-кейса."""
    case = mock_adapter.get_test_case(case_id="test", space_id="space")
    
    # Проверка обязательных полей
    assert "id" in case
    assert "title" in case
    assert "description" in case
    assert "steps" in case
    
    # Проверка структуры шагов
    assert isinstance(case["steps"], list)
    if case["steps"]:
        step = case["steps"][0]
        assert "number" in step
        assert "action" in step
        assert "expected_result" in step
