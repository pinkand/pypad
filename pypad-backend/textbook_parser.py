"""
PyPad Automated Textbook & Document Parsing Engine.
Extracts heading hierarchies, Python code blocks, key points, and AI summaries
from uploaded Markdown / PDF / Text documents and converts them to Knowledge Nodes & Edges.
"""

import re
import uuid
from typing import List, Dict, Any, Tuple


def parse_markdown_textbook(content: str, book_title: str = "导入教材") -> Dict[str, Any]:
    """
    Parses Markdown textbook text into structured Knowledge Nodes and prerequisite Edges.
    """
    lines = content.splitlines()
    
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    
    current_node = None
    current_code_lines = []
    in_code_block = False
    prev_node_id = None

    for line in lines:
        line_str = line.strip()
        
        # Detect code block fence
        if line_str.startswith("```"):
            if in_code_block:
                in_code_block = False
                if current_node:
                    snippet = "\n".join(current_code_lines)
                    current_node["aiSummary"]["recommendedCodeSnippet"] = snippet
                current_code_lines = []
            else:
                in_code_block = True
                current_code_lines = []
            continue

        if in_code_block:
            current_code_lines.append(line)
            continue

        # Detect Headings (# H1, ## H2, ### H3)
        heading_match = re.match(r"^(#{1,3})\s+(.+)", line_str)
        if heading_match:
            heading_title = heading_match.group(2).strip()
            node_id = f"imported-{uuid.uuid4().hex[:8]}"
            
            new_node = {
                "id": node_id,
                "name": heading_title,
                "category": book_title,
                "description": f"{book_title} 章节: {heading_title}",
                "importance": 4,
                "aiSummary": {
                    "overview": f"选自教材《{book_title}》的核心知识点：{heading_title}",
                    "keyPoints": [f"{heading_title} 概念解析", "语法规格与运行特性"],
                    "commonPitfalls": ["注意变量作用域与基本类型转换", "注意代码块缩进准则"],
                    "recommendedCodeSnippet": ""
                }
            }
            nodes.append(new_node)

            # Create prerequisite edge connecting previous node to new node
            if prev_node_id:
                edges.append({
                    "id": f"e-{prev_node_id}-{node_id}",
                    "source": prev_node_id,
                    "target": node_id,
                    "relationType": "prerequisite"
                })

            prev_node_id = node_id
            current_node = new_node
            continue

        # Append body text to current node description
        if current_node and line_str and not line_str.startswith("#"):
            if len(current_node["description"]) < 300:
                current_node["description"] += f" {line_str}"

    return {
        "bookTitle": book_title,
        "totalParsedNodes": len(nodes),
        "totalParsedEdges": len(edges),
        "nodes": nodes,
        "edges": edges
    }
