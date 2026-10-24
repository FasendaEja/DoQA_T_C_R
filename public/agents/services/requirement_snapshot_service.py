"""Сервис снимков требований."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from parsers import ParsedDocument, parse_file, parse_text
from schemas import RequirementFragment, RequirementVersion

logger = logging.getLogger(__name__)


class RequirementSnapshotService:
    """
    Сервис для создания снимков (версий) требований из различных источников.
    """

    def __init__(self, workspace_dir: str = "./workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

    def create_from_text(
        self,
        text: str,
        label: str = "new",
        source: str = "text",
        is_base: bool = False,
    ) -> RequirementVersion:
        """
        Создание снимка требований из текста.

        Args:
            text: Текст требований
            label: Метка версии
            source: Источник
            is_base: Это базовая (старая) версия

        Returns:
            RequirementVersion
        """
        parsed = parse_text(text, format="txt", source=source)

        if parsed.errors:
            logger.warning(f"Ошибки при парсинге текста: {parsed.errors}")

        fragments = self._parsed_to_fragments(parsed)

        version = RequirementVersion(
            version_id=str(uuid.uuid4()),
            label=label,
            source=source,
            source_path="",
            created_at=datetime.now(),
            fragments=fragments,
            raw_text=text,
            is_base=is_base,
            metadata={"parser": "text", "size": len(text)},
        )

        self._save_snapshot(version)
        logger.info(f"Снимок требований создан: {version.label} ({len(fragments)} фрагментов)")

        return version

    def create_from_file(
        self,
        file_path: str | Path,
        label: Optional[str] = None,
        is_base: bool = False,
    ) -> RequirementVersion:
        """
        Создание снимка требований из файла.

        Args:
            file_path: Путь к файлу
            label: Метка версии (по умолчанию — имя файла)
            is_base: Это базовая (старая) версия

        Returns:
            RequirementVersion
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        parsed = parse_file(file_path)

        if parsed.errors:
            logger.warning(f"Ошибки при парсинге файла {file_path}: {parsed.errors}")

        fragments = self._parsed_to_fragments(parsed)

        version = RequirementVersion(
            version_id=str(uuid.uuid4()),
            label=label or file_path.stem,
            source="file",
            source_path=str(file_path),
            created_at=datetime.now(),
            fragments=fragments,
            raw_text=parsed.content,
            is_base=is_base,
            metadata={
                "parser": type(parsed).__name__,
                "filename": file_path.name,
                "size": len(parsed.content),
                **parsed.metadata,
            },
        )

        self._save_snapshot(version)
        logger.info(
            f"Снимок требований создан из файла: {file_path.name} "
            f"({len(fragments)} фрагментов)"
        )

        return version

    def create_from_folder(
        self,
        folder_path: str | Path,
        label: str = "folder",
        is_base: bool = False,
        recursive: bool = True,
        file_masks: Optional[list[str]] = None,
    ) -> RequirementVersion:
        """
        Создание снимка требований из папки с файлами.

        Args:
            folder_path: Путь к папке
            label: Метка версии
            is_base: Это базовая (старая) версия
            recursive: Рекурсивный обход
            file_masks: Маски файлов (например, ["*.md", "*.txt"])

        Returns:
            RequirementVersion с объединёнными фрагментами
        """
        folder_path = Path(folder_path)

        if not folder_path.exists():
            raise FileNotFoundError(f"Папка не найдена: {folder_path}")

        if not folder_path.is_dir():
            raise ValueError(f"Путь не является папкой: {folder_path}")

        # Определяем файлы для обработки
        if file_masks:
            files = []
            for mask in file_masks:
                if recursive:
                    files.extend(folder_path.rglob(mask))
                else:
                    files.extend(folder_path.glob(mask))
        else:
            files = list(folder_path.rglob("*")) if recursive else list(folder_path.glob("*"))
            files = [f for f in files if f.is_file()]

        files = sorted(files)

        if not files:
            raise ValueError(f"В папке {folder_path} не найдено файлов")

        # Парсим все файлы
        all_fragments = []
        all_content = []
        errors = []
        warnings = []

        for file_path in files:
            try:
                parsed = parse_file(file_path)

                if parsed.errors:
                    errors.extend([f"{file_path.name}: {e}" for e in parsed.errors])
                    continue

                if parsed.warnings:
                    warnings.extend([f"{file_path.name}: {w}" for w in parsed.warnings])

                # Добавляем префикс с именем файла
                for frag in parsed.fragments:
                    frag["source_file"] = file_path.name
                    all_fragments.append(frag)

                all_content.append(f"=== {file_path.name} ===\n{parsed.content}")

            except Exception as e:
                errors.append(f"{file_path.name}: {e}")
                logger.warning(f"Ошибка парсинга {file_path}: {e}")

        if errors:
            logger.warning(f"Ошибки при парсинге папки: {errors}")

        # Создаём объединённый снимок
        fragments = [
            RequirementFragment(
                fragment_id=f.get("fragment_id", f"frag_{i}"),
                title=f.get("title", ""),
                text=f.get("text", ""),
                section_path=f.get("section_path", []),
                order=i,
                meta={
                    "source_file": f.get("source_file", ""),
                    "type": f.get("type", "paragraph"),
                },
            )
            for i, f in enumerate(all_fragments)
        ]

        version = RequirementVersion(
            version_id=str(uuid.uuid4()),
            label=label,
            source="folder",
            source_path=str(folder_path),
            created_at=datetime.now(),
            fragments=fragments,
            raw_text="\n\n".join(all_content),
            is_base=is_base,
            metadata={
                "files_count": len(files),
                "fragments_count": len(fragments),
                "errors": errors,
                "warnings": warnings,
            },
        )

        self._save_snapshot(version)
        logger.info(
            f"Снимок требований создан из папки: {folder_path} "
            f"({len(files)} файлов, {len(fragments)} фрагментов)"
        )

        return version

    def _parsed_to_fragments(self, parsed: ParsedDocument) -> list[RequirementFragment]:
        """Преобразование ParsedDocument в список RequirementFragment."""
        fragments = []

        for i, frag in enumerate(parsed.fragments):
            fragments.append(
                RequirementFragment(
                    fragment_id=frag.get("fragment_id", f"frag_{i}"),
                    title=frag.get("title", ""),
                    text=frag.get("text", ""),
                    section_path=frag.get("section_path", []),
                    order=i,
                    meta={
                        "type": frag.get("type", "paragraph"),
                        "source": parsed.source,
                    },
                )
            )

        # Если парсер не вернул фрагментов, создаём один из всего текста
        if not fragments and parsed.content:
            fragments.append(
                RequirementFragment(
                    fragment_id="frag_0",
                    title="",
                    text=parsed.content,
                    section_path=[],
                    order=0,
                    meta={"type": "full_text", "source": parsed.source},
                )
            )

        return fragments

    def _save_snapshot(self, version: RequirementVersion):
        """Сохранение снимка в workspace."""
        snapshot_dir = self.workspace_dir / "snapshots"
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        snapshot_file = snapshot_dir / f"{version.version_id}.json"
        snapshot_file.write_text(
            version.model_dump_json(indent=2),
            encoding="utf-8",
        )

        logger.debug(f"Снимок сохранён: {snapshot_file}")
