"""Сервис формирования mind-map."""

from __future__ import annotations

import logging
import uuid
from typing import Optional

from schemas import MindMap, MindMapNode, RequirementDelta, AnalysisReport

logger = logging.getLogger(__name__)


class MindMapService:
    """Сервис для формирования mind-map доработки."""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def generate(
        self,
        delta: Optional[RequirementDelta] = None,
        analysis: Optional[AnalysisReport] = None,
        title: str = "Mind-map доработки",
    ) -> MindMap:
        """
        Формирование mind-map доработки.

        Args:
            delta: Дельта требований
            analysis: Отчёт анализа требований
            title: Заголовок mind-map

        Returns:
            MindMap
        """
        logger.info("Формирование mind-map доработки")

        nodes = []
        root_id = f"node_{uuid.uuid4().hex[:8]}"

        # Корневой узел
        root = MindMapNode(
            node_id=root_id,
            title=title,
            description="Корневой узел mind-map",
            node_type="area",
            status="unchanged",
        )
        nodes.append(root)

        # Добавляем узлы из дельты
        if delta:
            for item in delta.items:
                node = MindMapNode(
                    node_id=f"node_{uuid.uuid4().hex[:8]}",
                    title=item.title,
                    description=item.explanation,
                    node_type="feature",
                    parent_id=root_id,
                    delta_id=item.delta_id,
                    status=item.change_type.value,
                )
                nodes.append(node)
                root.children.append(node.node_id)

        # Добавляем узлы из анализа (риски и вопросы)
        if analysis:
            if analysis.risks:
                risk_node = MindMapNode(
                    node_id=f"node_{uuid.uuid4().hex[:8]}",
                    title="Риски",
                    node_type="risk",
                    parent_id=root_id,
                    status="unchanged",
                )
                nodes.append(risk_node)
                root.children.append(risk_node.node_id)

                for risk in analysis.risks:
                    risk_item = MindMapNode(
                        node_id=f"node_{uuid.uuid4().hex[:8]}",
                        title=risk[:50],
                        description=risk,
                        node_type="risk",
                        parent_id=risk_node.node_id,
                        status="unchanged",
                    )
                    nodes.append(risk_item)
                    risk_node.children.append(risk_item.node_id)

        # Генерируем markdown и mermaid
        markdown = self._generate_markdown(nodes, root_id)
        mermaid = self._generate_mermaid(nodes)

        mindmap = MindMap(
            mindmap_id=str(uuid.uuid4()),
            title=title,
            root_node_id=root_id,
            nodes=nodes,
            markdown=markdown,
            mermaid=mermaid,
        )

        logger.info(f"Mind-map сформирован: {len(nodes)} узлов")
        return mindmap

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
