"""Тесты для stage gate."""

import pytest
from human.stage_gate import StageGate
from human.review_service import HumanReviewService
from schemas import StageState, StageStatus, HumanDecision


@pytest.fixture
def stage_gate():
    """Создание stage gate."""
    return StageGate()


@pytest.fixture
def sample_stage():
    """Создание тестового этапа."""
    return StageState(
        stage_id="test_stage",
        stage_name="Тестовый этап",
        status=StageStatus.WAITING_FOR_HUMAN,
        iteration=1,
    )


def test_can_proceed_approved(stage_gate, sample_stage):
    """Тест перехода при статусе APPROVED."""
    sample_stage.status = StageStatus.APPROVED
    assert stage_gate.can_proceed(sample_stage) is True


def test_can_proceed_waiting(stage_gate, sample_stage):
    """Тест перехода при статусе WAITING_FOR_HUMAN."""
    sample_stage.status = StageStatus.WAITING_FOR_HUMAN
    assert stage_gate.can_proceed(sample_stage) is False


def test_can_proceed_failed(stage_gate, sample_stage):
    """Тест перехода при статусе FAILED."""
    sample_stage.status = StageStatus.FAILED
    assert stage_gate.can_proceed(sample_stage) is False


def test_request_approval(stage_gate, sample_stage):
    """Тест запроса подтверждения."""
    review_id = stage_gate.request_approval(sample_stage)
    
    assert review_id is not None
    assert sample_stage.status == StageStatus.WAITING_FOR_HUMAN


def test_submit_approval_approve(stage_gate, sample_stage):
    """Тест подтверждения этапа."""
    review_id = stage_gate.request_approval(sample_stage)
    
    review, updated_stage = stage_gate.submit_approval(
        review_id=review_id,
        decision=HumanDecision.APPROVE,
        comments="Одобreno",
    )
    
    assert review.decision == HumanDecision.APPROVE
    assert updated_stage.status == StageStatus.APPROVED
    assert "Одобreno" in updated_stage.human_comments


def test_submit_approval_reject(stage_gate, sample_stage):
    """Тест отклонения этапа."""
    review_id = stage_gate.request_approval(sample_stage)
    
    review, updated_stage = stage_gate.submit_approval(
        review_id=review_id,
        decision=HumanDecision.REJECT,
        comments="Отклонено",
    )
    
    assert review.decision == HumanDecision.REJECT
    assert updated_stage.status == StageStatus.REJECTED


def test_submit_approval_rerun(stage_gate, sample_stage):
    """Тест повторного запуска этапа."""
    review_id = stage_gate.request_approval(sample_stage)
    initial_iteration = sample_stage.iteration
    
    review, updated_stage = stage_gate.submit_approval(
        review_id=review_id,
        decision=HumanDecision.RERUN,
        comments="Исправить",
    )
    
    assert review.decision == HumanDecision.RERUN
    assert updated_stage.status == StageStatus.NEEDS_RERUN
    assert updated_stage.iteration == initial_iteration + 1


def test_should_rerun(stage_gate, sample_stage):
    """Тест проверки необходимости повторного запуска."""
    sample_stage.status = StageStatus.NEEDS_RERUN
    assert stage_gate.should_rerun(sample_stage) is True
    
    sample_stage.status = StageStatus.APPROVED
    assert stage_gate.should_rerun(sample_stage) is False


def test_check_iteration_limit(stage_gate, sample_stage):
    """Тест проверки лимита итераций."""
    sample_stage.iteration = 1
    assert stage_gate.check_iteration_limit(sample_stage) is True
    
    # Превышение лимита
    sample_stage.iteration = 100
    assert stage_gate.check_iteration_limit(sample_stage) is False


def test_get_max_iterations(stage_gate):
    """Тест получения максимального количества итераций."""
    max_iter = stage_gate.get_max_iterations()
    assert max_iter > 0
    assert isinstance(max_iter, int)
