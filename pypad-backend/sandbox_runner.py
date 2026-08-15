"""
PyPad Code Sandbox Security Runner
Provides AST security checking, timeout process isolation, output truncation,
and intelligent Traceback error line parsing.
"""

import ast
import os
import sys
import time
import tempfile
import subprocess
from typing import Dict, Any, Tuple

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


from docker_runner import is_docker_available, run_in_docker_container


def execute_sandboxed(code: str, timeout_sec: float = 5.0) -> Dict[str, Any]:
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

    # Step 2: Prefer Docker Container CGroups Hard Isolation
    if is_docker_available():
        res = run_in_docker_container(code, timeout_seconds=int(timeout_sec))
        if res.get("exitCode") != 0 and res.get("stderr"):
            res["errorDetail"] = parse_traceback_advice(res["stderr"])
        return res

    # Step 3: Temporary file execution (Subprocess Fallback)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
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
            "errorDetail": error_detail
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
