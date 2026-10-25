"""Агент для формирования mind-map доработки."""

from __future__ import annotations

import logging
from typing import Any

from .base_agent import BaseAgent
from schemas import RequirementDelta, AnalysisReport, MindMap, MindMapNode

logger = logging.getLogger(__name__)


class MindMapAgent(BaseAgent):
    """
    Агент для формирования mind-map доработки.
    
    Функции:
    - Формирование структуры mind-map
    - Связывание узлов с дельтой
    - Генерация Markdown и Mermaid представлений
    """

    def run(
        self,
        delta: RequirementDelta | None = None,
        analysis: AnalysisReport | None = None,
        requirements_text: str = "",
        **kwargs,
    ) -> dict[str, Any]:
        """
        Формирование mind-map.
        
        Args:
            delta: Дельта требований
            analysis: Отчёт анализа
            requirements_text: Текст требований
            
        Returns:
            Словарь с MindMap и rationale
        """
        self.log_start(
            has_delta=delta is not None,
            has_analysis=analysis is not None,
        )

        try:
            # Подготовка информации
            delta_info = self._format_delta(delta) if delta else ""
            analysis_info = self._format_analysis(analysis) if analysis else ""

            # Построение промпта
            prompt = self.prompt_builder.build_mindmap_prompt(
                requirements=requirements_text,
                delta_info=delta_info,
                analysis_info=analysis_info,
            )

            # Получение ответа от LLM
            system_prompt = (
                "Ты — эксперт по структурированию информации. "
                "Формируй mind-map доработки на основе требований и изменений. "
                "Отвечай ТОЛЬКО валидным JSON."
            )

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]

            response = self.llm_client.chat_json(
                messages=messages,
                temperature=self.temperature,
            )

            # Извлечение узлов
            nodes_data = response.get("nodes", [])
            nodes = []

            for node_data in nodes_data:
                node = MindMapNode(
                    node_id=node_data.get("node_id", f"node_{len(nodes)}"),
                    title=node_data.get("title", ""),
                    description=node_data.get("description", ""),
                    node_type=node_data.get("node_type", "area"),
                    parent_id=node_data.get("parent_id"),
                    children=[],
                    delta_id=node_data.get("delta_id", ""),
                    status=node_data.get("status", "unchanged"),
                )
                nodes.append(node)

            # Построение связей parent-child
            for node in nodes:
                if node.parent_id:
                    parent = next((n for n in nodes if n.node_id == node.parent_id), None)
                    if parent:
                        parent.children.append(node.node_id)

            # Определение корневого узла
            root_node_id = nodes[0].node_id if nodes else ""

            # Генерация Markdown
            markdown = self._generate_markdown(nodes, root_node_id)

            # Генерация Mermaid
            mermaid = self._generate_mermaid(nodes)

            # Создание mind-map
            import uuid

            mindmap = MindMap(
                mindmap_id=str(uuid.uuid4()),
                title=response.get("title", "Mind-map доработки"),
                root_node_id=root_node_id,
                nodes=nodes,
                markdown=markdown,
                mermaid=mermaid,
            )

            # Генерация rationale
            rationale = self.generate_rationale(
                summary=f"Mind-map сформирован: {len(nodes)} узлов",
                used_sources=[
                    f"delta:{delta.delta_id}" if delta else "requirements",
                ],
                applied_rules=["Структурирование по областям", "Связывание с дельтой"],
                confidence="high" if len(nodes) > 0 else "low",
            )

            result = {
                "mindmap": mindmap,
                "nodes_count": len(nodes),
                "markdown": markdown,
                "mermaid": mermaid,
                "rationale": rationale,
            }

            self.log_finish(result)
            return result

        except Exception as e:
            self.log_error(e)
            raise

    def _format_delta(self, delta: RequirementDelta) -> str:
        """Форматирование дельты в текст."""
        lines = []
        for item in delta.items:
            lines.append(f"- [{item.change_type.value}] {item.title}: {item.explanation}")
        return "\n".join(lines)

    def _format_analysis(self, analysis: AnalysisReport) -> str:
        """Форматирование анализа в текст."""
        lines = []
        if analysis.risks:
            lines.append("Риски:")
            for risk in analysis.risks:
                lines.append(f"- {risk}")
        if analysis.missing_scenarios:
            lines.append("\nОтсутствующие сценарии:")
            for scenario in analysis.missing_scenarios:
                lines.append(f"- {scenario}")
        return "\n".join(lines)

    def _generate_markdown(self, nodes: list[MindMapNode], root_id: str) -> str:
        """Генерация Markdown-представления."""
        lines = []
        node_map = {n.node_id: n for n in nodes}

        def render_node(node_id: str, level: int = 0):
            node = node_map.get(node_id)
            if not node:
                return
            indent = "  " * level
            prefix = "- " if level > 0 else "# "
            lines.append(f"{indent}{prefix}{node.title}")
            if node.description and level > 0:
                lines.append(f"{indent}  > {node.description}")
            for child_id in node.children:
                render_node(child_id, level + 1)

        render_node(root_id)
        return "\n".join(lines)

    def _generate_mermaid(self, nodes: list[MindMapNode]) -> str:
        """Генерация Mermaid-представления."""
        lines = ["graph TD"]
        node_map = {n.node_id: n for n in nodes}

        for node in nodes:
            label = node.title.replace('"', "'")[:30]
            lines.append(f'    {node.node_id}["{label}"]')
            for child_id in node.children:
                lines.append(f"    {node.node_id} --> {child_id}")

        return "\n".join(lines)
