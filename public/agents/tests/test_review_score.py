"""Тесты для сервиса оценки качества тест-кейсов."""

import pytest
from services.review_score_service import ReviewScoreService
from services.rules_loader import RulesLoader
from schemas import DoQATestCase, TestCaseStep, ReviewSeverity


@pytest.fixture
def rules_loader(tmp_path):
    """Создание загрузчика правил с временными файлами."""
    rules_file = tmp_path / "rules.md"
    rules_file.write_text("# Правила DoQA v1.10.0\n", encoding="utf-8")
    
    config_file = tmp_path / "scoring.yaml"
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
    
    return RulesLoader(
        rules_path=str(rules_file),
        scoring_config_path=str(config_file),
    )


@pytest.fixture
def review_service(rules_loader):
    """Создание сервиса ревью."""
    return ReviewScoreService(rules_loader=rules_loader)


def test_review_good_test_case(review_service):
    """Тест ревью хорошего тест-кейса."""
    test_case = DoQATestCase(
        case_id="test_1",
        title="Авторизация с валидными данными",
        description="Проверка успешной авторизации",
        test_type="позитивный",
        preconditions="Пользователь зарегистрирован",
        test_ "user@example.com / password123",
        steps=[
            TestCaseStep(
                number=1,
                action="Ввести логин user@example.com",
                expected_result="Поле логина заполнено",
                test_ "user@example.com",
            ),
            TestCaseStep(
                number=2,
                action="Ввести пароль password123",
                expected_result="Поле пароля заполнено",
                test_ "password123",
            ),
            TestCaseStep(
                number=3,
                action="Нажать кнопку 'Войти'",
                expected_result="Отображается главная страница",
                test_ "",
            ),
        ],
        priority="high",
        automation_status="Подлежит автоматизации",
    )
    
    review = review_service.review(test_case)
    
    assert review.score >= 90
    assert review.rating >= 4
    assert review.status == "ready-for-review"
    assert len(review.issues) == 0 or all(
        i.severity != ReviewSeverity.ERROR for i in review.issues
    )


def test_review_title_with_stop_word(review_service):
    """Тест обнаружения стоп-слова в названии."""
    test_case = DoQATestCase(
        case_id="test_2",
        title="Проверка авторизации",
        description="Тест авторизации",
        test_type="позитивный",
        steps=[
            TestCaseStep(
                number=1,
                action="Ввести данные",
                expected_result="Данные введены",
            ),
        ],
    )
    
    review = review_service.review(test_case)
    
    # Должно быть замечание о стоп-слове
    title_issues = [i for i in review.issues if i.area == "title"]
    assert len(title_issues) > 0
    assert any("Проверка" in i.description or "стоп-слов" in i.description.lower() 
               for i in title_issues)


def test_review_empty_description(review_service):
    """Тест обнаружения пустого описания."""
    test_case = DoQATestCase(
        case_id="test_3",
        title="Авторизация",
        description="",  # Пустое описание
        test_type="",
        steps=[
            TestCaseStep(
                number=1,
                action="Ввести данные",
                expected_result="Данные введены",
            ),
        ],
    )
    
    review = review_service.review(test_case)
    
    # Должно быть замечание о пустом описании
    desc_issues = [i for i in review.issues if i.area == "description"]
    assert len(desc_issues) > 0


def test_review_forbidden_stub(review_service):
    """Тест обнаружения запрещённой заглушки."""
    test_case = DoQATestCase(
        case_id="test_4",
        title="Авторизация",
        description="Тест авторизации",
        test_type="позитивный",
        steps=[
            TestCaseStep(
                number=1,
                action="Ввести логин",
                expected_result="Логин введён",
                test_ "любое значение",  # Запрещённая заглушка
            ),
        ],
    )
    
    review = review_service.review(test_case)
    
    # Должно быть замечание о заглушке
    data_issues = [i for i in review.issues if i.area == "test_
    assert len(data_issues) > 0
    assert any("заглушка" in i.description.lower() or "любое значение" in i.description 
               for i in data_issues)


def test_review_branching(review_service):
    """Тест обнаружения ветвления."""
    test_case = DoQATestCase(
        case_id="test_5",
        title="Авторизация",
        description="Тест авторизации",
        test_type="позитивный",
        steps=[
            TestCaseStep(
                number=1,
                action="Если появится окно, ввести данные",  # Ветвление
                expected_result="Данные введены",
            ),
        ],
    )
    
    review = review_service.review(test_case)
    
    # Должно быть замечание о ветвлении
    step_issues = [i for i in review.issues if i.area == "step_instructions"]
    assert len(step_issues) > 0
    assert any("ветвление" in i.description.lower() or "если" in i.description.lower() 
               for i in step_issues)


def test_review_subjective_expected_result(review_service):
    """Тест обнаружения субъективного ожидаемого результата."""
    test_case = DoQATestCase(
        case_id="test_6",
        title="Авторизация",
        description="Тест авторизации",
        test_type="позитивный",
        steps=[
            TestCaseStep(
                number=1,
                action="Ввести данные",
                expected_result="Всё корректно",  # Субъективная формулировка
            ),
        ],
    )
    
    review = review_service.review(test_case)
    
    # Должно быть замечание о субъективной формулировке
    expected_issues = [i for i in review.issues if i.area == "expected_results"]
    assert len(expected_issues) > 0
    assert any("субъектив" in i.description.lower() or "всё корректно" in i.description.lower() 
               for i in expected_issues)


def test_review_score_calculation(review_service):
    """Тест расчёта оценки."""
    test_case = DoQATestCase(
        case_id="test_7",
        title="Тест",
        description="",
        test_type="",
        steps=[],
    )
    
    review = review_service.review(test_case)
    
    # Оценка должна быть низкой из-за множества проблем
    assert review.score < 90
    assert review.rating <= 3
    assert review.status == "needs-changes"
