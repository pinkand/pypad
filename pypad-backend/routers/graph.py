from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional

from database import get_session
from models import (
    KnowledgeNode,
    KnowledgeEdge,
    TreeNodeResponse,
    GraphResponse,
    EdgeResponse
)

router = APIRouter(prefix="/api/graph", tags=["Knowledge Graph"])


def _build_tree(nodes: List[KnowledgeNode], parent_id: Optional[str] = None) -> List[TreeNodeResponse]:
    """Recursively build a tree of TreeNodeResponse from a flat list of nodes."""
    children = []
    # Find all nodes that have the given parent_id
    for node in sorted([n for n in nodes if n.parent_id == parent_id], key=lambda x: x.sort_order):
        child_resp = TreeNodeResponse(
            id=node.id, name=node.name, description=node.description or "",
            category=node.category or "", importance=node.importance,
            parent_id=node.parent_id, depth=node.depth, sort_order=node.sort_order,
        )
        # Recursively fetch children
        child_resp.children = _build_tree(nodes, node.id)
        children.append(child_resp)
    return children


@router.get("/tree", response_model=GraphResponse)
def get_graph_tree(session: Session = Depends(get_session)):
    """
    Returns the complete knowledge graph.
    The nodes are returned as a nested tree structure (for 3D layout).
    The edges are returned as a flat list (for cross-links and weights).
    """
    # Fetch all nodes and edges
    all_nodes = session.exec(select(KnowledgeNode)).all()
    all_edges = session.exec(select(KnowledgeEdge)).all()

    # Build nested tree starting from root nodes (parent_id is None)
    tree = _build_tree(list(all_nodes), parent_id=None)

    # Map edges to API response format
    edges_resp = [
        EdgeResponse(
            source_id=e.source_id,
            target_id=e.target_id,
            relation_type=e.relation_type,
            weight=e.weight
        ) for e in all_edges
    ]

    return GraphResponse(tree=tree, edges=edges_resp)


@router.get("/categories")
def get_categories(session: Session = Depends(get_session)):
    """Returns a list of unique categories."""
    statement = select(KnowledgeNode.category).distinct()
    categories = session.exec(statement).all()
    # Filter out empty strings if any
    return {"categories": [c for c in categories if c]}
