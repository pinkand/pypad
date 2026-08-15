from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager
import subprocess
import sys

from sqlmodel import Session, select

from database import engine, create_db_and_tables, get_session
from llm_service import chat as llm_chat, chat_stream_generator
from auth import hash_password, verify_password, create_token, decode_token
from models import (
    Course, Chapter, Section,
    KnowledgeNode, KnowledgeEdge,
    Project, Practice,
    LearningSession, SessionEventLog,
    WorkspaceRun, CodeReview,
    UserMastery, UserProgress, StudyRecord, User, ChatMessage,
    TreeNodeResponse, GraphResponse, EdgeResponse,
)
from routers.graph import router as graph_router


from rag_service import rag_engine


# ──────────────────────────────────────────────
# Lifespan: create tables + seed + RAG Index on startup
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    _auto_seed()
    _index_rag_nodes()
    yield

def _auto_seed():
    """Run seed.py if the knowledge_nodes table is empty."""
    with Session(engine) as session:
        existing = session.exec(select(KnowledgeNode).limit(1)).first()
        if not existing:
            print("[startup] knowledge_nodes is empty — running seed.py …")
            subprocess.run([sys.executable, "seed.py"], check=True)

def _index_rag_nodes():
    """Index knowledge nodes into vector RAG engine."""
    with Session(engine) as session:
        nodes = session.exec(select(KnowledgeNode)).all()
        node_dicts = []
        for n in nodes:
            node_dicts.append({
                "id": n.id,
                "name": n.name,
                "description": n.description,
                "category": n.category,
                "aiSummary": n.ai_summary if hasattr(n, 'ai_summary') and n.ai_summary else getattr(n, 'aiSummary', {}),
            })
        rag_engine.index_knowledge_nodes(node_dicts)
        print(f"[startup] Vector RAG engine indexed {len(node_dicts)} knowledge nodes.")

app = FastAPI(title="PyPad API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the graph router
app.include_router(graph_router)


# ──────────────────────────────────────────────
# Auth dependency
# ──────────────────────────────────────────────
def get_current_user_id(request: Request) -> Optional[str]:
    """Extract user_id from Authorization header. Returns None if no/invalid token."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        payload = decode_token(auth[7:])
        if payload:
            return payload.get("sub")
    return None


def require_user(request: Request, session: Session = Depends(get_session)) -> User:
    """Dependency: require a valid JWT and return the User object."""
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(401, "Not authenticated")
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(401, "User not found")
    return user


# ──────────────────────────────────────────────
# 0. Auth API
# ──────────────────────────────────────────────
class RegisterReq(BaseModel):
    username: str
    email: str
    password: str
    displayName: Optional[str] = None

class LoginReq(BaseModel):
    username: str
    password: str

@app.post("/api/auth/register")
def register(req: RegisterReq, session: Session = Depends(get_session)):
    # Check duplicates
    existing = session.exec(select(User).where(
        (User.username == req.username) | (User.email == req.email)
    )).first()
    if existing:
        raise HTTPException(400, "Username or email already taken")

    user_id = f"user-{int(datetime.utcnow().timestamp())}"
    user = User(
        id=user_id, username=req.username, email=req.email,
        password_hash=hash_password(req.password),
        display_name=req.displayName or req.username,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    token = create_token({"sub": user_id, "username": req.username})
    return {
        "token": token,
        "user": {
            "id": user.id, "username": user.username, "email": user.email,
            "displayName": user.display_name, "level": user.level,
            "experience": user.experience, "streak": user.streak,
        },
    }

@app.post("/api/auth/login")
def login(req: LoginReq, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == req.username)).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(401, "Invalid username or password")

    token = create_token({"sub": user.id, "username": user.username})
    return {
        "token": token,
        "user": {
            "id": user.id, "username": user.username, "email": user.email,
            "displayName": user.display_name, "level": user.level,
            "experience": user.experience, "streak": user.streak,
        },
    }

@app.get("/api/auth/me")
def get_me(user: User = Depends(require_user)):
    return {
        "id": user.id, "username": user.username, "email": user.email,
        "displayName": user.display_name, "level": user.level,
        "experience": user.experience, "streak": user.streak,
    }


# ──────────────────────────────────────────────
# Helper: dict-ify an ORM row for JSON response
# ──────────────────────────────────────────────
def _course_dict(c: Course) -> dict:
    return {
        "id": c.id, "title": c.title, "description": c.description,
        "level": c.level, "category": c.category, "sortOrder": c.sort_order,
        "createdAt": c.created_at.isoformat() if c.created_at else None,
        "updatedAt": c.updated_at.isoformat() if c.updated_at else None,
    }

def _chapter_dict(ch: Chapter) -> dict:
    return {
        "id": ch.id, "courseId": ch.course_id, "title": ch.title,
        "description": ch.description, "sortOrder": ch.sort_order,
    }

def _section_dict(s: Section) -> dict:
    return {
        "id": s.id, "chapterId": s.chapter_id, "title": s.title,
        "contentType": s.content_type, "estimatedMinutes": s.estimated_minutes,
        "sortOrder": s.sort_order,
    }

def _node_dict(n: KnowledgeNode) -> dict:
    return {
        "id": n.id, "code": n.code, "name": n.name,
        "description": n.description, "category": n.category,
        "importance": n.importance, "parentId": n.parent_id,
        "depth": n.depth, "sortOrder": n.sort_order,
        "position": {"x": n.pos_x, "y": n.pos_y, "z": n.pos_z},
        "courseId": n.course_id, "chapterId": n.chapter_id,
        "sectionId": n.section_id,
        "aiSummary": n.ai_summary,
    }

def _edge_dict(e: KnowledgeEdge) -> dict:
    return {
        "id": f"{e.source_id}-{e.target_id}",
        "source": e.source_id, "target": e.target_id,
        "relationType": e.relation_type,
        "strength": e.strength, "weight": e.weight,
    }

def _project_dict(p: Project) -> dict:
    return {
        "id": p.id, "title": p.title, "description": p.description,
        "difficulty": p.difficulty, "estimatedHours": p.estimated_hours,
        "initCode": p.init_code, "readmeMarkdown": p.readme_markdown,
        "testCases": p.test_cases,
        "createdAt": p.created_at.isoformat() if p.created_at else None,
    }

def _practice_dict(p: Practice) -> dict:
    return {
        "id": p.id, "title": p.title, "type": p.type,
        "difficulty": p.difficulty, "knowledgeNodeId": p.knowledge_node_id,
        "prompt": p.prompt, "starterCode": p.starter_code,
        "solutionCode": p.solution_code, "testCases": p.test_cases,
    }

def _session_dict(s: LearningSession) -> dict:
    return {
        "id": s.id, "userId": s.user_id, "courseId": s.course_id,
        "chapterId": s.chapter_id, "sectionId": s.section_id,
        "knowledgeNodeId": s.knowledge_node_id, "status": s.status,
        "startTime": s.start_time.isoformat() if s.start_time else None,
        "endTime": s.end_time.isoformat() if s.end_time else None,
        "totalDurationSeconds": s.total_duration_seconds,
    }

def _run_dict(r: WorkspaceRun) -> dict:
    return {
        "id": r.id, "sessionId": r.session_id, "practiceId": r.practice_id,
        "code": r.code, "language": r.language, "status": r.status,
        "stdout": r.stdout, "stderr": r.stderr, "exitCode": r.exit_code,
        "runtimeMs": r.runtime_ms, "memoryBytes": r.memory_bytes,
        "createdAt": r.created_at.isoformat() if r.created_at else None,
    }

def _review_dict(cr: CodeReview) -> dict:
    return {
        "id": cr.id, "workspaceRunId": cr.workspace_run_id,
        "sessionId": cr.session_id, "overallScore": cr.overall_score,
        "codeQualityScore": cr.code_quality_score,
        "logicScore": cr.logic_score, "performanceScore": cr.performance_score,
        "aiFeedback": cr.ai_feedback, "suggestions": cr.suggestions,
        "weaknessTags": cr.weakness_tags,
        "createdAt": cr.created_at.isoformat() if cr.created_at else None,
    }


# ──────────────────────────────────────────────
# 1. Courses Domain API
# ──────────────────────────────────────────────
@app.get("/api/courses")
def get_courses(session: Session = Depends(get_session)):
    courses = session.exec(select(Course).order_by(Course.sort_order)).all()
    return {"courses": [_course_dict(c) for c in courses]}

@app.get("/api/courses/{course_id}")
def get_course(course_id: str, session: Session = Depends(get_session)):
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    return {"course": _course_dict(course)}

@app.get("/api/courses/{course_id}/tree")
def get_course_tree(course_id: str, session: Session = Depends(get_session)):
    chapters = session.exec(
        select(Chapter).where(Chapter.course_id == course_id).order_by(Chapter.sort_order)
    ).all()
    return {"courseId": course_id, "chapters": [_chapter_dict(ch) for ch in chapters]}


# ──────────────────────────────────────────────
# 2. Chapters & Sections Domain API
# ──────────────────────────────────────────────
@app.get("/api/chapters")
def get_chapters(courseId: Optional[str] = None, session: Session = Depends(get_session)):
    stmt = select(Chapter)
    if courseId:
        stmt = stmt.where(Chapter.course_id == courseId)
    chapters = session.exec(stmt.order_by(Chapter.sort_order)).all()
    return {"chapters": [_chapter_dict(ch) for ch in chapters]}

@app.get("/api/chapters/{chapter_id}/sections")
def get_sections(chapter_id: str, session: Session = Depends(get_session)):
    sections = session.exec(
        select(Section).where(Section.chapter_id == chapter_id).order_by(Section.sort_order)
    ).all()
    return {"sections": [_section_dict(s) for s in sections]}


# ──────────────────────────────────────────────
# 3. Knowledge Graph & Node Domain API
# ──────────────────────────────────────────────
@app.get("/api/knowledge/nodes")
def get_knowledge_nodes(session: Session = Depends(get_session)):
    nodes = session.exec(select(KnowledgeNode)).all()
    return [_node_dict(n) for n in nodes]

@app.get("/api/knowledge/nodes/{node_id}")
def get_knowledge_node(node_id: str, session: Session = Depends(get_session)):
    node = session.get(KnowledgeNode, node_id)
    if not node:
        raise HTTPException(404, "Knowledge node not found")
    return _node_dict(node)

@app.get("/api/knowledge/graph")
def get_knowledge_graph(session: Session = Depends(get_session)):
    nodes = session.exec(select(KnowledgeNode)).all()
    edges = session.exec(select(KnowledgeEdge)).all()
    return {
        "nodes": [_node_dict(n) for n in nodes],
        "edges": [_edge_dict(e) for e in edges],
    }

@app.get("/api/knowledge/relations")
def get_knowledge_relations(session: Session = Depends(get_session)):
    edges = session.exec(select(KnowledgeEdge)).all()
    return [_edge_dict(e) for e in edges]

@app.get("/api/knowledge/categories")
def get_knowledge_categories(session: Session = Depends(get_session)):
    nodes = session.exec(select(KnowledgeNode)).all()
    categories = list({n.category for n in nodes if n.category})
    return {"categories": categories}

@app.post("/api/knowledge/nodes/{node_id}/ai-summary")
def generate_node_summary(node_id: str, session: Session = Depends(get_session)):
    node = session.get(KnowledgeNode, node_id)
    if not node:
        raise HTTPException(404, "Knowledge node not found")
    summary = node.ai_summary or {
        "overview": f"{node.name} 核心知识点精要总结",
        "keyPoints": ["核心原理", "底层逻辑", "性能调优"],
        "commonPitfalls": ["类型转换误区", "内存泄露"],
    }
    return {"nodeId": node_id, "aiSummary": summary}

@app.get("/api/knowledge/search")
def search_knowledge(q: str = "", session: Session = Depends(get_session)):
    """Keyword search across knowledge nodes. Used for RAG context retrieval."""
    if not q:
        return {"results": []}
    q_lower = q.lower()
    nodes = session.exec(select(KnowledgeNode)).all()
    scored = []
    for n in nodes:
        score = 0
        if q_lower in n.name.lower():
            score += 10
        if q_lower in (n.description or "").lower():
            score += 5
        if q_lower in (n.category or "").lower():
            score += 3
        if score > 0:
            scored.append((score, n))
    scored.sort(key=lambda x: -x[0])
    return {"results": [
        {"id": n.id, "name": n.name, "description": n.description,
         "category": n.category, "importance": n.importance, "score": s}
        for s, n in scored[:10]
    ]}

@app.get("/api/knowledge/rag-context")
def get_rag_context(q: str = "", session: Session = Depends(get_session)):
    """Return knowledge context string for LLM augmentation."""
    if not q:
        return {"context": ""}
    q_lower = q.lower()
    nodes = session.exec(select(KnowledgeNode)).all()
    scored = []
    for n in nodes:
        score = 0
        if q_lower in n.name.lower(): score += 10
        if q_lower in (n.description or "").lower(): score += 5
        if q_lower in (n.category or "").lower(): score += 3
        if score > 0: scored.append((score, n))
    scored.sort(key=lambda x: -x[0])
    context_parts = []
    for s, n in scored[:5]:
        context_parts.append(f"【{n.name}】{n.description}")
    return {"context": "\n".join(context_parts)}


# ──────────────────────────────────────────────
# 4. Projects Domain API
# ──────────────────────────────────────────────
@app.get("/api/projects")
def get_projects(session: Session = Depends(get_session)):
    projects = session.exec(select(Project)).all()
    return {"projects": [_project_dict(p) for p in projects]}

@app.get("/api/projects/{project_id}")
def get_project(project_id: str, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return {"project": _project_dict(project)}


# ──────────────────────────────────────────────
# 5. Practices Domain API
# ──────────────────────────────────────────────
class PracticeGenReq(BaseModel):
    knowledgeId: str
    difficulty: str = "medium"

class PracticeSubmitReq(BaseModel):
    code: str

@app.get("/api/practices")
def get_practices(knowledgeId: Optional[str] = None, session: Session = Depends(get_session)):
    stmt = select(Practice)
    if knowledgeId:
        stmt = stmt.where(Practice.knowledge_node_id == knowledgeId)
    practices = session.exec(stmt).all()
    return {"practices": [_practice_dict(p) for p in practices]}

@app.get("/api/practices/{practice_id}")
def get_practice(practice_id: str, session: Session = Depends(get_session)):
    practice = session.get(Practice, practice_id)
    if not practice:
        raise HTTPException(404, "Practice not found")
    return {"practice": _practice_dict(practice)}

@app.post("/api/practices/generate-ai")
def generate_ai_practice(req: PracticeGenReq, session: Session = Depends(get_session)):
    node = session.get(KnowledgeNode, req.knowledgeId)
    node_name = node.name if node else req.knowledgeId
    node_desc = node.description if node else ""

    prompt = f"""为知识点「{node_name}」生成一道 {req.difficulty} 难度的 Python 编程练习题。
知识点描述: {node_desc}

请严格按以下 JSON 格式返回（不要有其他文字）：
{{"title": "题目标题", "prompt": "题目描述（中文）", "starterCode": "初始代码", "solutionCode": "参考答案", "testCases": [{{"input": "", "expectedOutput": "期望输出"}}]}}"""

    try:
        ai_reply = llm_chat(prompt)
        import json as _json
        parsed = _json.loads(ai_reply.strip().strip("`").removeprefix("json"))
        title = parsed.get("title", f"{node_name} 练习")
        practice_prompt = parsed.get("prompt", f"基于 {node_name} 的练习")
        starter = parsed.get("starter_code", parsed.get("starterCode", "# Your code here\n"))
        solution = parsed.get("solution_code", parsed.get("solutionCode", ""))
        tests = parsed.get("testCases", parsed.get("test_cases", [{"input": "", "expectedOutput": ""}]))
    except Exception:
        title = f"{node_name} 练习"
        practice_prompt = f"编写一个与 {node_name} 相关的 Python 函数"
        starter = f"# {node_name} 练习\n# TODO: 在此编写代码\n\ndef solution():\n    pass\n"
        solution = ""
        tests = [{"input": "", "expectedOutput": ""}]

    new_prac = Practice(
        id=f"prac-ai-{int(datetime.utcnow().timestamp())}",
        title=title, type="ai_generated", difficulty=req.difficulty,
        knowledge_node_id=req.knowledgeId, prompt=practice_prompt,
        starter_code=starter, solution_code=solution, test_cases=tests,
    )
    session.add(new_prac)
    session.commit()
    session.refresh(new_prac)
    return {"practice": _practice_dict(new_prac)}

@app.post("/api/practices/{practice_id}/submit")
def submit_practice(practice_id: str, req: PracticeSubmitReq, request: Request, session: Session = Depends(get_session)):
    import subprocess, tempfile, os
    practice = session.get(Practice, practice_id)
    if not practice:
        raise HTTPException(404, "Practice not found")

    test_cases = practice.test_cases or []
    if not test_cases:
        return {"practiceId": practice_id, "passed": True, "score": 100,
                "feedback": "无测试用例，代码已提交。"}

    passed_count = 0
    total = len(test_cases)
    details = []

    for tc in test_cases:
        tc_input = tc.get("input", "")
        expected = tc.get("expectedOutput", "")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(req.code)
            if tc_input:
                f.write(f"\n# test input\nprint({tc_input})" if not tc_input.startswith("print") else f"\n{tc_input}")
            tmp_path = f.name
        try:
            result = subprocess.run(
                ["python3", tmp_path], capture_output=True, text=True, timeout=5,
            )
            actual = result.stdout.strip()
            ok = actual == expected.strip() if expected else (result.returncode == 0)
            if ok:
                passed_count += 1
            details.append({"input": tc_input, "expected": expected, "actual": actual, "passed": ok})
        except Exception as e:
            details.append({"input": tc_input, "expected": expected, "actual": str(e), "passed": False})
        finally:
            os.unlink(tmp_path)

    score = int(passed_count / total * 100)
    passed = passed_count == total
    feedback = f"通过 {passed_count}/{total} 个测试用例" + ("，全部通过！" if passed else "，请检查未通过的用例。")

    # Auto-update mastery
    if practice.knowledge_node_id:
        user_id = get_current_user_id(request) or "user-1"
        existing = session.exec(
            select(UserMastery).where(
                UserMastery.user_id == user_id,
                UserMastery.knowledge_node_id == practice.knowledge_node_id,
            )
        ).first()
        if existing:
            existing.mastery_score = max(existing.mastery_score, score)
            existing.status = "mastered" if score >= 90 else "learning" if score >= 60 else "weak"
            existing.last_studied_at = datetime.utcnow()
        else:
            session.add(UserMastery(
                user_id=user_id, knowledge_node_id=practice.knowledge_node_id,
                mastery_score=score,
                status="mastered" if score >= 90 else "learning" if score >= 60 else "weak",
                last_studied_at=datetime.utcnow(),
            ))
        session.commit()

    return {"practiceId": practice_id, "passed": passed, "score": score,
            "feedback": feedback, "details": details}


# ──────────────────────────────────────────────
# 6. Sessions Domain API
# ──────────────────────────────────────────────
class StartSessionReq(BaseModel):
    userId: str = "user-1"
    knowledgeNodeId: str
    courseId: Optional[str] = None
    chapterId: Optional[str] = None
    sectionId: Optional[str] = None

class EventLogReq(BaseModel):
    eventType: str
    payload: Dict[str, Any] = {}

@app.post("/api/sessions/start")
def start_session(req: StartSessionReq, session: Session = Depends(get_session)):
    sid = f"sess-{int(datetime.utcnow().timestamp())}"
    ls = LearningSession(
        id=sid, user_id=req.userId, course_id=req.courseId,
        chapter_id=req.chapter_id if hasattr(req, 'chapter_id') else req.chapterId,
        section_id=req.sectionId,
        knowledge_node_id=req.knowledgeNodeId,
        status="active",
    )
    session.add(ls)
    session.commit()
    session.refresh(ls)
    result = _session_dict(ls)
    result["eventLogs"] = []
    result["workspaceRuns"] = []
    result["reviews"] = []
    return {"session": result}

@app.post("/api/sessions/{session_id}/events")
def record_session_event(session_id: str, req: EventLogReq, session: Session = Depends(get_session)):
    ls = session.get(LearningSession, session_id)
    if not ls:
        return {"success": False, "message": "Session not found"}
    evt = SessionEventLog(
        session_id=session_id, event_type=req.eventType,
        payload=req.payload,
    )
    session.add(evt)
    session.commit()
    return {"success": True, "event": {
        "id": evt.id, "sessionId": session_id,
        "eventType": req.eventType, "payload": req.payload,
        "timestamp": evt.timestamp.isoformat(),
    }}

@app.post("/api/sessions/{session_id}/end")
def end_session(session_id: str, session: Session = Depends(get_session)):
    ls = session.get(LearningSession, session_id)
    if ls:
        ls.status = "completed"
        ls.end_time = datetime.utcnow()
        session.add(ls)
        session.commit()
    return {"success": True}

@app.get("/api/sessions/{session_id}/timeline")
def get_session_timeline(session_id: str, session: Session = Depends(get_session)):
    ls = session.get(LearningSession, session_id)
    if not ls:
        raise HTTPException(404, "Session not found")
    events = session.exec(
        select(SessionEventLog).where(SessionEventLog.session_id == session_id)
    ).all()
    return {"timeline": [
        {"id": e.id, "sessionId": e.session_id, "eventType": e.event_type,
         "payload": e.payload, "timestamp": e.timestamp.isoformat()}
        for e in events
    ]}


# ──────────────────────────────────────────────
# 7. Workspace Domain API
# ──────────────────────────────────────────────
class RunCodeReq(BaseModel):
    sessionId: str
    code: str
    language: str = "python"
    practiceId: Optional[str] = None

class AIReviewReq(BaseModel):
    runId: str

from sandbox_runner import execute_sandboxed

@app.post("/api/workspace/run")
def run_code(req: RunCodeReq, session: Session = Depends(get_session)):
    run_id = f"run-{int(datetime.utcnow().timestamp())}"

    if req.language == "python":
        res = execute_sandboxed(req.code, timeout_sec=5.0)
        status = res["status"]
        stdout_buf = res["stdout"]
        stderr_buf = res["stderr"]
        exit_code = res["exitCode"]
        runtime_ms = res["runtimeMs"]
        error_detail = res.get("errorDetail")
    else:
        status = "runtime_error"
        stdout_buf = ""
        stderr_buf = f"不支持的编程语言: {req.language}"
        exit_code = -1
        runtime_ms = 0
        error_detail = None

    run = WorkspaceRun(
        id=run_id, session_id=req.sessionId, practice_id=req.practiceId,
        code=req.code, language=req.language, status=status,
        stdout=stdout_buf, stderr=stderr_buf, exit_code=exit_code,
        runtime_ms=runtime_ms, memory_bytes=0,
    )
    try:
        session.add(run)
        session.commit()
        session.refresh(run)
    except Exception:
        session.rollback()
    
    run_res = _run_dict(run)
    if error_detail:
        run_res["errorDetail"] = error_detail
    return run_res


@app.get("/api/workspace/runs/{session_id}")
def get_run_history(session_id: str, session: Session = Depends(get_session)):
    runs = session.exec(
        select(WorkspaceRun).where(WorkspaceRun.session_id == session_id)
    ).all()
    return {"runs": [_run_dict(r) for r in runs]}

@app.post("/api/workspace/ai-review")
def request_ai_review(req: AIReviewReq, session: Session = Depends(get_session)):
    run = session.get(WorkspaceRun, req.runId)
    if not run:
        raise HTTPException(404, "Run not found")

    prompt = f"""审查以下 Python 代码，给出评分和建议。严格按 JSON 返回（不要有其他文字）：
代码:
```
{run.code}
```
执行结果: exit_code={run.exit_code}, stdout={run.stdout[:200] if run.stdout else ''}, stderr={run.stderr[:200] if run.stderr else ''}

返回格式:
{{"overallScore": 0-100, "codeQualityScore": 0-100, "logicScore": 0-100, "performanceScore": 0-100, "feedback": "总体评价（中文）", "suggestions": ["建议1", "建议2"], "weaknessTags": ["薄弱点1"]}}"""

    try:
        ai_reply = llm_chat(prompt)
        import json as _json
        parsed = _json.loads(ai_reply.strip().strip("`").removeprefix("json"))
        review = CodeReview(
            id=f"rev-{int(datetime.utcnow().timestamp())}",
            workspace_run_id=req.runId, session_id=run.session_id,
            overall_score=parsed.get("overallScore", 80),
            code_quality_score=parsed.get("codeQualityScore", 80),
            logic_score=parsed.get("logicScore", 80),
            performance_score=parsed.get("performanceScore", 80),
            ai_feedback=parsed.get("feedback", "代码审查完成"),
            suggestions=parsed.get("suggestions", []),
            weakness_tags=parsed.get("weaknessTags", []),
        )
    except Exception:
        review = CodeReview(
            id=f"rev-{int(datetime.utcnow().timestamp())}",
            workspace_run_id=req.runId, session_id=run.session_id,
            overall_score=80, code_quality_score=80, logic_score=80, performance_score=80,
            ai_feedback="代码审查完成（LLM 解析失败，使用默认评分）",
            suggestions=["建议添加类型注解", "增加异常处理"],
            weakness_tags=["代码规范"],
        )

    session.add(review)
    session.commit()
    session.refresh(review)
    return {"review": _review_dict(review)}


# ──────────────────────────────────────────────
# 8. Reviews & Dashboard Domain API
# ──────────────────────────────────────────────
@app.get("/api/reviews/{review_id}")
def get_review(review_id: str, session: Session = Depends(get_session)):
    review = session.get(CodeReview, review_id)
    if not review:
        raise HTTPException(404, "Review not found")
    return {"review": _review_dict(review)}

@app.get("/api/reviews/user/{user_id}")
def get_user_reviews(user_id: str, session: Session = Depends(get_session)):
    reviews = session.exec(select(CodeReview)).all()
    return {"reviews": [_review_dict(r) for r in reviews]}

@app.get("/api/dashboard/overview")
def get_dashboard_overview(request: Request, userId: Optional[str] = None, session: Session = Depends(get_session)):
    if not userId:
        userId = get_current_user_id(request) or "user-1"
    progress = session.get(UserProgress, userId)
    if progress:
        return {
            "overallMastery": progress.overall_mastery,
            "studyStreakDays": progress.study_streak_days,
            "completedProjectsCount": progress.completed_projects_count,
            "completedPracticesCount": progress.completed_practices_count,
            "totalStudyTimeSeconds": progress.total_study_time_seconds,
            "weakKnowledgeNodeIds": progress.weak_node_ids or [],
        }
    return {
        "overallMastery": 0, "studyStreakDays": 0,
        "completedProjectsCount": 0, "completedPracticesCount": 0,
        "totalStudyTimeSeconds": 0, "weakKnowledgeNodeIds": [],
    }

@app.get("/api/dashboard/progress")
def get_dashboard_progress(request: Request, userId: Optional[str] = None, session: Session = Depends(get_session)):
    if not userId:
        userId = get_current_user_id(request) or "user-1"
    progress = session.get(UserProgress, userId)
    if progress:
        return {
            "userId": userId,
            "currentCourseId": progress.current_course_id,
            "streak": progress.study_streak_days,
            "level": max(1, int(progress.overall_mastery / 20) + 1),
        }
    return {"userId": userId, "currentCourseId": None, "streak": 0, "level": 1}


# ──────────────────────────────────────────────
# 9. User Knowledge & Study Records
# ──────────────────────────────────────────────
@app.get("/api/user/knowledge")
def get_user_knowledge(request: Request, user_id: Optional[str] = None, session: Session = Depends(get_session)):
    if not user_id:
        user_id = get_current_user_id(request) or "user-1"
    masteries = session.exec(
        select(UserMastery).where(UserMastery.user_id == user_id)
    ).all()
    
    # 艾宾浩斯记忆遗忘曲线衰减算法: R(t) = score * e^(-Δt / 7)
    import math
    now = datetime.utcnow()
    knowledge = {}
    for m in masteries:
        days_elapsed = (now - m.last_studied_at).total_seconds() / 86400.0
        decay_factor = math.exp(-days_elapsed / 7.0)
        decayed_score = max(0, min(100, int(m.mastery_score * decay_factor)))
        knowledge[m.knowledge_node_id] = decayed_score

    return {"userId": user_id, "knowledge": knowledge}


from topological_path import generate_topological_learning_path


@app.get("/api/user/recommend-path")
def get_recommended_learning_path(request: Request, user_id: Optional[str] = None, session: Session = Depends(get_session)):
    if not user_id:
        user_id = get_current_user_id(request) or "user-1"

    nodes = session.exec(select(KnowledgeNode)).all()
    edges = session.exec(select(KnowledgeEdge)).all()
    masteries = session.exec(select(UserMastery).where(UserMastery.user_id == user_id)).all()

    node_dicts = [{"id": n.id, "name": n.name, "category": n.category, "importance": n.importance} for n in nodes]
    edge_dicts = [{"source": e.source_id, "target": e.target_id, "relationType": e.relation_type} for e in edges]
    mastery_dict = {m.knowledge_node_id: m.mastery_score for m in masteries}

    path = generate_topological_learning_path(node_dicts, edge_dicts, mastery_dict)
    return path


from textbook_parser import parse_markdown_textbook

@app.post("/api/textbook/upload")
async def upload_textbook(request: Request, session: Session = Depends(get_session)):
    data = await request.json()
    content = data.get("content", "")
    book_title = data.get("bookTitle", "自定义教材")

    if not content:
        return {"success": False, "message": "教材内容为空"}

    parsed = parse_markdown_textbook(content, book_title=book_title)
    
    # Save parsed nodes and edges to DB
    new_nodes_count = 0
    for node_data in parsed["nodes"]:
        existing = session.get(KnowledgeNode, node_data["id"])
        if not existing:
            session.add(KnowledgeNode(
                id=node_data["id"],
                name=node_data["name"],
                category=node_data["category"],
                description=node_data["description"],
                importance=node_data.get("importance", 4),
                ai_summary=node_data["aiSummary"]
            ))
            new_nodes_count += 1

    for edge_data in parsed["edges"]:
        existing_e = session.exec(select(KnowledgeEdge).where(
            KnowledgeEdge.source_id == edge_data["source"],
            KnowledgeEdge.target_id == edge_data["target"]
        )).first()
        if not existing_e:
            session.add(KnowledgeEdge(
                source_id=edge_data["source"],
                target_id=edge_data["target"],
                relation_type=edge_data.get("relationType", "prerequisite")
            ))

    session.commit()
    
    # Refresh Vector RAG Engine index with newly added nodes
    _index_rag_nodes()

    return {
        "success": True,
        "message": f"成功解析教材《{book_title}》，导入 {new_nodes_count} 个知识节点",
        "parsedSummary": parsed
    }

@app.post("/api/user/knowledge")
def update_user_knowledge(data: Dict[str, Any], session: Session = Depends(get_session)):
    user_id = data.get("userId", "user-1")
    node_id = data.get("knowledgeId")
    score = data.get("masteryScore", 0)
    if not node_id:
        return {"success": False, "message": "knowledgeId required"}
    existing = session.exec(
        select(UserMastery).where(
            UserMastery.user_id == user_id,
            UserMastery.knowledge_node_id == node_id,
        )
    ).first()
    if existing:
        existing.mastery_score = score
        existing.last_studied_at = datetime.utcnow()
        session.add(existing)
    else:
        session.add(UserMastery(
            user_id=user_id, knowledge_node_id=node_id,
            mastery_score=score, last_studied_at=datetime.utcnow(),
        ))
    session.commit()
    return {"success": True}

@app.post("/api/user/study")
def record_study(data: Dict[str, Any], session: Session = Depends(get_session)):
    user_id = data.get("userId", "user-1")
    node_id = data.get("knowledgeId")
    duration = data.get("duration", 0)
    behavior = data.get("behavior", "read")
    if node_id:
        session.add(StudyRecord(
            user_id=user_id, knowledge_node_id=node_id,
            duration_seconds=duration, behavior=behavior,
        ))
        session.commit()
    return {"success": True}

@app.get("/api/user/study-records")
def get_study_records(request: Request, user_id: Optional[str] = None, limit: int = 10, session: Session = Depends(get_session)):
    if not user_id:
        user_id = get_current_user_id(request) or "user-1"
    records = session.exec(
        select(StudyRecord).where(StudyRecord.user_id == user_id)
        .order_by(StudyRecord.created_at.desc()).limit(limit)
    ).all()
    return {"records": [
        {"id": r.id, "userId": r.user_id, "knowledgeNodeId": r.knowledge_node_id,
         "duration": r.duration_seconds, "behavior": r.behavior,
         "createdAt": r.created_at.isoformat()}
        for r in records
    ]}


# ──────────────────────────────────────────────
# 10. Agent API
# ──────────────────────────────────────────────
AGENT_SYSTEM_PROMPTS = {
    "tutor": "你是 Python 导师。用简洁中文讲解知识点，给代码示例时附注释，鼓励动手实践。",
    "planner": "你是学习规划师。根据用户目标制定学习路径，列出知识点和时间安排。",
    "coder": "你是编程教练。帮用户写代码、调试、优化，给出最佳实践建议。",
    "practice": "你是出题官。根据知识点生成练习题，包含题目描述、 starter code 和测试用例。",
    "memory": "你是学习分析师。分析用户学习记录，找出薄弱点，推荐复习计划。",
}

@app.get("/api/agent/history")
def get_agent_history(request: Request, agentType: str = "tutor", limit: int = 50, session: Session = Depends(get_session)):
    user_id = get_current_user_id(request) or "user-1"
    messages = session.exec(
        select(ChatMessage).where(
            ChatMessage.user_id == user_id,
            ChatMessage.agent_type == agentType,
        ).order_by(ChatMessage.created_at.desc()).limit(limit)
    ).all()
    messages.reverse()
    return {"messages": [
        {"id": m.id, "role": m.role, "content": m.content,
         "agentType": m.agent_type, "knowledgeNodeId": m.knowledge_node_id,
         "createdAt": m.created_at.isoformat()}
        for m in messages
    ]}

@app.post("/api/agent/chat")
def chat_with_agent(request: Dict[str, Any], session: Session = Depends(get_session)):
    msg = request.get("message", "")
    agent_type = request.get("agentType", "tutor")
    user_id = request.get("userId", "user-1")
    knowledge_node_id = request.get("knowledgeId")
    session_id = request.get("sessionId")
    ai_config = request.get("aiConfig")

    # Build context from DB history (last 10 messages)
    history = session.exec(
        select(ChatMessage).where(
            ChatMessage.user_id == user_id,
            ChatMessage.agent_type == agent_type,
        ).order_by(ChatMessage.created_at.desc()).limit(10)
    ).all()
    history.reverse()

    context = [{"role": m.role, "content": m.content} for m in history]

    # Add knowledge context if available
    system_extra = ""
    if knowledge_node_id:
        node = session.get(KnowledgeNode, knowledge_node_id)
        if node:
            system_extra += f"\n用户正在学习: {node.name} — {node.description}"

    rag_prompt = rag_engine.get_rag_context_prompt(msg, top_k=3)
    if rag_prompt:
        system_extra += f"\n{rag_prompt}"

    system = AGENT_SYSTEM_PROMPTS.get(agent_type, AGENT_SYSTEM_PROMPTS["tutor"]) + system_extra
    full_context = [{"role": "system", "content": system}] + context

    reply = llm_chat(msg, context=full_context, ai_config=ai_config)

    # Persist messages
    session.add(ChatMessage(user_id=user_id, session_id=session_id, agent_type=agent_type, role="user", content=msg, knowledge_node_id=knowledge_node_id))
    session.add(ChatMessage(user_id=user_id, session_id=session_id, agent_type=agent_type, role="assistant", content=reply, knowledge_node_id=knowledge_node_id))
    session.commit()

    return {"message": reply, "agentType": agent_type}


@app.post("/api/agent/chat-stream")
async def chat_stream_with_agent(request: Dict[str, Any], session: Session = Depends(get_session)):
    msg = request.get("message", "")
    agent_type = request.get("agentType", "tutor")
    user_id = request.get("userId", "user-1")
    knowledge_node_id = request.get("knowledgeId")
    session_id = request.get("sessionId")
    ai_config = request.get("aiConfig")

    history = session.exec(
        select(ChatMessage).where(
            ChatMessage.user_id == user_id,
            ChatMessage.agent_type == agent_type,
        ).order_by(ChatMessage.created_at.desc()).limit(10)
    ).all()
    history.reverse()

    context = [{"role": m.role, "content": m.content} for m in history]
    system_extra = ""
    if knowledge_node_id:
        node = session.get(KnowledgeNode, knowledge_node_id)
        if node:
            system_extra += f"\n用户正在学习: {node.name} — {node.description}"

    rag_prompt = rag_engine.get_rag_context_prompt(msg, top_k=3)
    if rag_prompt:
        system_extra += f"\n{rag_prompt}"

    system = AGENT_SYSTEM_PROMPTS.get(agent_type, AGENT_SYSTEM_PROMPTS["tutor"]) + system_extra
    full_context = [{"role": "system", "content": system}] + context

    # Persist user message
    session.add(ChatMessage(user_id=user_id, session_id=session_id, agent_type=agent_type, role="user", content=msg, knowledge_node_id=knowledge_node_id))
    session.commit()

    return StreamingResponse(
        chat_stream_generator(msg, context=full_context, ai_config=ai_config),
        media_type="text/event-stream"
    )



@app.post("/api/agent/plan")
def generate_learning_plan(goal: str):
    return {"goal": goal, "nodes": ["python-basics", "variables"], "estimatedTime": "20小时"}

@app.post("/api/agent/practice")
def generate_practice_legacy(knowledgeId: str, difficulty: str = "medium"):
    return {"knowledgeId": knowledgeId, "difficulty": difficulty}


# ──────────────────────────────────────────────
# 11. Analytics
# ──────────────────────────────────────────────
@app.get("/api/analytics/overview")
def get_analytics_overview(request: Request, user_id: Optional[str] = None, session: Session = Depends(get_session)):
    if not user_id:
        user_id = get_current_user_id(request) or "user-1"
    total = session.exec(select(KnowledgeNode)).all()
    masteries = session.exec(
        select(UserMastery).where(UserMastery.user_id == user_id)
    ).all()
    mastered = sum(1 for m in masteries if m.mastery_score >= 80)
    avg = sum(m.mastery_score for m in masteries) / len(masteries) if masteries else 0
    return {"totalNodes": len(total), "masteredNodes": mastered, "averageMastery": round(avg, 1)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
