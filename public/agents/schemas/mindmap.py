"""Схема mind-map."""

from __future__ import annotations

from pydantic import BaseModel, Field


class MindMapNode(BaseModel):
    """Узел mind-map."""

    node_id: str
    title: str
    description: str = Field(default="")
    node_type: str = Field(
        default="area",
        description="Тип: area, module, feature, risk, question",
    )
    parent_id: str | None = None
    children: list[str] = Field(default_factory=list)
    delta_id: str = Field(default="", description="Связанный delta_id")
    status: str = Field(
        default="unchanged",
        description="added, changed, removed, unchanged",
    )
    metadata: dict = Field(default_factory=dict)


class MindMap(BaseModel):
    """Mind-map доработки."""

    mindmap_id: str
    title: str
    root_node_id: str
    nodes: list[MindMapNode] = Field(default_factory=list)
    markdown: str = Field(default="", description="Markdown-представление")
    mermaid: str = Field(default="", description="Mermaid-представление")
