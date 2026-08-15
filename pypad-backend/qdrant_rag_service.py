"""
PyPad Qdrant-backed Vector RAG Engine.
Uses Qdrant local storage for persistence and fastembed for vector embeddings.
Falls back to in-memory TF-IDF if Qdrant is unavailable.
"""

import os
import math
import re
from typing import List, Dict, Any, Tuple, Optional

# Try importing qdrant and fastembed
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

# Import the TF-IDF fallback engine
from rag_service import VectorRAGEngine


# ── Text extraction helper ──────────────────────────────────────────────

def _extract_text(node: Dict[str, Any]) -> str:
    """Combine all text fields from a knowledge node into a single string."""
    parts = [
        node.get("name", ""),
        node.get("description", ""),
        node.get("category", ""),
    ]
    summary = node.get("aiSummary", {})
    if isinstance(summary, dict):
        parts.append(summary.get("overview", ""))
        parts.extend(summary.get("keyPoints", []))
    return " ".join(p for p in parts if p)


# ── Qdrant RAG Engine ──────────────────────────────────────────────────

class QdrantRAGEngine:
    """
    Persistent vector RAG engine backed by Qdrant local storage.
    Uses fastembed for embedding generation.
    """

    COLLECTION_NAME = "pypad_knowledge"
    EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"  # 384-dim, fast & lightweight
    VECTOR_DIM = 384

    def __init__(self, storage_path: str = "./qdrant_data"):
        self.storage_path = storage_path
        self.client: Optional[Any] = None
        self.documents: List[Dict[str, Any]] = []
        self.is_indexed = False
        self._embedder = None
        self._init_client()

    def _init_client(self):
        """Initialize Qdrant client with local storage."""
        if not QDRANT_AVAILABLE:
            return
        try:
            os.makedirs(self.storage_path, exist_ok=True)
            self.client = QdrantClient(path=self.storage_path)
            # Create collection if it doesn't exist
            collections = [c.name for c in self.client.get_collections().collections]
            if self.COLLECTION_NAME not in collections:
                self.client.create_collection(
                    collection_name=self.COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=self.VECTOR_DIM,
                        distance=Distance.COSINE,
                    ),
                )
            print(f"[QdrantRAG] Initialized local Qdrant at {self.storage_path}")
        except Exception as e:
            print(f"[QdrantRAG] Failed to initialize Qdrant: {e}")
            self.client = None

    def _get_embedder(self):
        """Lazy-load the fastembed model."""
        if self._embedder is None:
            try:
                from fastembed import TextEmbedding
                self._embedder = TextEmbedding(model_name=self.EMBEDDING_MODEL)
                print(f"[QdrantRAG] Loaded embedding model: {self.EMBEDDING_MODEL}")
            except Exception as e:
                print(f"[QdrantRAG] Failed to load fastembed: {e}")
        return self._embedder

    def _embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        embedder = self._get_embedder()
        if embedder is None:
            return []
        embeddings = list(embedder.embed(texts))
        return [e.tolist() for e in embeddings]

    def index_knowledge_nodes(self, nodes: List[Dict[str, Any]]):
        """
        Index knowledge nodes into Qdrant vector store.
        Falls back to TF-IDF engine if Qdrant is unavailable.
        """
        self.documents = nodes

        if self.client is None:
            print("[QdrantRAG] Qdrant unavailable, skipping vector index.")
            return

        try:
            # Clear existing collection data
            self.client.delete_collection(self.COLLECTION_NAME)
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.VECTOR_DIM,
                    distance=Distance.COSINE,
                ),
            )

            # Prepare texts and generate embeddings
            texts = [_extract_text(n) for n in nodes]
            if not texts:
                return

            embeddings = self._embed(texts)
            if not embeddings:
                print("[QdrantRAG] Embedding generation failed, skipping.")
                return

            # Upsert points into Qdrant
            points = []
            for idx, (node, vector) in enumerate(zip(nodes, embeddings)):
                # Store searchable metadata as payload
                payload = {
                    "name": node.get("name", ""),
                    "description": node.get("description", ""),
                    "category": node.get("category", ""),
                    "node_id": node.get("id", ""),
                    "importance": node.get("importance", 4),
                }
                summary = node.get("aiSummary", {})
                if isinstance(summary, dict):
                    payload["overview"] = summary.get("overview", "")

                points.append(PointStruct(
                    id=idx,
                    vector=vector,
                    payload=payload,
                ))

            # Batch upsert (Qdrant handles batching internally for local mode)
            self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=points,
            )

            self.is_indexed = True
            print(f"[QdrantRAG] Indexed {len(nodes)} knowledge nodes into Qdrant.")

        except Exception as e:
            print(f"[QdrantRAG] Indexing failed: {e}")
            self.is_indexed = False

    def search(self, query: str, top_k: int = 3) -> List[Tuple[float, Dict[str, Any]]]:
        """
        Search Top-K relevant knowledge nodes using vector similarity.
        """
        if not self.is_indexed or self.client is None:
            return []

        try:
            # Generate query embedding
            query_vectors = self._embed([query])
            if not query_vectors:
                return []

            # Search in Qdrant
            results = self.client.query_points(
                collection_name=self.COLLECTION_NAME,
                query=query_vectors[0],
                limit=top_k,
            )

            # Map results back to document nodes
            scored = []
            for hit in results.points:
                idx = hit.id
                score = hit.score
                if 0 <= idx < len(self.documents) and score > 0.05:
                    scored.append((score, self.documents[idx]))

            return scored

        except Exception as e:
            print(f"[QdrantRAG] Search failed: {e}")
            return []

    def get_rag_context_prompt(self, query: str, top_k: int = 3) -> str:
        """
        Returns structured RAG context prompt string for LLM system context.
        """
        results = self.search(query, top_k=top_k)
        if not results:
            return ""

        context_lines = ["【PyPad 向量检索知识库关联背景】："]
        for score, node in results:
            summary = node.get("aiSummary", {})
            overview = summary.get("overview", "") if isinstance(summary, dict) else ""
            context_lines.append(
                f"- [知识点: {node.get('name')}] ({node.get('category')}): "
                f"{node.get('description')} {overview}"
            )

        return "\n".join(context_lines)


# ── Composite RAG Engine (Qdrant + TF-IDF Fallback) ───────────────────

class CompositeRAGEngine:
    """
    Tries Qdrant first; falls back to in-memory TF-IDF if Qdrant is unavailable.
    This is the engine used by main.py.
    """

    def __init__(self, storage_path: str = "./qdrant_data"):
        self.qdrant_engine = QdrantRAGEngine(storage_path=storage_path)
        self.tfidf_engine = VectorRAGEngine()
        self.use_qdrant = self.qdrant_engine.client is not None

    def index_knowledge_nodes(self, nodes: List[Dict[str, Any]]):
        """Index into both engines; Qdrant for persistence, TF-IDF as fallback."""
        # Always index into TF-IDF (lightweight, instant)
        self.tfidf_engine.index_knowledge_nodes(nodes)

        # Try Qdrant indexing
        if self.use_qdrant:
            self.qdrant_engine.index_knowledge_nodes(nodes)
            if self.qdrant_engine.is_indexed:
                print(f"[RAG] Using Qdrant vector engine ({len(nodes)} nodes indexed)")
            else:
                print(f"[RAG] Qdrant indexing failed, using TF-IDF fallback ({len(nodes)} nodes)")
        else:
            print(f"[RAG] Using TF-IDF engine ({len(nodes)} nodes indexed)")

    def search(self, query: str, top_k: int = 3) -> List[Tuple[float, Dict[str, Any]]]:
        """Search with Qdrant first, fallback to TF-IDF."""
        if self.use_qdrant and self.qdrant_engine.is_indexed:
            results = self.qdrant_engine.search(query, top_k=top_k)
            if results:
                return results
        # Fallback
        return self.tfidf_engine.search(query, top_k=top_k)

    def get_rag_context_prompt(self, query: str, top_k: int = 3) -> str:
        """Get RAG context prompt using best available engine."""
        if self.use_qdrant and self.qdrant_engine.is_indexed:
            result = self.qdrant_engine.get_rag_context_prompt(query, top_k=top_k)
            if result:
                return result
        # Fallback
        return self.tfidf_engine.get_rag_context_prompt(query, top_k=top_k)


# Global singleton instance
rag_engine = CompositeRAGEngine()
