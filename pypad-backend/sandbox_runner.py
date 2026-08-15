"""
PyPad Code Sandbox Security Runner
Provides AST security checking, timeout process isolation, output truncation,
intelligent Traceback error line parsing, and runtime variable capture.
"""

import ast
import os
import sys
import time
import tempfile
import subprocess
import json
from typing import Dict, Any, Tuple, Optional

# ── Variable Serialization & Capture ──────────────────────

_VARIABLE_CAPTURE_SERIALIZER = r'''
import json as __json, sys as __sys, datetime as __dt, decimal as __dec, fractions as __frac, collections as __col

def __serialize_value(val, __depth=0):
    if __depth > 6:
        return {"type": type(val).__name__, "value": "[depth limit]", "size": 0}
    if val is None:
        return {"type": "NoneType", "value": None, "size": 0}
    if isinstance(val, (bool, int, float, str)):
        return {"type": type(val).__name__, "value": val, "size": len(str(val))}
    if isinstance(val, bytes):
        return {"type": "bytes", "value": f"<{len(val)} bytes>", "size": len(val)}
    if isinstance(val, complex):
        return {"type": "complex", "value": str(val), "size": 16}
    if isinstance(val, __dec.Decimal):
        return {"type": "Decimal", "value": str(val), "size": 16}
    if isinstance(val, __frac.Fraction):
        return {"type": "Fraction", "value": str(val), "size": 16}
    if isinstance(val, (__dt.datetime, __dt.date, __dt.time)):
        return {"type": type(val).__name__, "value": val.isoformat(), "size": 26}
    if isinstance(val, set):
        items = [__serialize_value(v, __depth+1) for v in list(val)[:20]]
        return {"type": "set", "value": items, "size": len(val), "length": len(val)}
    if isinstance(val, frozenset):
        items = [__serialize_value(v, __depth+1) for v in list(val)[:20]]
        return {"type": "frozenset", "value": items, "size": len(val), "length": len(val)}
    if isinstance(val, tuple):
        items = [__serialize_value(v, __depth+1) for v in val[:30]]
        return {"type": "tuple", "value": items, "size": len(val), "length": len(val)}
    if isinstance(val, list):
        items = [__serialize_value(v, __depth+1) for v in val[:30]]
        return {"type": "list", "value": items, "size": len(val), "length": len(val)}
    if isinstance(val, dict):
        items = {str(k): __serialize_value(v, __depth+1) for k, v in list(val.items())[:30]}
        return {"type": "dict", "value": items, "size": len(val), "length": len(val)}
    if hasattr(val, 'to_dict'):
        try:
            return {"type": type(val).__name__, "value": val.to_dict(), "size": 0}
        except Exception:
            pass
    if hasattr(val, '__dict__'):
        attrs = {}
        for k, v in list(val.__dict__.items())[:20]:
            if not k.startswith('_'):
                try:
                    attrs[k] = __serialize_value(v, __depth+1)
                except Exception:
                    attrs[k] = {"type": type(v).__name__, "value": str(v)[:100], "size": 0}
        return {"type": type(val).__name__, "value": attrs, "size": len(attrs)}
    return {"type": type(val).__name__, "value": str(val)[:200], "size": len(str(val))}

__pypad_vars = {}
for __k, __v in list(locals().items()):
    if not __k.startswith('_') and __k not in ('__builtins__',):
        try:
            __pypad_vars[__k] = __serialize_value(__v)
        except Exception:
            pass
__sys.stderr.write('\n__PYPAD_VARIABLES__' + __json.dumps(__pypad_vars, ensure_ascii=False, default=str) + '__END_VARIABLES__\n')
'''

FORBIDDEN_IMPORTS = {
    "os", "sys", "subprocess", "shutil", "socket", "ctypes", 
    "pickle", "importlib", "signal", "multiprocessing", "threading"
}

FORBIDDEN_FUNCTIONS = {
    "eval", "exec", "__import__", "compile", "open"
}


def security_audit(code: str) -> Tuple[bool, str]:
    """
    AST-level static security scan.
    Returns (is_safe, violation_reason).
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        # Let SyntaxErrors pass to python execution engine for detailed SyntaxError traceback
        return True, ""

    for node in ast.walk(tree):
        # 1. Check Import & ImportFrom
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_pkg = alias.name.split(".")[0]
                if root_pkg in FORBIDDEN_IMPORTS:
                    return False, f"安全拦截：禁止导入危险模块 '{root_pkg}'"
        
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_pkg = node.module.split(".")[0]
                if root_pkg in FORBIDDEN_IMPORTS:
                    return False, f"安全拦截：禁止从危险模块 '{root_pkg}' 导入"

        # 2. Check Call expressions
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in FORBIDDEN_FUNCTIONS:
                    return False, f"安全拦截：禁止使用高危系统函数 '{node.func.id}()'"

    return True, ""


def parse_traceback_advice(stderr: str, code: str) -> Dict[str, Any]:
    """
    Parse Python traceback stderr to extract exact failing line number and human readable advice.
    """
    line_number = None
    error_type = "UnknownError"
    error_msg = stderr

    lines = stderr.strip().split("\n")
    for line in lines:
        if 'File "<string>"' in line or 'File "' in line:
            parts = line.split(",")
            for part in parts:
                if "line " in part:
                    try:
                        line_number = int(part.strip().split(" ")[1])
                    except ValueError:
                        pass
        elif ":" in line and not line.startswith(" "):
            parts = line.split(":", 1)
            error_type = parts[0].strip()
            error_msg = parts[1].strip() if len(parts) > 1 else line

    advice = "提示：请检查代码语法与逻辑"
    if "IndentationError" in error_type:
        advice = f"第 {line_number or '?'} 行：缩进错误。请检查条件语句、循环或函数定义下方是否缺少 4 个空格缩进。"
    elif "SyntaxError" in error_type:
        advice = f"第 {line_number or '?'} 行：语法错误。请检查是否遗漏了冒号 ':'、括号 '()' 或引号 ''。"
    elif "NameError" in error_type:
        advice = f"第 {line_number or '?'} 行：变量名未定义。请确认变量拼写是否正确或此前已赋值。"
    elif "TypeError" in error_type:
        advice = f"第 {line_number or '?'} 行：类型错误。请检查运算符两侧的数据类型是否匹配。"
    elif "ZeroDivisionError" in error_type:
        advice = f"第 {line_number or '?'} 行：除以零错误。除数不能为 0。"
    elif "IndexError" in error_type:
        advice = f"第 {line_number or '?'} 行：索引越界。请检查列表索引是否超出了有效范围。"
    elif "KeyError" in error_type:
        advice = f"第 {line_number or '?'} 行：字典键不存在。请检查访问的 Key 是否存在于字典中。"

    return {
        "lineNumber": line_number,
        "errorType": error_type,
        "errorMessage": error_msg,
        "chineseAdvice": advice
    }


def _parse_captured_variables(stderr: str) -> Optional[Dict[str, Any]]:
    """Extract captured variables from stderr output of the wrapper script."""
    try:
        start_marker = "__PYPAD_VARIABLES__"
        end_marker = "__END_VARIABLES__"
        start_idx = stderr.find(start_marker)
        end_idx = stderr.find(end_marker)
        if start_idx != -1 and end_idx != -1:
            json_str = stderr[start_idx + len(start_marker):end_idx]
            return json.loads(json_str)
    except Exception:
        pass
    return None


def _wrap_code_with_capture(code: str) -> str:
    """Wrap user code to capture local variables after execution."""
    # Escape the serializer for embedding
    return code + "\n\n" + _VARIABLE_CAPTURE_SERIALIZER


def analyze_pythonic_style(code: str) -> Dict[str, Any]:
    """
    AST-based static analysis for Pythonic style issues.
    Returns structured style feedback without requiring LLM.
    """
    issues = []
    score = 100
    suggestions = []

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {"score": 0, "issues": [], "suggestions": ["代码存在语法错误，无法分析风格"], "category": "error"}

    for node in ast.walk(tree):
        # 1. Check for `for` loop that could be a list comprehension
        if isinstance(node, ast.For):
            # Detect pattern: result = []; for x in ...: result.append(expr)
            # This is a heuristic — we look for append calls inside for loops
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Attribute) and child.func.attr == 'append':
                        issues.append({
                            "line": node.lineno,
                            "type": "suggestion",
                            "severity": "info",
                            "rule": "use-list-comprehension",
                            "message": "此 for 循环中的 append 操作可考虑使用列表推导式替代",
                            "example": "[expr for x in iterable]"
                        })
                        score -= 5
                        break

        # 2. Check for `type() ==` instead of `isinstance()`
        # Patterns: type(x) == str, type(x) == type(y), type(x) is str
        if isinstance(node, ast.Compare):
            # Check if LEFT side is type() call
            if isinstance(node.left, ast.Call) and isinstance(node.left.func, ast.Name):
                if node.left.func.id == 'type':
                    for op in node.ops:
                        if isinstance(op, (ast.Eq, ast.Is, ast.NotEq, ast.IsNot)):
                            issues.append({
                                "line": node.lineno,
                                "type": "warning",
                                "severity": "medium",
                                "rule": "use-isinstance",
                                "message": "使用 `type(x) == T` 不如 `isinstance(x, T)` Pythonic（不支持继承）",
                                "example": "isinstance(x, str) 而非 type(x) == str"
                            })
                            score -= 8
                            break
            # Also check if RIGHT side is type() call: str == type(x)
            for op, comparator in zip(node.ops, node.comparators):
                if isinstance(comparator, ast.Call) and isinstance(comparator.func, ast.Name):
                    if comparator.func.id == 'type' and isinstance(op, (ast.Eq, ast.Is)):
                        issues.append({
                            "line": node.lineno,
                            "type": "warning",
                            "severity": "medium",
                            "rule": "use-isinstance",
                            "message": "使用 `type(x) == T` 不如 `isinstance(x, T)` Pythonic（不支持继承）",
                            "example": "isinstance(x, str) 而非 type(x) == str"
                        })
                        score -= 8
                        break

        # 3. Check for bare `except:` without exception type
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            issues.append({
                "line": node.lineno,
                "type": "warning",
                "severity": "high",
                "rule": "no-bare-except",
                "message": "裸 `except:` 会捕获所有异常（含 KeyboardInterrupt），请指定异常类型",
                "example": "except Exception as e:"
            })
            score -= 15

        # 4. Check for `if x == True` or `if x == False`
        if isinstance(node, ast.Compare):
            for comparator in node.comparators:
                if isinstance(comparator, ast.Constant) and isinstance(comparator.value, bool):
                    if isinstance(node.ops[0], (ast.Eq, ast.Is)):
                        val = comparator.value
                        issues.append({
                            "line": node.lineno,
                            "type": "suggestion",
                            "severity": "low",
                            "rule": "simplify-bool-compare",
                            "message": f"`== {'True' if val else 'False'}` 可简化为 `{'if x:' if val else 'if not x:'}`",
                            "example": f"if x:" if val else "if not x:"
                        })
                        score -= 3

        # 5. Check for string concatenation in loops (should use join)
        if isinstance(node, (ast.For, ast.While)):
            for child in ast.walk(node):
                if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                    issues.append({
                        "line": child.lineno,
                        "type": "warning",
                        "severity": "medium",
                        "rule": "use-join",
                        "message": "循环中字符串 `+=` 拼接效率低，建议使用 `''.join()` 或列表收集后 join",
                        "example": "result = ''.join(parts)"
                    })
                    score -= 5
                    break

        # 6. Check for `open()` without `with` statement
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'open':
            # Check if this is inside a `with` statement
            in_with = False
            for ancestor in ast.walk(tree):
                if isinstance(ancestor, ast.With):
                    for item in ancestor.items:
                        if isinstance(item.context_expr, ast.Call):
                            if isinstance(item.context_expr.func, ast.Name) and item.context_expr.func.id == 'open':
                                # Check if this is the same open call
                                if hasattr(item.context_expr, 'lineno') and item.context_expr.lineno == node.lineno:
                                    in_with = True
            if not in_with:
                issues.append({
                    "line": node.lineno,
                    "type": "warning",
                    "severity": "high",
                    "rule": "use-with-open",
                    "message": "`open()` 应配合 `with` 语句使用，确保文件正确关闭",
                    "example": "with open('file.txt') as f: ..."
                })
                score -= 10

        # 7. Check for magic numbers (int/float literals outside of assignments)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            # Skip common values and assignments
            if node.value not in (0, 1, -1, 2, 10, 100, 0.0, 1.0, 0.5):
                parent = getattr(node, '_parent', None)

        # 8. Check for `len(x) == 0` instead of `not x`
        if isinstance(node, ast.Compare):
            for op, comparator in zip(node.ops, node.comparators):
                if isinstance(comparator, ast.Constant) and comparator.value == 0:
                    if isinstance(op, (ast.Eq, ast.LtE)):
                        if isinstance(node.left, ast.Call) and isinstance(node.left.func, ast.Name):
                            if node.left.func.id == 'len':
                                issues.append({
                                    "line": node.lineno,
                                    "type": "suggestion",
                                    "severity": "low",
                                    "rule": "use-truthiness",
                                    "message": "`len(x) == 0` 不如 `not x` Pythonic",
                                    "example": "if not my_list:"
                                })
                                score -= 3

    # Generate summary suggestions
    if not issues:
        suggestions.append("代码风格良好，符合 Pythonic 规范 ✨")
    else:
        rule_counts = {}
        for issue in issues:
            rule_counts[issue["rule"]] = rule_counts.get(issue["rule"], 0) + 1
        for rule, count in sorted(rule_counts.items(), key=lambda x: -x[1]):
            rule_messages = {
                "use-list-comprehension": "多处可使用列表推导式简化",
                "use-isinstance": "类型检查应使用 isinstance()",
                "no-bare-except": "避免裸 except，应指定异常类型",
                "simplify-bool-compare": "布尔值比较可简化",
                "use-join": "循环中字符串拼接应使用 join()",
                "use-with-open": "文件操作应使用 with 语句",
                "use-truthiness": "空值检查应使用 Python 真值判断",
            }
            msg = rule_messages.get(rule, rule)
            suggestions.append(f"{msg} ({count}处)")

    # Determine category
    high_count = sum(1 for i in issues if i["severity"] == "high")
    medium_count = sum(1 for i in issues if i["severity"] == "medium")
    if high_count > 0:
        category = "needs_improvement"
    elif medium_count > 2:
        category = "fair"
    elif issues:
        category = "good"
    else:
        category = "excellent"

    return {
        "score": max(0, score),
        "issues": issues[:20],  # Limit to 20 issues
        "suggestions": suggestions[:5],
        "category": category
    }


def _clean_stderr(stderr: str) -> str:
    """Remove variable capture markers from stderr for clean user output."""
    start_marker = "__PYPAD_VARIABLES__"
    end_marker = "__END_VARIABLES__"
    start_idx = stderr.find(start_marker)
    end_idx = stderr.find(end_marker)
    if start_idx != -1 and end_idx != -1:
        return stderr[:start_idx] + stderr[end_idx + len(end_marker):]
    return stderr


from docker_runner import is_docker_available, run_in_docker_container


def execute_sandboxed(code: str, timeout_sec: float = 5.0, capture_variables: bool = True) -> Dict[str, Any]:
    """
    Execute user Python code with security audit, Docker container CGroups isolation (if available), or Subprocess fallback.
    """
    # Step 1: Security Audit
    is_safe, violation_msg = security_audit(code)
    if not is_safe:
        return {
            "status": "security_violation",
            "stdout": "",
            "stderr": violation_msg,
            "exitCode": 403,
            "runtimeMs": 0,
            "errorDetail": {
                "lineNumber": None,
                "errorType": "SecurityViolation",
                "errorMessage": violation_msg,
                "chineseAdvice": "代码包含未允许的安全调用（如文件或系统命令操作），已被沙箱强行拦截。"
            }
        }

    # Determine if we should capture variables
    exec_code = _wrap_code_with_capture(code) if capture_variables else code

    # Step 2: Prefer Docker Container CGroups Hard Isolation
    if is_docker_available():
        res = run_in_docker_container(exec_code, timeout_seconds=int(timeout_sec))
        if res.get("exitCode") != 0 and res.get("stderr"):
            res["errorDetail"] = parse_traceback_advice(res["stderr"])
        # Parse variables from Docker output
        if capture_variables and res.get("exitCode") == 0:
            variables = _parse_captured_variables(res.get("stderr", ""))
            res["variables"] = variables
            res["stderr"] = _clean_stderr(res.get("stderr", ""))
        return res

    # Step 3: Temporary file execution (Subprocess Fallback)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(exec_code)
        tmp_path = f.name

    start_time = time.time()
    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
        runtime_ms = int((time.time() - start_time) * 1000)
        stdout_buf = result.stdout[:50000]
        stderr_buf = result.stderr[:50000]
        exit_code = result.returncode

        # Parse captured variables from stderr
        variables = None
        if capture_variables and exit_code == 0:
            variables = _parse_captured_variables(stderr_buf)
            stderr_buf = _clean_stderr(stderr_buf)

        status = "success" if exit_code == 0 else "runtime_error"
        error_detail = None
        if exit_code != 0:
            error_detail = parse_traceback_advice(stderr_buf, code)

        return {
            "status": status,
            "stdout": stdout_buf,
            "stderr": stderr_buf,
            "exitCode": exit_code,
            "runtimeMs": runtime_ms,
            "errorDetail": error_detail,
            "variables": variables
        }

    except subprocess.TimeoutExpired:
        runtime_ms = int((time.time() - start_time) * 1000)
        return {
            "status": "timeout",
            "stdout": "",
            "stderr": f"执行超时：代码运行超过了最大限制时间 ({int(timeout_sec)}s)，已被沙箱自动终止。",
            "exitCode": 124,
            "runtimeMs": runtime_ms,
            "errorDetail": {
                "lineNumber": None,
                "errorType": "TimeoutExpired",
                "errorMessage": "Execution timed out",
                "chineseAdvice": "代码可能存在死循环（如 `while True:` 缺乏退出条件），已被沙箱终止。"
            }
        }
    except Exception as e:
        runtime_ms = int((time.time() - start_time) * 1000)
        return {
            "status": "runtime_error",
            "stdout": "",
            "stderr": str(e),
            "exitCode": -1,
            "runtimeMs": runtime_ms,
            "errorDetail": None
        }
    finally:
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
