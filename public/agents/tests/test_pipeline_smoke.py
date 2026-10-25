"""Smoke-тест пайплайна."""

import pytest
from graph.state import PipelineState, create_initial_state
from graph.nodes import PipelineNodes
from graph.edges import PipelineEdges


@pytest.fixture
def initial_state():
    """Создание начального состояния."""
    return create_initial_state()


@pytest.fixture
def pipeline_nodes():
    """Создание узлов пайплайна."""
    # Используем None для llm_client, чтобы избежать реальных запросов
    return PipelineNodes(llm_client=None)


def test_create_initial_state():
    """Тест создания начального состояния."""
    state = create_initial_state()
    
    assert state["current_stage"] == "requirement_intake"
    assert state["iteration"] == 0
    assert state["errors"] == []
    assert state["new_requirements"] is None
    assert state["delta"] is None


def test_initial_state_structure():
    """Тест структуры начального состояния."""
    state = create_initial_state()
    
    # Проверка наличия всех необходимых полей
    required_fields = [
        "messages",
        "new_requirements",
        "old_requirements",
        "delta",
        "delta_approved",
        "analysis_report",
        "mindmap",
        "checklist",
        "doqa_context",
        "codebase_context",
        "impact",
        "new_cases",
        "updated_cases",
        "archived_cases",
        "generated_cases",
        "reviewed_cases",
        "structure_changes",
        "import_result",
        "stages",
        "rationales",
        "current_stage",
        "iteration",
        "errors",
        "warnings",
        "metadata",
    ]
    
    for field in required_fields:
        assert field in state, f"Отсутствует поле: {field}"


def test_route_after_requirement_intake_with_old():
    """Тест маршрутизации при наличии старой версии."""
    state = create_initial_state()
    state["old_requirements"] = {"version_id": "old"}
    state["new_requirements"] = {"version_id": "new"}
    
    next_stage = PipelineEdges.route_after_requirement_intake(state)
    
    assert next_stage == "requirement_diff"


def test_route_after_requirement_intake_without_old():
    """Тест маршрутизации без старой версии."""
    state = create_initial_state()
    state["new_requirements"] = {"version_id": "new"}
    
    next_stage = PipelineEdges.route_after_requirement_intake(state)
    
    assert next_stage == "requirement_analysis"


def test_route_after_requirement_intake_with_errors():
    """Тест маршрутизации при ошибках."""
    state = create_initial_state()
    state["errors"] = ["test error"]
    
    next_stage = PipelineEdges.route_after_requirement_intake(state)
    
    assert next_stage == "error"


def test_should_continue_normal():
    """Тест проверки продолжения в нормальном состоянии."""
    state = create_initial_state()
    state["current_stage"] = "requirement_intake"
    
    assert PipelineEdges.should_continue(state) is True


def test_should_continue_with_errors():
    """Тест проверки продолжения при ошибках."""
    state = create_initial_state()
    state["errors"] = ["test error"]
    
    assert PipelineEdges.should_continue(state) is False


def test_should_continue_completed():
    """Тест проверки продолжения при завершении."""
    state = create_initial_state()
    state["current_stage"] = "completed"
    
    assert PipelineEdges.should_continue(state) is False


def test_should_continue_max_iterations():
    """Тест проверки продолжения при превышении итераций."""
    state = create_initial_state()
    state["iteration"] = 100  # Превышение лимита
    
    assert PipelineEdges.should_continue(state) is False


def test_get_next_stage():
    """Тест получения следующего этапа."""
    assert PipelineEdges.get_next_stage("requirement_intake") == "requirement_diff"
    assert PipelineEdges.get_next_stage("requirement_diff") == "requirement_analysis"
    assert PipelineEdges.get_next_stage("doqa_export") == "completed"


def test_get_next_stage_unknown():
    """Тест получения следующего этапа для неизвестного этапа."""
    next_stage = PipelineEdges.get_next_stage("unknown_stage")
    assert next_stage == "error"


def test_state_is_typed_dict():
    """Тест что состояние является TypedDict."""
    state = create_initial_state()
    assert isinstance(state, dict)
    
    # Проверка типов некоторых полей
    assert isinstance(state["errors"], list)
    assert isinstance(state["warnings"], list)
    assert isinstance(state["stages"], dict)
