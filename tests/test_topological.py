"""
Unit tests for PyPad Topological Sort Learning Path Engine.
Tests Kahn's algorithm, priority queue weighting, and edge handling.
"""

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "pypad-backend"))
from topological_path import generate_topological_learning_path


class TestTopologicalPath(unittest.TestCase):

    def setUp(self):
        self.nodes = [
            {"id": "py-variables", "name": "变量与类型", "category": "基础", "importance": 5},
            {"id": "py-control-if", "name": "条件控制", "category": "基础", "importance": 4},
            {"id": "py-functions", "name": "函数定义", "category": "进阶", "importance": 5},
        ]
        self.edges = [
            {"source": "py-variables", "target": "py-control-if", "relationType": "prerequisite"},
            {"source": "py-control-if", "target": "py-functions", "relationType": "prerequisite"},
        ]
        self.masteries = {
            "py-variables": 80.0,
            "py-control-if": 20.0,
            "py-functions": 0.0,
        }

    def test_topological_sort_order(self):
        result = generate_topological_learning_path(self.nodes, self.edges, self.masteries)
        sequence = result["sequence"]
        self.assertEqual(len(sequence), 3)
        # Prerequisite order: py-variables must come before py-control-if, and py-control-if before py-functions
        ids = [item["id"] for item in sequence]
        self.assertEqual(ids, ["py-variables", "py-control-if", "py-functions"])

    def test_unblocked_priority(self):
        result = generate_topological_learning_path(self.nodes, self.edges, self.masteries)
        self.assertEqual(result["weakNodesCount"], 2)


if __name__ == "__main__":
    unittest.main()
