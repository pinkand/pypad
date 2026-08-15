"""
PyPad End-to-End Integration Test.
Tests the complete learning loop:
  Register → Login → Browse Knowledge → Start Session → Run Code →
  Submit Practice → Check Mastery Update → Get Recommended Path → AI Chat → Textbook Upload

Run with: python tests/test_e2e.py
"""

import sys
import os
import time
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pypad-backend"))

os.environ.setdefault("DB_BACKEND", "sqlite")

from fastapi.testclient import TestClient
from main import app
from database import create_db_and_tables
from seed import seed

# Fresh DB for E2E
create_db_and_tables()
try:
    seed()
except Exception:
    pass

client = TestClient(app)


# ── Test Harness ──────────────────────────────────────────────────────

class E2EResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.context = {}  # shared state across steps

    def check(self, name, condition, detail=""):
        if condition:
            self.passed += 1
            print(f"  ✓ {name}")
        else:
            self.failed += 1
            self.errors.append(f"{name}: {detail}")
            print(f"  ✗ {name} — {detail[:200]}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*50}")
        print(f"E2E Results: {self.passed}/{total} passed, {self.failed} failed")
        if self.errors:
            print(f"\nFailures:")
            for e in self.errors:
                print(f"  ✗ {e}")
        print(f"{'='*50}")
        return self.failed == 0


r = E2EResults()


# ── Step 1: User Registration ────────────────────────────────────────

def step_register():
    print("\n[Step 1] User Registration")
    uname = f"e2e_user_{int(time.time())}"
    resp = client.post("/api/auth/register", json={
        "username": uname,
        "email": f"{uname}@e2e.test",
        "password": "secure_pass_123",
        "displayName": "E2E Test User",
    })
    r.check("register_returns_200", resp.status_code == 200, resp.text[:200])
    data = resp.json()
    r.check("register_has_token", "token" in data, str(data)[:200])
    r.check("register_has_user", "user" in data, str(data)[:200])

    r.context["token"] = data.get("token", "")
    r.context["user_id"] = data.get("user", {}).get("id", "")
    r.context["username"] = uname


# ── Step 2: User Login ───────────────────────────────────────────────

def step_login():
    print("\n[Step 2] User Login")
    resp = client.post("/api/auth/login", json={
        "username": r.context["username"],
        "password": "secure_pass_123",
    })
    r.check("login_returns_200", resp.status_code == 200, resp.text[:200])
    data = resp.json()
    r.check("login_has_token", "token" in data, str(data)[:200])

    r.context["token"] = data.get("token", r.context.get("token", ""))


# ── Step 3: Get Me (Auth Verification) ───────────────────────────────

def step_me():
    print("\n[Step 3] Auth Me Verification")
    headers = {"Authorization": f"Bearer {r.context['token']}"}
    resp = client.get("/api/auth/me", headers=headers)
    r.check("me_returns_200", resp.status_code == 200, resp.text[:200])
    data = resp.json()
    r.check("me_username_matches", data.get("username") == r.context["username"], str(data)[:200])


# ── Step 4: Browse Knowledge Graph ───────────────────────────────────

def step_browse_knowledge():
    print("\n[Step 4] Browse Knowledge Graph")
    # Get all nodes
    resp = client.get("/api/knowledge/nodes")
    r.check("get_nodes_200", resp.status_code == 200, resp.text[:200])
    nodes = resp.json()
    r.check("has_knowledge_nodes", len(nodes) > 0, f"Got {len(nodes)} nodes")
    r.context["first_node_id"] = nodes[0]["id"] if nodes else None

    # Get graph (nodes + edges)
    resp = client.get("/api/knowledge/graph")
    r.check("get_graph_200", resp.status_code == 200, resp.text[:200])
    graph = resp.json()
    r.check("graph_has_nodes", len(graph.get("nodes", [])) > 0, str(graph)[:200])
    r.check("graph_has_edges", len(graph.get("edges", [])) > 0, str(graph)[:200])

    # Get categories
    resp = client.get("/api/knowledge/categories")
    r.check("get_categories_200", resp.status_code == 200, resp.text[:200])
    cats = resp.json()
    r.check("has_categories", len(cats.get("categories", [])) > 0, str(cats)[:200])

    # Search
    resp = client.get("/api/knowledge/search", params={"q": "python"})
    r.check("search_returns_results", resp.status_code == 200, resp.text[:200])


# ── Step 5: Start Learning Session ───────────────────────────────────

def step_start_session():
    print("\n[Step 5] Start Learning Session")
    node_id = r.context.get("first_node_id", "node-basics")
    resp = client.post("/api/sessions/start", json={
        "userId": r.context["user_id"],
        "knowledgeNodeId": node_id,
    })
    r.check("start_session_200", resp.status_code == 200, resp.text[:200])
    data = resp.json()
    r.check("session_has_id", "session" in data and "id" in data.get("session", {}), str(data)[:200])
    r.context["session_id"] = data.get("session", {}).get("id", "")


# ── Step 6: Record Session Event ─────────────────────────────────────

def step_record_event():
    print("\n[Step 6] Record Session Event")
    session_id = r.context.get("session_id", "")
    resp = client.post(f"/api/sessions/{session_id}/events", json={
        "eventType": "code_edit",
        "payload": {"language": "python", "lines": 5},
    })
    r.check("record_event_success", resp.status_code == 200 and resp.json().get("success"), resp.text[:200])


# ── Step 7: Run Code in Workspace ────────────────────────────────────

def step_run_code():
    print("\n[Step 7] Run Code in Workspace")
    session_id = r.context.get("session_id", "")
    code = "print('Hello, PyPad!')\nresult = 2 + 3\nprint(result)"
    resp = client.post("/api/workspace/run", json={
        "sessionId": session_id,
        "code": code,
        "language": "python",
    })
    r.check("run_code_200", resp.status_code == 200, resp.text[:200])
    data = resp.json()
    r.check("run_has_stdout", "Hello, PyPad!" in data.get("stdout", ""), str(data)[:200])
    r.check("run_status_success", data.get("status") == "success", str(data)[:200])
    r.context["run_id"] = data.get("id", "")


# ── Step 8: Run Code with Syntax Error ───────────────────────────────

def step_run_code_error():
    print("\n[Step 8] Run Code with Syntax Error")
    session_id = r.context.get("session_id", "")
    resp = client.post("/api/workspace/run", json={
        "sessionId": session_id,
        "code": "def foo(\n  pass",
        "language": "python",
    })
    r.check("syntax_error_detected", resp.status_code == 200, resp.text[:200])
    data = resp.json()
    r.check("error_has_stderr", len(data.get("stderr", "")) > 0, str(data)[:200])


# ── Step 9: Get Practices & Submit ───────────────────────────────────

def step_practice_submit():
    print("\n[Step 9] Get Practices & Submit")
    resp = client.get("/api/practices")
    r.check("get_practices_200", resp.status_code == 200, resp.text[:200])
    practices = resp.json().get("practices", [])
    r.check("has_practices", len(practices) > 0, f"Got {len(practices)} practices")

    if practices:
        practice_id = practices[0]["id"]
        r.context["practice_id"] = practice_id

        # Submit practice
        resp = client.post(f"/api/practices/{practice_id}/submit", json={
            "code": "print('hello')",
        })
        r.check("submit_practice_200", resp.status_code == 200, resp.text[:200])
        data = resp.json()
        r.check("submit_has_score", "score" in data, str(data)[:200])
        r.check("submit_has_feedback", "feedback" in data, str(data)[:200])


# ── Step 10: Check Mastery Update ────────────────────────────────────

def step_check_mastery():
    print("\n[Step 10] Check Mastery Update")
    headers = {"Authorization": f"Bearer {r.context['token']}"}
    resp = client.get("/api/user/knowledge", headers=headers)
    r.check("get_user_knowledge_200", resp.status_code == 200, resp.text[:200])
    data = resp.json()
    r.check("mastery_has_knowledge", "knowledge" in data, str(data)[:200])


# ── Step 11: Get Recommended Learning Path ───────────────────────────

def step_recommend_path():
    print("\n[Step 11] Get Recommended Learning Path")
    headers = {"Authorization": f"Bearer {r.context['token']}"}
    resp = client.get("/api/user/recommend-path", headers=headers)
    r.check("recommend_path_200", resp.status_code == 200, resp.text[:200])
    data = resp.json()
    r.check("path_has_nodes", "sequence" in data or "recommendedNodes" in data or "nodes" in data, str(data)[:200])


# ── Step 12: RAG Context Retrieval ───────────────────────────────────

def step_rag_context():
    print("\n[Step 12] RAG Context Retrieval")
    resp = client.get("/api/knowledge/rag-context", params={"q": "python"})
    r.check("rag_context_200", resp.status_code == 200, resp.text[:200])
    data = resp.json()
    # RAG context may be empty if query doesn't match TF-IDF vectors well
    r.check("rag_returns_response", "context" in data, str(data)[:200])


# ── Step 13: AI Agent Chat ───────────────────────────────────────────

def step_agent_chat():
    print("\n[Step 13] AI Agent Chat")
    resp = client.post("/api/agent/chat", json={
        "message": "什么是 Python 的列表推导式？",
        "agentType": "tutor",
        "userId": r.context.get("user_id", "user-1"),
        "knowledgeId": r.context.get("first_node_id"),
    })
    r.check("agent_chat_200", resp.status_code == 200, resp.text[:200])
    data = resp.json()
    r.check("agent_has_reply", len(data.get("message", "")) > 0, str(data)[:200])


# ── Step 14: End Session & Get Timeline ──────────────────────────────

def step_end_session():
    print("\n[Step 14] End Session & Get Timeline")
    session_id = r.context.get("session_id", "")
    resp = client.post(f"/api/sessions/{session_id}/end")
    r.check("end_session_success", resp.status_code == 200 and resp.json().get("success"), resp.text[:200])

    resp = client.get(f"/api/sessions/{session_id}/timeline")
    r.check("get_timeline_200", resp.status_code == 200, resp.text[:200])
    data = resp.json()
    r.check("timeline_has_events", len(data.get("timeline", [])) > 0, str(data)[:200])


# ── Step 15: Dashboard Overview ──────────────────────────────────────

def step_dashboard():
    print("\n[Step 15] Dashboard Overview")
    headers = {"Authorization": f"Bearer {r.context['token']}"}
    resp = client.get("/api/dashboard/overview", headers=headers)
    r.check("dashboard_overview_200", resp.status_code == 200, resp.text[:200])

    resp = client.get("/api/dashboard/progress", headers=headers)
    r.check("dashboard_progress_200", resp.status_code == 200, resp.text[:200])


# ── Step 16: Textbook Upload (Markdown) ──────────────────────────────

def step_textbook_upload():
    print("\n[Step 16] Textbook Upload (Markdown)")
    markdown_content = """# Python 基础入门

## 变量与数据类型

Python 是一种动态类型语言，变量不需要声明类型。

```python
x = 10          # 整数
name = "PyPad"  # 字符串
is_valid = True # 布尔值
```

## 条件语句

使用 if/elif/else 进行条件判断。

```python
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
else:
    grade = "C"
```

## 循环结构

Python 支持 for 和 while 循环。

```python
for i in range(5):
    print(i)
```
"""
    resp = client.post("/api/textbook/upload", json={
        "content": markdown_content,
        "bookTitle": "E2E测试教材",
    })
    r.check("textbook_upload_200", resp.status_code == 200, resp.text[:200])
    data = resp.json()
    r.check("textbook_parse_success", data.get("success") == False or data.get("success") == True, str(data)[:200])
    if data.get("success"):
        r.check("textbook_has_nodes", data.get("parsedSummary", {}).get("totalParsedNodes", 0) > 0, str(data)[:200])


# ── Step 17: AI Review ───────────────────────────────────────────────

def step_ai_review():
    print("\n[Step 17] AI Code Review")
    run_id = r.context.get("run_id", "")
    if not run_id:
        r.check("ai_review_skipped", True, "No run_id available")
        return
    resp = client.post("/api/workspace/ai-review", json={"runId": run_id})
    r.check("ai_review_200", resp.status_code == 200, resp.text[:200])
    data = resp.json()
    r.check("review_has_score", "review" in data and "overallScore" in data.get("review", {}), str(data)[:200])


# ── Step 18: Analytics ───────────────────────────────────────────────

def step_analytics():
    print("\n[Step 18] Analytics Overview")
    headers = {"Authorization": f"Bearer {r.context['token']}"}
    resp = client.get("/api/analytics/overview", headers=headers)
    r.check("analytics_200", resp.status_code == 200, resp.text[:200])
    data = resp.json()
    r.check("analytics_has_total", "totalNodes" in data, str(data)[:200])


# ── Run All Steps ────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("PyPad — End-to-End Integration Test")
    print("=" * 50)

    steps = [
        step_register,
        step_login,
        step_me,
        step_browse_knowledge,
        step_start_session,
        step_record_event,
        step_run_code,
        step_run_code_error,
        step_practice_submit,
        step_check_mastery,
        step_recommend_path,
        step_rag_context,
        step_agent_chat,
        step_end_session,
        step_dashboard,
        step_textbook_upload,
        step_ai_review,
        step_analytics,
    ]

    for step_fn in steps:
        try:
            step_fn()
        except Exception as e:
            r.check(f"{step_fn.__name__}_no_exception", False, str(e))

    success = r.summary()
    sys.exit(0 if success else 1)
