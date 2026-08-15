"""
Unit tests for PyPad Sandbox Security Runner.
Tests AST static audit, timeout execution, output truncation, and Traceback parsing.
"""

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "pypad-backend"))
from sandbox_runner import execute_sandboxed, security_audit, parse_traceback_advice


class TestSandboxRunner(unittest.TestCase):

    def test_normal_code_execution(self):
        code = "print('Hello, PyPad Sandbox!')"
        res = execute_sandboxed(code)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["exitCode"], 0)
        self.assertIn("Hello, PyPad Sandbox!", res["stdout"])

    def test_security_violation_os_import(self):
        code = "import os\nos.system('echo hacked')"
        is_safe, reason = security_audit(code)
        self.assertFalse(is_safe)
        self.assertIn("危险模块 'os'", reason)

        res = execute_sandboxed(code)
        self.assertEqual(res["status"], "security_violation")
        self.assertEqual(res["exitCode"], 403)

    def test_security_violation_eval_call(self):
        code = "eval('1 + 1')"
        is_safe, reason = security_audit(code)
        self.assertFalse(is_safe)
        self.assertIn("高危系统函数 'eval()'", reason)

    def test_timeout_execution(self):
        code = "import time\nwhile True:\n    pass"
        res = execute_sandboxed(code, timeout_sec=1.0)
        self.assertEqual(res["status"], "timeout")
        self.assertEqual(res["exitCode"], 124)
        self.assertIn("超时", res["stderr"])

    def test_syntax_error_advice(self):
        code = "def foo()\n    pass"
        res = execute_sandboxed(code)
        self.assertEqual(res["status"], "runtime_error")
        self.assertIsNotNone(res["errorDetail"])
        self.assertIn("语法错误", res["errorDetail"]["chineseAdvice"])

    def test_zero_division_error_advice(self):
        code = "x = 1 / 0"
        res = execute_sandboxed(code)
        self.assertEqual(res["status"], "runtime_error")
        self.assertIsNotNone(res["errorDetail"])
        self.assertIn("除以零错误", res["errorDetail"]["chineseAdvice"])


if __name__ == "__main__":
    unittest.main()
