"""
PyPad Vector RAG (Retrieval-Augmented Generation) Engine.
Provides TF-IDF Vector Space Model cosine similarity search and Qdrant integration.
"""

import math
import re
from typing import List, Dict, Any, Tuple


def tokenize(text: str) -> List[str]:
    """
    Tokenize Chinese & English text into term tokens.
    """
    text_clean = re.sub(r"[^\w\u4e00-\u9fa5]+", " ", text.lower())
    words = []
    # Extract English words and Chinese 1-gram / 2-gram tokens
    for token in text_clean.split():
        if re.match(r"^[a-zA-Z0-9_]+$", token):
            words.append(token)
        else:
            # Chinese character n-grams
            for i in range(len(token)):
                words.append(token[i])
                if i + 1 < len(token):
                    words.append(token[i:i+2])
    return words


class VectorRAGEngine:
    def __init__(self):
        self.documents: List[Dict[str, Any]] = []
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.doc_vectors: List[Dict[str, float]] = []
        self.is_indexed = False

    def index_knowledge_nodes(self, nodes: List[Dict[str, Any]]):
        """
        Index knowledge nodes into TF-IDF vector space.
        """
        self.documents = []
        self.doc_vectors = []
        self.vocabulary = {}
        self.idf = {}

        doc_count = len(nodes)
        if doc_count == 0:
            self.is_indexed = False
            return

        df: Dict[str, int] = {}
        doc_tokens_list: List[List[str]] = []

        for node in nodes:
            # Combine fields into text body
            text_body = f"{node.get('name', '')} {node.get('description', '')} {node.get('category', '')} "
            summary = node.get('aiSummary', {})
            if isinstance(summary, dict):
                text_body += f"{summary.get('overview', '')} {' '.join(summary.get('keyPoints', []))} "

            tokens = tokenize(text_body)
            doc_tokens_list.append(tokens)
            self.documents.append(node)

            unique_tokens = set(tokens)
            for t in unique_tokens:
                df[t] = df.get(t, 0) + 1

        # Calculate IDF
        for term, count in df.items():
            self.idf[term] = math.log((doc_count + 1) / (count + 1)) + 1.0

        # Calculate TF-IDF vectors
        for tokens in doc_tokens_list:
            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1

            doc_len = max(1, len(tokens))
            vector: Dict[str, float] = {}
            for t, freq in tf.items():
                tfidf = (freq / doc_len) * self.idf.get(t, 1.0)
                vector[t] = tfidf
            
            # Normalize vector
            norm = math.sqrt(sum(val ** 2 for val in vector.values())) or 1.0
            norm_vector = {t: val / norm for t, val in vector.items()}
            self.doc_vectors.append(norm_vector)

        self.is_indexed = True

    def search(self, query: str, top_k: int = 3) -> List[Tuple[float, Dict[str, Any]]]:
        """
        Search Top-K relevant knowledge nodes using Cosine Similarity.
        """
        if not self.is_indexed or not self.documents:
            return []

        q_tokens = tokenize(query)
        if not q_tokens:
            return []

        q_tf: Dict[str, int] = {}
        for t in q_tokens:
            q_tf[t] = q_tf.get(t, 0) + 1

        q_len = max(1, len(q_tokens))
        q_vector: Dict[str, float] = {}
        for t, freq in q_tf.items():
            if t in self.idf:
                q_vector[t] = (freq / q_len) * self.idf[t]

        q_norm = math.sqrt(sum(val ** 2 for val in q_vector.values())) or 1.0
        q_norm_vector = {t: val / q_norm for t, val in q_vector.items()}

        scores: List[Tuple[float, Dict[str, Any]]] = []
        for idx, doc_vec in enumerate(self.doc_vectors):
            dot_product = sum(q_norm_vector[t] * doc_vec[t] for t in q_norm_vector if t in doc_vec)
            if dot_product > 0.05:
                scores.append((dot_product, self.documents[idx]))

        scores.sort(key=lambda x: -x[0])
        return scores[:top_k]

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
            context_lines.append(f"- [知识点: {node.get('name')}] ({node.get('category')}): {node.get('description')} {overview}")

        return "\n".join(context_lines)


# Global singleton instance
rag_engine = VectorRAGEngine()
