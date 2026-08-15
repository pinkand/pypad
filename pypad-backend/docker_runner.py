"""
PyPad Docker Container Sandbox Hard Isolation Runner.
Provides hard Cgroups memory & CPU isolation with network disabled (--network none).
Falls back gracefully if Docker daemon is not active.
"""

import subprocess
import tempfile
import os
import time
from typing import Dict, Any


def is_docker_available() -> bool:
    """
    Checks whether Docker CLI and daemon are accessible.
    """
    try:
        res = subprocess.run(
            ["docker", "info"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=2
        )
        return res.returncode == 0
    except Exception:
        return False


def run_in_docker_container(code: str, timeout_seconds: int = 5) -> Dict[str, Any]:
    """
    Executes Python code inside an ephemeral Docker container with CGroups memory & CPU limits.
    """
    start_time = time.time()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        code_file = os.path.join(tmpdir, "script.py")
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(code)

        cmd = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", "128m",
            "--cpus", "0.5",
            "-v", f"{tmpdir}:/app:ro",
            "python:3.9-slim",
            "python", "/app/script.py"
        ]

        try:
            res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout_seconds,
                text=True
            )
            runtime_ms = int((time.time() - start_time) * 1000)
            
            return {
                "stdout": res.stdout[:50000],
                "stderr": res.stderr[:50000],
                "exitCode": res.returncode,
                "runtimeMs": runtime_ms,
                "isolatedBy": "docker-cgroups"
            }
        except subprocess.TimeoutExpired:
            runtime_ms = int((time.time() - start_time) * 1000)
            return {
                "stdout": "",
                "stderr": f"ExecError: Container execution timed out (> {timeout_seconds}s limit)",
                "exitCode": 124,
                "runtimeMs": runtime_ms,
                "isolatedBy": "docker-cgroups"
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": f"ContainerError: {str(e)}",
                "exitCode": 1,
                "runtimeMs": 0,
                "isolatedBy": "docker-cgroups"
            }
