"""
Test suite for PyPad backend.
Run with: pytest tests/test_api.py -v
Or: python tests/test_api.py (stdlib fallback)
"""
import sys
import os

# Add pypad-backend/ to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pypad-backend"))

from fastapi.testclient import TestClient

# Ensure we're using the test DB (or let conftest handle it)
os.environ.setdefault("DB_BACKEND", "sqlite")

from main import app
from database import create_db_and_tables
from seed import seed

# Ensure tables and seed data exist for test
create_db_and_tables()
try:
    seed()
except Exception as e:
    print(f"Seed warning: {e}")

client = TestClient(app)


# ── Helpers ──────────────────────────────────
class Results:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def check(self, name, condition, detail=""):
        if condition:
            self.passed += 1
            print(f"  ✓ {name}")
        else:
            self.failed += 1
            self.errors.append(f"{name}: {detail}")
            print(f"  ✗ {name} — {detail}")

results = Results()


import time

def test_auth():
    print("\n[Auth]")
    uname = f"testrunner_{int(time.time())}"
    # Register
    r = client.post("/api/auth/register", json={
        "username": uname, "email": f"{uname}@test.com", "password": "pass123",
    })
    results.check("register", r.status_code == 200 and "token" in r.json(), r.text[:100])
    token = r.json().get("token", "")

    # Login
    r = client.post("/api/auth/login", json={"username": uname, "password": "pass123"})
    results.check("login", r.status_code == 200 and "token" in r.json(), r.text[:100])

    # Me
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    results.check("me", r.status_code == 200 and r.json()["username"] == uname, r.text[:100])

    # Wrong password
    r = client.post("/api/auth/login", json={"username": uname, "password": "wrong"})
    results.check("wrong_password", r.status_code == 401, str(r.status_code))


def test_knowledge():
    print("\n[Knowledge]")
    r = client.get("/api/knowledge/nodes")
    results.check("get_nodes", r.status_code == 200 and len(r.json()) > 0, f"count={len(r.json())}")

    r = client.get("/api/knowledge/graph")
    data = r.json()
    results.check("get_graph", r.status_code == 200 and "nodes" in data and "edges" in data)

    r = client.get("/api/knowledge/categories")
    results.check("categories", r.status_code == 200 and "categories" in r.json())

    r = client.get("/api/knowledge/search", params={"q": "函数"})
    results.check("search", r.status_code == 200 and len(r.json()["results"]) > 0)

    r = client.get("/api/knowledge/rag-context", params={"q": "变量"})
    results.check("rag_context", r.status_code == 200 and "context" in r.json())


def test_courses():
    print("\n[Courses]")
    r = client.get("/api/courses")
    results.check("get_courses", r.status_code == 200 and len(r.json()["courses"]) > 0)

    r = client.get("/api/courses/py-course-1")
    results.check("get_course", r.status_code == 200 and r.json()["course"]["id"] == "py-course-1")

    r = client.get("/api/chapters")
    results.check("get_chapters", r.status_code == 200 and len(r.json()["chapters"]) > 0)


def test_workspace():
    print("\n[Workspace]")
    # Run code
    r = client.post("/api/workspace/run", json={
        "sessionId": "test-sess", "code": "print(2+3)", "language": "python",
    })
    run = r.json()
    results.check("run_code", r.status_code == 200 and run["status"] == "success" and "5" in run.get("stdout", ""))

    # Syntax error
    r = client.post("/api/workspace/run", json={
        "sessionId": "test-sess", "code": "def foo(", "language": "python",
    })
    results.check("syntax_error", r.json()["status"] == "runtime_error")


def test_sessions():
    print("\n[Sessions]")
    r = client.post("/api/sessions/start", json={
        "userId": "user-1", "knowledgeNodeId": "functions-def",
    })
    results.check("start_session", r.status_code == 200 and "session" in r.json())
    sid = r.json()["session"]["id"]

    r = client.post(f"/api/sessions/{sid}/events", json={"eventType": "read_content", "payload": {}})
    results.check("record_event", r.status_code == 200 and r.json()["success"])

    r = client.post(f"/api/sessions/{sid}/end")
    results.check("end_session", r.status_code == 200)


def test_practices():
    print("\n[Practices]")
    r = client.get("/api/practices")
    results.check("get_practices", r.status_code == 200)

    r = client.post("/api/practices/prac-input-1/submit", json={"code": "print('test')"})
    results.check("submit_practice", r.status_code == 200 and "score" in r.json())


def test_agent():
    print("\n[Agent]")
    r = client.post("/api/agent/chat", json={
        "message": "什么是Python?", "agentType": "tutor", "userId": "user-1",
    })
    results.check("chat", r.status_code == 200 and "message" in r.json() and len(r.json()["message"]) > 0)


def test_dashboard():
    print("\n[Dashboard]")
    r = client.get("/api/dashboard/overview")
    results.check("overview", r.status_code == 200 and "overallMastery" in r.json())

    r = client.get("/api/dashboard/progress")
    results.check("progress", r.status_code == 200 and "userId" in r.json())


def test_textbook_and_recommendation():
    print("\n[Textbook & Recommendation Engine]")
    r = client.post("/api/textbook/upload", json={
        "bookTitle": "实战教材测试",
        "content": "# 第一章：Python 高阶范式\n## 1.1 闭包与装饰器\n语法糖定义与上下文绑定\n```python\ndef my_decorator(func):\n    return func\n```"
    })
    results.check("textbook_upload", r.status_code == 200 and r.json().get("success") is True)

    r = client.get("/api/user/recommend-path")
    results.check("recommend_path", r.status_code == 200 and "sequence" in r.json() and len(r.json()["sequence"]) > 0)


# ── Run all ──────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("PyPad — Test Suite")
    print("=" * 50)

    test_auth()
    test_knowledge()
    test_courses()
    test_workspace()
    test_sessions()
    test_practices()
    test_agent()
    test_dashboard()
    test_textbook_and_recommendation()

    print("\n" + "=" * 50)
    print(f"Results: {results.passed} passed, {results.failed} failed")
    if results.errors:
        print("Failures:")
        for e in results.errors:
            print(f"  - {e}")
    print("=" * 50)
    sys.exit(0 if results.failed == 0 else 1)
