"""
Unit tests for PyPad new features:
1. Variable capture in sandbox execution
2. Pythonic style analysis
3. Style review API endpoint
"""

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "pypad-backend"))
from sandbox_runner import execute_sandboxed, analyze_pythonic_style, _parse_captured_variables


class TestVariableCapture(unittest.TestCase):
    """Test variable capture during sandbox execution."""

    def test_capture_simple_variables(self):
        code = "x = 42\nname = 'PyPad'\nflag = True"
        res = execute_sandboxed(code, capture_variables=True)
        self.assertEqual(res["status"], "success")
        self.assertIsNotNone(res.get("variables"))
        vars_ = res["variables"]
        self.assertIn("x", vars_)
        self.assertEqual(vars_["x"]["type"], "int")
        self.assertEqual(vars_["x"]["value"], 42)
        self.assertIn("name", vars_)
        self.assertEqual(vars_["name"]["type"], "str")
        self.assertEqual(vars_["name"]["value"], "PyPad")
        self.assertIn("flag", vars_)
        self.assertEqual(vars_["flag"]["type"], "bool")
        self.assertEqual(vars_["flag"]["value"], True)

    def test_capture_list_variable(self):
        code = "nums = [1, 2, 3, 4, 5]"
        res = execute_sandboxed(code, capture_variables=True)
        self.assertEqual(res["status"], "success")
        vars_ = res["variables"]
        self.assertIn("nums", vars_)
        self.assertEqual(vars_["nums"]["type"], "list")
        self.assertEqual(vars_["nums"]["length"], 5)
        self.assertIsInstance(vars_["nums"]["value"], list)

    def test_capture_dict_variable(self):
        code = "data = {'key': 'value', 'count': 10}"
        res = execute_sandboxed(code, capture_variables=True)
        self.assertEqual(res["status"], "success")
        vars_ = res["variables"]
        self.assertIn("data", vars_)
        self.assertEqual(vars_["data"]["type"], "dict")
        self.assertEqual(vars_["data"]["length"], 2)

    def test_capture_none_variable(self):
        code = "result = None"
        res = execute_sandboxed(code, capture_variables=True)
        self.assertEqual(res["status"], "success")
        vars_ = res["variables"]
        self.assertIn("result", vars_)
        self.assertEqual(vars_["result"]["type"], "NoneType")
        self.assertIsNone(vars_["result"]["value"])

    def test_capture_nested_structure(self):
        code = "matrix = [[1, 2], [3, 4]]"
        res = execute_sandboxed(code, capture_variables=True)
        self.assertEqual(res["status"], "success")
        vars_ = res["variables"]
        self.assertIn("matrix", vars_)
        self.assertEqual(vars_["matrix"]["type"], "list")
        self.assertEqual(vars_["matrix"]["length"], 2)

    def test_no_variables_when_disabled(self):
        code = "x = 42"
        res = execute_sandboxed(code, capture_variables=False)
        self.assertEqual(res["status"], "success")
        self.assertIsNone(res.get("variables"))

    def test_variables_on_error_is_none(self):
        code = "x = 1 / 0"
        res = execute_sandboxed(code, capture_variables=True)
        self.assertEqual(res["status"], "runtime_error")
        self.assertIsNone(res.get("variables"))

    def test_capture_empty_code(self):
        code = ""
        res = execute_sandboxed(code, capture_variables=True)
        self.assertEqual(res["status"], "success")
        # Should still return variables (possibly empty or with builtins filtered)
        self.assertIn("variables", res)

    def test_capture_with_print(self):
        code = "x = 10\nprint(f'x = {x}')\ny = x * 2"
        res = execute_sandboxed(code, capture_variables=True)
        self.assertEqual(res["status"], "success")
        self.assertIn("x = 10", res["stdout"])
        vars_ = res["variables"]
        self.assertIn("x", vars_)
        self.assertIn("y", vars_)
        self.assertEqual(vars_["y"]["value"], 20)

    def test_capture_set_variable(self):
        code = "s = {1, 2, 3}"
        res = execute_sandboxed(code, capture_variables=True)
        self.assertEqual(res["status"], "success")
        vars_ = res["variables"]
        self.assertIn("s", vars_)
        self.assertEqual(vars_["s"]["type"], "set")
        self.assertEqual(vars_["s"]["length"], 3)


class TestParseCapturedVariables(unittest.TestCase):
    """Test the stderr parsing function for variable capture."""

    def test_parse_valid_json(self):
        stderr = 'some output\n__PYPAD_VARIABLES__{"x": {"type": "int", "value": 42}}__END_VARIABLES__\n'
        result = _parse_captured_variables(stderr)
        self.assertIsNotNone(result)
        self.assertIn("x", result)
        self.assertEqual(result["x"]["value"], 42)

    def test_parse_missing_markers(self):
        stderr = "just normal output\n"
        result = _parse_captured_variables(stderr)
        self.assertIsNone(result)

    def test_parse_malformed_json(self):
        stderr = '__PYPAD_VARIABLES__{invalid json}__END_VARIABLES__'
        result = _parse_captured_variables(stderr)
        self.assertIsNone(result)


class TestPythonicStyleAnalysis(unittest.TestCase):
    """Test AST-based Pythonic style analysis."""

    def test_clean_code_scores_high(self):
        code = """
def greet(name: str) -> str:
    return f"Hello, {name}!"

result = greet("World")
print(result)
"""
        result = analyze_pythonic_style(code)
        self.assertGreaterEqual(result["score"], 90)
        self.assertIn(result["category"], ["excellent", "good"])

    def test_bare_except_detected(self):
        code = """
try:
    x = 1 / 0
except:
    pass
"""
        result = analyze_pythonic_style(code)
        self.assertLess(result["score"], 100)
        rules = [i["rule"] for i in result["issues"]]
        self.assertIn("no-bare-except", rules)

    def test_type_comparison_detected(self):
        code = """
x = "hello"
if type(x) == str:
    print("string")
"""
        result = analyze_pythonic_style(code)
        rules = [i["rule"] for i in result["issues"]]
        self.assertIn("use-isinstance", rules)

    def test_bool_comparison_detected(self):
        code = """
flag = True
if flag == True:
    print("yes")
"""
        result = analyze_pythonic_style(code)
        rules = [i["rule"] for i in result["issues"]]
        self.assertIn("simplify-bool-compare", rules)

    def test_len_zero_comparison_detected(self):
        code = """
items = [1, 2, 3]
if len(items) == 0:
    print("empty")
"""
        result = analyze_pythonic_style(code)
        rules = [i["rule"] for i in result["issues"]]
        self.assertIn("use-truthiness", rules)

    def test_list_comprehension_suggestion(self):
        code = """
result = []
for x in range(10):
    result.append(x * 2)
"""
        result = analyze_pythonic_style(code)
        rules = [i["rule"] for i in result["issues"]]
        self.assertIn("use-list-comprehension", rules)

    def test_syntax_error_returns_error_category(self):
        code = "def foo(\n    pass"
        result = analyze_pythonic_style(code)
        self.assertEqual(result["category"], "error")
        self.assertEqual(result["score"], 0)

    def test_string_concat_in_loop_detected(self):
        code = """
result = ""
for i in range(10):
    result += str(i)
"""
        result = analyze_pythonic_style(code)
        rules = [i["rule"] for i in result["issues"]]
        self.assertIn("use-join", rules)

    def test_multiple_issues_lower_score(self):
        code = """
try:
    x = "hello"
    if type(x) == str:
        result = []
        for i in range(10):
            result.append(i)
except:
    pass
"""
        result = analyze_pythonic_style(code)
        self.assertLessEqual(result["score"], 80)
        self.assertGreater(len(result["issues"]), 2)

    def test_suggestions_generated(self):
        code = """
try:
    pass
except:
    pass
"""
        result = analyze_pythonic_style(code)
        self.assertGreater(len(result["suggestions"]), 0)


class TestStyleReviewAPI(unittest.TestCase):
    """Test the style review API endpoint via TestClient."""

    @classmethod
    def setUpClass(cls):
        os.environ.setdefault("DB_BACKEND", "sqlite")
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pypad-backend"))
        from fastapi.testclient import TestClient
        from main import app
        from database import create_db_and_tables
        from seed import seed
        create_db_and_tables()
        try:
            seed()
        except Exception:
            pass
        cls.client = TestClient(app)

    def test_run_code_returns_variables(self):
        r = self.client.post("/api/workspace/run", json={
            "sessionId": "test-sess",
            "code": "x = 42\nname = 'test'",
            "language": "python",
        })
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("variables", data)
        self.assertIsNotNone(data["variables"])
        self.assertIn("x", data["variables"])
        self.assertEqual(data["variables"]["x"]["value"], 42)

    def test_style_review_endpoint(self):
        # First run code to create a WorkspaceRun
        r = self.client.post("/api/workspace/run", json={
            "sessionId": "test-sess",
            "code": "x = 1\nprint(x)",
            "language": "python",
        })
        run_id = r.json()["id"]

        # Now request style review
        r = self.client.post("/api/workspace/style-review", json={"runId": run_id})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("styleReview", data)
        self.assertIn("score", data["styleReview"])
        self.assertIn("issues", data["styleReview"])
        self.assertIn("suggestions", data["styleReview"])
        self.assertIn("category", data["styleReview"])

    def test_style_review_catches_bare_except(self):
        import time
        time.sleep(1)  # Ensure unique timestamp-based run ID
        r = self.client.post("/api/workspace/run", json={
            "sessionId": "test-bare-except",
            "code": "try:\n    pass\nexcept:\n    pass",
            "language": "python",
        })
        self.assertEqual(r.status_code, 200)
        run_id = r.json()["id"]

        r = self.client.post("/api/workspace/style-review", json={"runId": run_id})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        rules = [i["rule"] for i in data["styleReview"]["issues"]]
        self.assertIn("no-bare-except", rules)

    def test_ai_review_includes_style_score(self):
        r = self.client.post("/api/workspace/run", json={
            "sessionId": "test-sess",
            "code": "print('hello')",
            "language": "python",
        })
        run_id = r.json()["id"]

        r = self.client.post("/api/workspace/ai-review", json={"runId": run_id})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("review", data)
        self.assertIn("overallScore", data["review"])


if __name__ == "__main__":
    unittest.main()
