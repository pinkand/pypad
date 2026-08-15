"""
Unit tests for PyPad Automated Textbook Parsing Engine.
Tests Markdown chapter heading extraction, code block parsing, and node generation.
"""

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "pypad-backend"))
from textbook_parser import parse_markdown_textbook


class TestTextbookParser(unittest.TestCase):

    def setUp(self):
        self.sample_markdown = """# 第一章：Python 快速入门
Python 是一种高层级的、解释型编程语言。

## 1.1 变量与赋值
在 Python 中无需声明类型，直接使用赋值符号进行变量声明。

```python
x = 10
y = 20
print(x + y)
```

## 1.2 列表推导式
列表推导式是 Python 标志性的简洁表达范式。

```python
squares = [i ** 2 for i in range(10)]
print(squares)
```
"""

    def test_parse_markdown_headings(self):
        result = parse_markdown_textbook(self.sample_markdown, book_title="Python极简教程")
        self.assertEqual(result["totalParsedNodes"], 3)
        self.assertEqual(result["totalParsedEdges"], 2)

        node_names = [n["name"] for n in result["nodes"]]
        self.assertIn("第一章：Python 快速入门", node_names)
        self.assertIn("1.1 变量与赋值", node_names)
        self.assertIn("1.2 列表推导式", node_names)

    def test_parse_code_snippets(self):
        result = parse_markdown_textbook(self.sample_markdown, book_title="Python极简教程")
        nodes = result["nodes"]
        
        # 1.1 变量与赋值 should have x = 10 snippet
        var_node = next(n for n in nodes if n["name"] == "1.1 变量与赋值")
        snippet = var_node["aiSummary"]["recommendedCodeSnippet"]
        self.assertIn("x = 10", snippet)

        # 1.2 列表推导式 should have squares snippet
        list_node = next(n for n in nodes if n["name"] == "1.2 列表推导式")
        snippet2 = list_node["aiSummary"]["recommendedCodeSnippet"]
        self.assertIn("squares =", snippet2)


if __name__ == "__main__":
    unittest.main()
