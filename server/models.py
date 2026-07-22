"""
SQLModel data models for the knowledge graph, mastery, and study records.
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


# ──────────────────────────────────────────────
# Knowledge Graph Models
# ──────────────────────────────────────────────

class KnowledgeNode(SQLModel, table=True):
    """A single knowledge point in the graph / tree."""
    __tablename__ = "knowledge_nodes"

    id: str = Field(primary_key=True, max_length=64)
    name: str = Field(max_length=128)
    description: str = Field(default="", max_length=512)
    category: str = Field(default="", max_length=64, index=True)
    importance: int = Field(default=5, ge=1, le=10)

    # Tree structure
    parent_id: Optional[str] = Field(
        default=None, foreign_key="knowledge_nodes.id", max_length=64, index=True
    )
    depth: int = Field(default=0, ge=0)
    sort_order: int = Field(default=0)

    created_at: datetime = Field(default_factory=datetime.utcnow)


class KnowledgeEdge(SQLModel, table=True):
    """A directed edge between two knowledge nodes (graph semantics)."""
    __tablename__ = "knowledge_edges"

    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: str = Field(foreign_key="knowledge_nodes.id", max_length=64, index=True)
    target_id: str = Field(foreign_key="knowledge_nodes.id", max_length=64, index=True)
    relation_type: str = Field(default="prerequisite", max_length=32)
    weight: float = Field(default=0.5, ge=0.0, le=1.0)


# ──────────────────────────────────────────────
# User Learning Models
# ──────────────────────────────────────────────

class UserMastery(SQLModel, table=True):
    """Cached mastery score per user per node."""
    __tablename__ = "user_mastery"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=64, index=True)
    node_id: str = Field(foreign_key="knowledge_nodes.id", max_length=64, index=True)
    mastery: float = Field(default=0.0, ge=0.0, le=100.0)
    last_study: Optional[datetime] = Field(default=None)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class StudyRecord(SQLModel, table=True):
    """A single study session record."""
    __tablename__ = "study_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=64, index=True)
    node_id: str = Field(foreign_key="knowledge_nodes.id", max_length=64, index=True)
    duration: int = Field(default=0, ge=0)  # seconds
    behavior: str = Field(default="learn", max_length=32)  # learn|practice|review|debug
    score: float = Field(default=0.0, ge=0.0, le=100.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ──────────────────────────────────────────────
# API Response Schemas (not DB tables)
# ──────────────────────────────────────────────

class TreeNodeResponse(SQLModel):
    """A knowledge node with its children for tree rendering."""
    id: str
    name: str
    description: str
    category: str
    importance: int
    parent_id: Optional[str] = None
    depth: int = 0
    sort_order: int = 0
    children: List["TreeNodeResponse"] = []

    class Config:
        from_attributes = True


class GraphResponse(SQLModel):
    """Full graph data for the frontend."""
    tree: List[TreeNodeResponse]
    edges: List["EdgeResponse"]


class EdgeResponse(SQLModel):
    """An edge in the API response."""
    source_id: str
    target_id: str
    relation_type: str
    weight: float


class SubgraphResponse(SQLModel):
    """A subgraph centered on a specific node."""
    center: TreeNodeResponse
    nodes: List[TreeNodeResponse]
    edges: List[EdgeResponse]
    mastery: dict = {}
