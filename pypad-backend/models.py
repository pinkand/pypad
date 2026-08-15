from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, JSON


# ── Response models (non-table) ──────────────────────

class TreeNodeResponse(BaseModel):
    id: str
    name: str
    description: str = ""
    category: str = ""
    importance: int = 5
    parent_id: Optional[str] = None
    depth: int = 0
    sort_order: int = 0
    children: List["TreeNodeResponse"] = []

class EdgeResponse(BaseModel):
    source_id: str
    target_id: str
    relation_type: str = "prerequisite"
    weight: float = 0.5

class GraphResponse(BaseModel):
    tree: List[TreeNodeResponse]
    edges: List[EdgeResponse]

class Course(SQLModel, table=True):
    __tablename__ = "courses"
    id: str = Field(primary_key=True, max_length=64)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    cover_url: Optional[str] = Field(default=None, max_length=512)
    level: str = Field(default="beginner", max_length=32)
    category: str = Field(max_length=64, index=True)
    sort_order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Chapter(SQLModel, table=True):
    __tablename__ = "chapters"
    id: str = Field(primary_key=True, max_length=64)
    course_id: str = Field(foreign_key="courses.id", max_length=64, index=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    sort_order: int = Field(default=0)

class Section(SQLModel, table=True):
    __tablename__ = "sections"
    id: str = Field(primary_key=True, max_length=64)
    chapter_id: str = Field(foreign_key="chapters.id", max_length=64, index=True)
    title: str = Field(max_length=255)
    content_type: str = Field(default="text", max_length=32)
    estimated_minutes: int = Field(default=15)
    sort_order: int = Field(default=0)

class KnowledgeNode(SQLModel, table=True):
    __tablename__ = "knowledge_nodes"
    id: str = Field(primary_key=True, max_length=64)
    code: Optional[str] = Field(default=None, max_length=64, index=True)
    name: str = Field(max_length=128)
    description: str = Field(default="", max_length=512)
    category: str = Field(default="", max_length=64, index=True)
    importance: int = Field(default=5, ge=1, le=10)
    
    course_id: Optional[str] = Field(default=None, foreign_key="courses.id", max_length=64)
    chapter_id: Optional[str] = Field(default=None, foreign_key="chapters.id", max_length=64)
    section_id: Optional[str] = Field(default=None, foreign_key="sections.id", max_length=64)
    
    parent_id: Optional[str] = Field(default=None, max_length=64, index=True)
    depth: int = Field(default=0, ge=0)
    sort_order: int = Field(default=0)
    
    pos_x: float = Field(default=0.0)
    pos_y: float = Field(default=0.0)
    pos_z: float = Field(default=0.0)
    
    ai_summary: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class KnowledgeEdge(SQLModel, table=True):
    __tablename__ = "knowledge_edges"
    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: str = Field(foreign_key="knowledge_nodes.id", max_length=64, index=True)
    target_id: str = Field(foreign_key="knowledge_nodes.id", max_length=64, index=True)
    relation_type: str = Field(default="prerequisite", max_length=32)
    strength: str = Field(default="soft", max_length=16)
    weight: float = Field(default=0.5, ge=0.0, le=1.0)

class Project(SQLModel, table=True):
    __tablename__ = "projects"
    id: str = Field(primary_key=True, max_length=64)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    difficulty: str = Field(default="easy", max_length=32)
    estimated_hours: int = Field(default=2)
    init_code: Optional[str] = Field(default=None)
    readme_markdown: Optional[str] = Field(default=None)
    test_cases: Optional[List[Dict[str, Any]]] = Field(default=None, sa_type=JSON)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Practice(SQLModel, table=True):
    __tablename__ = "practices"
    id: str = Field(primary_key=True, max_length=64)
    title: str = Field(max_length=255)
    type: str = Field(default="fixed", max_length=32)
    difficulty: str = Field(default="easy", max_length=32)
    knowledge_node_id: str = Field(foreign_key="knowledge_nodes.id", max_length=64, index=True)
    project_id: Optional[str] = Field(default=None, foreign_key="projects.id", max_length=64)
    prompt: str = Field(default="")
    starter_code: Optional[str] = Field(default=None)
    solution_code: Optional[str] = Field(default=None)
    test_cases: Optional[List[Dict[str, Any]]] = Field(default=None, sa_type=JSON)
    ai_gen_params: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class LearningSession(SQLModel, table=True):
    __tablename__ = "learning_sessions"
    id: str = Field(primary_key=True, max_length=64)
    user_id: str = Field(max_length=64, index=True)
    course_id: Optional[str] = Field(default=None, max_length=64)
    chapter_id: Optional[str] = Field(default=None, max_length=64)
    section_id: Optional[str] = Field(default=None, max_length=64)
    knowledge_node_id: str = Field(foreign_key="knowledge_nodes.id", max_length=64, index=True)
    status: str = Field(default="active", max_length=32)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = Field(default=None)
    total_duration_seconds: int = Field(default=0)

class SessionEventLog(SQLModel, table=True):
    __tablename__ = "session_event_logs"
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(foreign_key="learning_sessions.id", max_length=64, index=True)
    event_type: str = Field(max_length=64)
    payload: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class WorkspaceRun(SQLModel, table=True):
    __tablename__ = "workspace_runs"
    id: str = Field(primary_key=True, max_length=64)
    session_id: str = Field(foreign_key="learning_sessions.id", max_length=64, index=True)
    practice_id: Optional[str] = Field(default=None, max_length=64)
    code: str = Field(default="")
    language: str = Field(default="python", max_length=32)
    status: str = Field(max_length=32)
    stdout: Optional[str] = Field(default=None)
    stderr: Optional[str] = Field(default=None)
    exit_code: int = Field(default=0)
    runtime_ms: int = Field(default=0)
    memory_bytes: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CodeReview(SQLModel, table=True):
    __tablename__ = "code_reviews"
    id: str = Field(primary_key=True, max_length=64)
    workspace_run_id: str = Field(foreign_key="workspace_runs.id", max_length=64, unique=True)
    session_id: str = Field(foreign_key="learning_sessions.id", max_length=64, index=True)
    overall_score: int = Field(default=85)
    code_quality_score: int = Field(default=80)
    logic_score: int = Field(default=90)
    performance_score: int = Field(default=85)
    ai_feedback: Optional[str] = Field(default=None)
    suggestions: Optional[List[str]] = Field(default=None, sa_type=JSON)
    weakness_tags: Optional[List[str]] = Field(default=None, sa_type=JSON)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserMastery(SQLModel, table=True):
    __tablename__ = "user_mastery"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=64, index=True)
    knowledge_node_id: str = Field(foreign_key="knowledge_nodes.id", max_length=64, index=True)
    mastery_score: float = Field(default=0.0, ge=0.0, le=100.0)
    status: str = Field(default="unlearned", max_length=32)
    last_studied_at: Optional[datetime] = Field(default=None)

class UserProgress(SQLModel, table=True):
    __tablename__ = "user_progress"
    user_id: str = Field(primary_key=True, max_length=64)
    current_course_id: Optional[str] = Field(default=None, max_length=64)
    current_session_id: Optional[str] = Field(default=None, max_length=64)
    overall_mastery: float = Field(default=0.0)
    study_streak_days: int = Field(default=1)
    completed_projects_count: int = Field(default=0)
    completed_practices_count: int = Field(default=0)
    total_study_time_seconds: int = Field(default=0)
    weak_node_ids: Optional[List[str]] = Field(default=None, sa_type=JSON)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class StudyRecord(SQLModel, table=True):
    __tablename__ = "study_records"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=64, index=True)
    knowledge_node_id: str = Field(foreign_key="knowledge_nodes.id", max_length=64, index=True)
    duration_seconds: int = Field(default=0)
    behavior: str = Field(default="read", max_length=32)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: str = Field(primary_key=True, max_length=64)
    username: str = Field(max_length=64, unique=True, index=True)
    email: str = Field(max_length=128, unique=True, index=True)
    password_hash: str = Field(max_length=256)
    display_name: Optional[str] = Field(default=None, max_length=128)
    avatar_url: Optional[str] = Field(default=None, max_length=512)
    level: int = Field(default=1)
    experience: int = Field(default=0)
    streak: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=64, index=True)
    session_id: Optional[str] = Field(default=None, max_length=64)
    agent_type: str = Field(default="tutor", max_length=32)
    role: str = Field(max_length=16)  # "user" | "assistant"
    content: str = Field(default="")
    knowledge_node_id: Optional[str] = Field(default=None, max_length=64)
    created_at: datetime = Field(default_factory=datetime.utcnow)
