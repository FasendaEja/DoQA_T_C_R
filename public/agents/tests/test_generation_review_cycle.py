"""Тесты для цикла генерации и ревью тест-кейсов."""

import pytest
from unittest.mock import Mock, MagicMock
from graph.generation_review_cycle import GenerationReviewCycleNode
from schemas import DoQATestCase, DoQAReview, ReviewIssue, ReviewSeverity, Checklist, ChecklistItem


@pytest.fixture
def mock_llm_client():
    """Создание мок LLM-клиента."""
    return Mock()


@pytest.fixture
def cycle_node(mock_llm_client):
    """Создание узла цикла."""
    return GenerationReviewCycleNode(
        llm_client=mock_llm_client,
        max_iterations=3,
        pass_threshold=90.0,
    )


@pytest.fixture
def sample_checklist():
    """Создание тестового чек-листа."""
    return Checklist(
        checklist_id="test_checklist",
        title="Тестовый чек-лист",
        items=[
            ChecklistItem(
                item_id="item_1",
                title="Проверка авторизации",
                category="positive",
                priority="high",
            ),
        ],
    )


@pytest.fixture
def good_test_case():
    """Создание хорошего тест-кейса."""
    return DoQATestCase(
        case_id="case_1",
        title="Авторизация с валидными данными",
        description="Проверка успешной авторизации",
        test_type="позитивный",
        preconditions="Пользователь зарегистрирован",
        steps=[
            {
                "number": 1,
                "action": "Ввести логин user@example.com",
                "expected_result": "Поле логина заполнено",
            },
            {
                "number": 2,
                "action": "Ввести пароль password123",
                "expected_result": "Поле пароля заполнено",
            },
            {
                "number": 3,
                "action": "Нажать кнопку 'Войти'",
                "expected_result": "Отображается главная страница",
            },
        ],
        priority="high",
    )


@pytest.fixture
def bad_test_case():
    """Создание плохого тест-кейса."""
    return DoQATestCase(
        case_id="case_2",
        title="Проверка авторизации",  # Стоп-слово
        description="",  # Пустое описание
        test_type="",
        steps=[
            {
                "number": 1,
                "action": "Ввести данные",  # Нечёткое действие
                "expected_result": "Всё корректно",  # Субъективный результат
            },
        ],
        priority="medium",
    )


def test_cycle_passes_on_first_iteration(cycle_node, good_test_case):
    """Тест прохождения цикла с первой итерации."""
    # Мок агентов
    cycle_node.authoring_agent = Mock()
    cycle_node.authoring_agent.run.return_value = {"test_case": good_test_case}
    
    cycle_node.review_agent = Mock()
    cycle_node.review_agent.run.return_value = {
        "review": DoQAReview(
            review_id="review_1",
            case_id="case_1",
            score=95.0,
            rating=5,
            status="ready-for-review",
            issues=[],
        )
    }
    
    # Создание состояния
    state = {
        "checklist": Checklist(
            checklist_id="test",
            title="Test",
            items=[ChecklistItem(item_id="1", title="Test", category="positive", priority="high")],
        ),
        "delta": None,
        "new_requirements": None,
    }
    
    # Запуск цикла
    result = cycle_node.run(state)
    
    # Проверка результата
    assert len(result["generated_cases"]) == 1
    assert len(result["reviewed_cases"]) == 1
    assert result["reviewed_cases"][0].score == 95.0
    assert result["reviewed_cases"][0].status == "ready-for-review"


def test_cycle_retries_on_low_score(cycle_node, bad_test_case, good_test_case):
    """Тест повторных итераций при низкой оценке."""
    # Мок агентов
    cycle_node.authoring_agent = Mock()
    cycle_node.authoring_agent.run.side_effect = [
        {"test_case": bad_test_case},  # Первая итерация - плохой кейс
        {"test_case": good_test_case},  # Вторая итерация - хороший кейс
    ]
    
    cycle_node.review_agent = Mock()
    cycle_node.review_agent.run.side_effect = [
        {
            "review": DoQAReview(
                review_id="review_1",
                case_id="case_2",
                score=60.0,
                rating=3,
                status="needs-changes",
                issues=[
                    ReviewIssue(
                        issue_id="issue_1",
                        severity=ReviewSeverity.ERROR,
                        category="test_case_defect",
                        area="title",
                        description="Стоп-слово в названии",
                    )
                ],
            )
        },
        {
            "review": DoQAReview(
                review_id="review_2",
                case_id="case_1",
                score=95.0,
                rating=5,
                status="ready-for-review",
                issues=[],
            )
        },
    ]
    
    # Создание состояния
    state = {
        "checklist": Checklist(
            checklist_id="test",
            title="Test",
            items=[ChecklistItem(item_id="1", title="Test", category="positive", priority="high")],
        ),
        "delta": None,
        "new_requirements": None,
    }
    
    # Запуск цикла
    result = cycle_node.run(state)
    
    # Проверка результата
    assert len(result["generated_cases"]) == 1
    assert len(result["reviewed_cases"]) == 1
    assert result["reviewed_cases"][0].score == 95.0
    assert result["reviewed_cases"][0].status == "ready-for-review"
    
    # Проверка что было 2 итерации
    assert cycle_node.authoring_agent.run.call_count == 2
    assert cycle_node.review_agent.run.call_count == 2


def test_cycle_fails_after_max_iterations(cycle_node, bad_test_case):
    """Тест неудачи после максимального количества итераций."""
    # Мок агентов - всегда возвращает плохой кейс
    cycle_node.authoring_agent = Mock()
    cycle_node.authoring_agent.run.return_value = {"test_case": bad_test_case}
    
    cycle_node.review_agent = Mock()
    cycle_node.review_agent.run.return_value = {
        "review": DoQAReview(
            review_id="review_1",
            case_id="case_2",
            score=50.0,
            rating=2,
            status="needs-changes",
            issues=[
                ReviewIssue(
                    issue_id="issue_1",
                    severity=ReviewSeverity.ERROR,
                    category="test_case_defect",
                    area="title",
                    description="Стоп-слово в названии",
                )
            ],
        )
    }
    
    # Создание состояния
    state = {
        "checklist": Checklist(
            checklist_id="test",
            title="Test",
            items=[ChecklistItem(item_id="1", title="Test", category="positive", priority="high")],
        ),
        "delta": None,
        "new_requirements": None,
    }
    
    # Запуск цикла
    result = cycle_node.run(state)
    
    # Проверка результата
    assert len(result["generated_cases"]) == 1
    assert len(result["reviewed_cases"]) == 1
    assert result["reviewed_cases"][0].score == 50.0
    assert result["reviewed_cases"][0].status == "needs-changes"
    
    # Проверка что было 3 итерации (максимум)
    assert cycle_node.authoring_agent.run.call_count == 3
    assert cycle_node.review_agent.run.call_count == 3


def test_cycle_fails_on_blocking_errors(cycle_node, bad_test_case):
    """Тест неудачи при блокирующих ошибках."""
    # Мок агентов
    cycle_node.authoring_agent = Mock()
    cycle_node.authoring_agent.run.return_value = {"test_case": bad_test_case}
    
    cycle_node.review_agent = Mock()
    cycle_node.review_agent.run.return_value = {
        "review": DoQAReview(
            review_id="review_1",
            case_id="case_2",
            score=95.0,  # Высокая оценка
            rating=5,
            status="needs-changes",  # Но есть блокирующие ошибки
            issues=[
                ReviewIssue(
                    issue_id="issue_1",
                    severity=ReviewSeverity.ERROR,  # Блокирующая ошибка
                    category="test_case_defect",
                    area="title",
                    description="Критическая ошибка",
                )
            ],
        )
    }
    
    # Создание состояния
    state = {
        "checklist": Checklist(
            checklist_id="test",
            title="Test",
            items=[ChecklistItem(item_id="1", title="Test", category="positive", priority="high")],
        ),
        "delta": None,
        "new_requirements": None,
    }
    
    # Запуск цикла
    result = cycle_node.run(state)
    
    # Проверка результата - должен провалиться из-за блокирующих ошибок
    assert result["reviewed_cases"][0].status == "needs-changes"
    assert cycle_node.authoring_agent.run.call_count == 3  # Все 3 итерации


def test_cycle_handles_empty_checklist(cycle_node):
    """Тест обработки пустого чек-листа."""
    # Создание состояния с пустым чек-листом
    state = {
        "checklist": Checklist(
            checklist_id="test",
            title="Test",
            items=[],
        ),
        "delta": None,
        "new_requirements": None,
    }
    
    # Запуск цикла
    result = cycle_node.run(state)
    
    # Проверка результата
    assert len(result["generated_cases"]) == 0
    assert len(result["reviewed_cases"]) == 0


def test_cycle_passes_context_to_next_iteration(cycle_node, bad_test_case, good_test_case):
    """Тест передачи контекста замечаний в следующую итерацию."""
    # Мок агентов
    cycle_node.authoring_agent = Mock()
    cycle_node.authoring_agent.run.side_effect = [
        {"test_case": bad_test_case},
        {"test_case": good_test_case},
    ]
    
    cycle_node.review_agent = Mock()
    cycle_node.review_agent.run.side_effect = [
        {
            "review": DoQAReview(
                review_id="review_1",
                case_id="case_2",
                score=60.0,
                rating=3,
                status="needs-changes",
                issues=[
                    ReviewIssue(
                        issue_id="issue_1",
                        severity=ReviewSeverity.ERROR,
                        category="test_case_defect",
                        area="title",
                        description="Стоп-слово в названии",
                        recommendation="Убрать слово 'Проверка'",
                    )
                ],
            )
        },
        {
            "review": DoQAReview(
                review_id="review_2",
                case_id="case_1",
                score=95.0,
                rating=5,
                status="ready-for-review",
                issues=[],
            )
        },
    ]
    
    # Создание состояния
    state = {
        "checklist": Checklist(
            checklist_id="test",
            title="Test",
            items=[ChecklistItem(item_id="1", title="Test", category="positive", priority="high")],
        ),
        "delta": None,
        "new_requirements": None,
    }
    
    # Запуск цикла
    result = cycle_node.run(state)
    
    # Проверка что второй вызов authoring_agent получил контекст с замечаниями
    assert cycle_node.authoring_agent.run.call_count == 2
    second_call_context = cycle_node.authoring_agent.run.call_args_list[1][1]["context"]
    assert "ЗАМЕЧАНИЯ ОТ ПРЕДЫДУЩЕЙ ИТЕРАЦИИ" in second_call_context
    assert "Стоп-слово в названии" in second_call_context
