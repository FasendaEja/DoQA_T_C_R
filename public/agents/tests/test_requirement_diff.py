"""Тесты для сервиса дельты требований."""

import pytest
from services.requirement_diff_service import RequirementDiffService
from schemas import RequirementVersion, RequirementFragment, ChangeType


@pytest.fixture
def diff_service():
    """Создание сервиса дельты."""
    return RequirementDiffService()


@pytest.fixture
def old_version():
    """Создание старой версии требований."""
    return RequirementVersion(
        version_id="old_v1",
        label="v1.0",
        source="test",
        fragments=[
            RequirementFragment(
                fragment_id="frag_1",
                title="Авторизация",
                text="Пользователь может войти в систему",
                section_path=["Функции"],
                order=0,
            ),
            RequirementFragment(
                fragment_id="frag_2",
                title="Регистрация",
                text="Новый пользователь может зарегистрироваться",
                section_path=["Функции"],
                order=1,
            ),
        ],
        raw_text="Пользователь может войти в систему\nНовый пользователь может зарегистрироваться",
    )


@pytest.fixture
def new_version():
    """Создание новой версии требований."""
    return RequirementVersion(
        version_id="new_v1",
        label="v2.0",
        source="test",
        fragments=[
            RequirementFragment(
                fragment_id="frag_1",
                title="Авторизация",
                text="Пользователь может войти в систему с помощью email и пароля",
                section_path=["Функции"],
                order=0,
            ),
            RequirementFragment(
                fragment_id="frag_2",
                title="Регистрация",
                text="Новый пользователь может зарегистрироваться",
                section_path=["Функции"],
                order=1,
            ),
            RequirementFragment(
                fragment_id="frag_3",
                title="Восстановление пароля",
                text="Пользователь может восстановить забытый пароль",
                section_path=["Функции"],
                order=2,
            ),
        ],
        raw_text="Пользователь может войти в систему с помощью email и пароля\nНовый пользователь может зарегистрироваться\nПользователь может восстановить забытый пароль",
    )


def test_compute_delta_added(diff_service, old_version, new_version):
    """Тест обнаружения добавленных требований."""
    delta = diff_service.compute_delta(old_version, new_version)
    
    # Должен быть добавлен frag_3
    added = [item for item in delta.items if item.change_type == ChangeType.ADDED]
    assert len(added) > 0
    assert any("Восстановление пароля" in item.title for item in added)


def test_compute_delta_changed(diff_service, old_version, new_version):
    """Тест обнаружения изменённых требований."""
    delta = diff_service.compute_delta(old_version, new_version)
    
    # Должен быть изменён frag_1
    changed = [item for item in delta.items if item.change_type == ChangeType.CHANGED]
    assert len(changed) > 0
    assert any("Авторизация" in item.title for item in changed)


def test_compute_delta_unchanged(diff_service, old_version, new_version):
    """Тест обнаружения неизменённых требований."""
    delta = diff_service.compute_delta(old_version, new_version)
    
    # frag_2 не должен измениться
    unchanged = [item for item in delta.items if item.change_type == ChangeType.UNCHANGED]
    assert len(unchanged) > 0
    assert any("Регистрация" in item.title for item in unchanged)


def test_compute_delta_removed(diff_service):
    """Тест обнаружения удалённых требований."""
    old_version = RequirementVersion(
        version_id="old_v2",
        label="v1.0",
        source="test",
        fragments=[
            RequirementFragment(
                fragment_id="frag_1",
                title="Функция 1",
                text="Текст 1",
                order=0,
            ),
            RequirementFragment(
                fragment_id="frag_2",
                title="Функция 2",
                text="Текст 2",
                order=1,
            ),
        ],
    )
    
    new_version = RequirementVersion(
        version_id="new_v2",
        label="v2.0",
        source="test",
        fragments=[
            RequirementFragment(
                fragment_id="frag_1",
                title="Функция 1",
                text="Текст 1",
                order=0,
            ),
        ],
    )
    
    delta = diff_service.compute_delta(old_version, new_version)
    
    # Должен быть удалён frag_2
    removed = [item for item in delta.items if item.change_type == ChangeType.REMOVED]
    assert len(removed) > 0
    assert any("Функция 2" in item.title for item in removed)


def test_compute_delta_format_only(diff_service):
    """Тест определения форматных изменений."""
    old_version = RequirementVersion(
        version_id="old_v3",
        label="v1.0",
        source="test",
        fragments=[
            RequirementFragment(
                fragment_id="frag_1",
                title="Тест",
                text="Текст с пробелами",
                order=0,
            ),
        ],
    )
    
    new_version = RequirementVersion(
        version_id="new_v3",
        label="v2.0",
        source="test",
        fragments=[
            RequirementFragment(
                fragment_id="frag_1",
                title="Тест",
                text="Текст  с  пробелами",  # Только форматирование
                order=0,
            ),
        ],
    )
    
    delta = diff_service.compute_delta(old_version, new_version)
    
    # Должно быть определено как форматное изменение
    changed = [item for item in delta.items if item.change_type == ChangeType.CHANGED]
    if changed:
        assert any(item.is_format_only for item in changed)


def test_compute_delta_summary(diff_service, old_version, new_version):
    """Тест генерации резюме дельты."""
    delta = diff_service.compute_delta(old_version, new_version)
    
    assert delta.summary
    assert len(delta.summary) > 0


def test_compute_delta_ids(diff_service, old_version, new_version):
    """Тест генерации уникальных ID."""
    delta = diff_service.compute_delta(old_version, new_version)
    
    # Все delta_id должны быть уникальными
    delta_ids = [item.delta_id for item in delta.items]
    assert len(delta_ids) == len(set(delta_ids))
