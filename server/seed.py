"""
Seed the database from public/data/python-knowledge.json.
Automatically infers tree parent_id and depth from the prerequisite graph.
"""
import json
import sys
from pathlib import Path
from collections import defaultdict, deque

from sqlmodel import Session, select
from database import engine, create_db_and_tables
from models import KnowledgeNode, KnowledgeEdge


def load_json() -> dict:
    json_path = Path(__file__).parent.parent / "public" / "data" / "python-knowledge.json"
    if not json_path.exists():
        print(f"ERROR: {json_path} not found.")
        sys.exit(1)
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def infer_tree(nodes_data: list, edges_data: list):
    """
    Infer a tree structure from the prerequisite DAG.
    Each node's primary parent = its first 'hard' prerequisite (fallback: first prerequisite).
    Returns a dict: { node_id: { parent_id, depth, sort_order } }
    """
    # Build prerequisite map: target -> list of sources
    prereqs = defaultdict(list)
    for edge in edges_data:
        prereqs[edge["target"]].append(
            (edge["source"], edge.get("strength", "soft"))
        )

    node_ids = {n["id"] for n in nodes_data}
    tree_info = {}

    # Find root nodes (no prerequisites at all)
    roots = [n["id"] for n in nodes_data if not n.get("prerequisites")]

    # BFS to assign parent + depth
    visited = set()
    queue = deque()

    for root_id in roots:
        tree_info[root_id] = {"parent_id": None, "depth": 0, "sort_order": 0}
        visited.add(root_id)
        queue.append(root_id)

    # Build children map from edges (source -> targets)
    children_map = defaultdict(list)
    for edge in edges_data:
        children_map[edge["source"]].append(edge["target"])

    while queue:
        current = queue.popleft()
        current_depth = tree_info[current]["depth"]

        # Get children of current node
        child_targets = children_map[current]
        sort_idx = 0
        for child_id in child_targets:
            if child_id in visited:
                continue
            if child_id not in node_ids:
                continue

            # Check if this is the "primary" parent for the child
            # A child picks the first hard prerequisite it encounters in BFS order
            child_prereqs = prereqs.get(child_id, [])
            hard_prereqs = [p for p, s in child_prereqs if s == "hard"]
            primary_parent = hard_prereqs[0] if hard_prereqs else (
                child_prereqs[0][0] if child_prereqs else current
            )

            # Only claim this child if we are the primary parent
            if primary_parent == current:
                tree_info[child_id] = {
                    "parent_id": current,
                    "depth": current_depth + 1,
                    "sort_order": sort_idx,
                }
                sort_idx += 1
                visited.add(child_id)
                queue.append(child_id)

    # Handle any orphans (nodes not reached by BFS)
    for n in nodes_data:
        if n["id"] not in tree_info:
            # Attach to the first prerequisite that exists in tree_info
            prereq_list = n.get("prerequisites", [])
            parent = None
            for p in prereq_list:
                if p in tree_info:
                    parent = p
                    break
            depth = (tree_info[parent]["depth"] + 1) if parent else 0
            tree_info[n["id"]] = {
                "parent_id": parent,
                "depth": depth,
                "sort_order": 99,
            }

    return tree_info


def seed():
    """Main seed function."""
    print("Creating tables...")
    create_db_and_tables()

    data = load_json()
    nodes_data = data.get("nodes", [])
    edges_data = data.get("edges", [])

    print(f"Loaded {len(nodes_data)} nodes and {len(edges_data)} edges from JSON.")

    # Infer tree structure
    tree_info = infer_tree(nodes_data, edges_data)

    with Session(engine) as session:
        # Check if already seeded
        existing = session.exec(select(KnowledgeNode)).first()
        if existing:
            print("Database already seeded. Use --force to re-seed.")
            if "--force" not in sys.argv:
                return
            # Clear existing data
            print("Clearing existing data...")
            session.exec(select(KnowledgeEdge)).all()
            for edge in session.exec(select(KnowledgeEdge)).all():
                session.delete(edge)
            for node in session.exec(select(KnowledgeNode)).all():
                session.delete(node)
            session.commit()

        # Insert nodes
        for n in nodes_data:
            info = tree_info.get(n["id"], {"parent_id": None, "depth": 0, "sort_order": 0})
            node = KnowledgeNode(
                id=n["id"],
                name=n["name"],
                description=n.get("description", ""),
                category=n.get("category", ""),
                importance=n.get("importance", 5),
                parent_id=info["parent_id"],
                depth=info["depth"],
                sort_order=info["sort_order"],
            )
            session.add(node)

        session.commit()
        print(f"Inserted {len(nodes_data)} nodes.")

        # Insert edges (cross-links with weight)
        for edge in edges_data:
            # Skip edges to non-existent nodes
            source_exists = session.get(KnowledgeNode, edge["source"])
            target_exists = session.get(KnowledgeNode, edge["target"])
            if not source_exists or not target_exists:
                print(f"  Skipping edge {edge['source']} -> {edge['target']} (missing node)")
                continue

            weight = 1.0 if edge.get("strength") == "hard" else 0.5
            db_edge = KnowledgeEdge(
                source_id=edge["source"],
                target_id=edge["target"],
                relation_type=edge.get("relationType", "prerequisite"),
                weight=weight,
            )
            session.add(db_edge)

        session.commit()
        print(f"Inserted edges.")

    # Print tree for verification
    print("\nInferred tree structure:")
    print_tree(tree_info, nodes_data)


def print_tree(tree_info: dict, nodes_data: list):
    """Pretty-print the tree."""
    name_map = {n["id"]: n["name"] for n in nodes_data}
    children = defaultdict(list)
    roots = []
    for nid, info in tree_info.items():
        if info["parent_id"] is None:
            roots.append(nid)
        else:
            children[info["parent_id"]].append((nid, info["sort_order"]))

    def _print(nid, indent=0):
        name = name_map.get(nid, nid)
        depth = tree_info[nid]["depth"]
        prefix = "  " * indent + ("└─ " if indent > 0 else "")
        print(f"{prefix}{name} (depth={depth})")
        kids = sorted(children.get(nid, []), key=lambda x: x[1])
        for kid_id, _ in kids:
            _print(kid_id, indent + 1)

    for root in roots:
        _print(root)


if __name__ == "__main__":
    seed()
