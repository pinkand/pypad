"""
Unit tests for PyPad Vector RAG Engine.
Tests TF-IDF indexing, vector similarity search, and prompt formatting.
"""

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "pypad-backend"))
from rag_service import VectorRAGEngine, tokenize


class TestVectorRAG(unittest.TestCase):

    def setUp(self):
        self.engine = VectorRAGEngine()
        self.sample_nodes = [
            {
                "id": "py-variables",
                "name": "变量与数据类型",
                "category": "基本语法",
                "description": "Python 中的变量声明与基础数据类型包含 int, float, str, bool",
                "aiSummary": {"overview": "掌握变量赋值与基础数据类型转换", "keyPoints": ["动态类型", "不可变类型"]}
            },
            {
                "id": "py-control-if",
                "name": "条件控制语句",
                "category": "控制结构",
                "description": "使用 if, elif, else 进行多分支逻辑判定与条件控制",
                "aiSummary": {"overview": "分支判断逻辑与布尔表达式计算", "keyPoints": ["条件嵌套", "布尔逻辑"]}
            },
            {
                "id": "py-functions",
                "name": "函数定义与参数",
                "category": "函数设计",
                "description": "使用 def 关键字定义可复用的代码块，支持默认参数与 *args **kwargs",
                "aiSummary": {"overview": "模块化函数设计与作用域机制", "keyPoints": ["返回值", "形参与实参"]}
            }
        ]
        self.engine.index_knowledge_nodes(self.sample_nodes)

    def test_tokenize(self):
        tokens = tokenize("Python 变量与数据类型 123")
        self.assertIn("python", tokens)
        self.assertIn("变", tokens)
        self.assertIn("变量", tokens)

    def test_search_relevance(self):
        results = self.engine.search("如何在 Python 中定义函数和传参？", top_k=2)
        self.assertTrue(len(results) > 0)
        top_doc = results[0][1]
        self.assertEqual(top_doc["id"], "py-functions")

    def test_rag_prompt_generation(self):
        prompt = self.engine.get_rag_context_prompt("分支判断语句 if else")
        self.assertIn("【PyPad 向量检索知识库关联背景】", prompt)
        self.assertIn("条件控制语句", prompt)


if __name__ == "__main__":
    unittest.main()
