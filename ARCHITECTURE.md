# PyPad 系统架构

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Vite + Tailwind CSS |
| 编辑器 | Monaco Editor |
| 图谱 | Cytoscape.js + VueFlow |
| 3D | Three.js |
| 后端 | Python FastAPI |
| ORM | SQLModel + SQLite |
| 向量库 | Qdrant (fastembed) |
| 沙箱 | Subprocess / Docker |
| AI | DeepSeek / OpenAI / Ollama |

## 架构分层

```text
Browser (Vue 3 SPA)
  │ REST / SSE
  ▼
API Gateway (FastAPI)
  ├── Auth / Knowledge / Courses / Workspace
  ├── Sessions / Practices / Agent / Dashboard
  ▼
Data Layer ─── AI & RAG Engine ─── Code Sandbox
(SQLite)       (Qdrant + LLM)      (Subprocess/Docker)
```

## 核心数据模型

User, Course, Chapter, Section, KnowledgeNode, KnowledgeEdge,
LearningSession, SessionEventLog, WorkspaceRun, CodeReview,
Practice, UserMastery, UserProgress, StudyRecord, ChatMessage
