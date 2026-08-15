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

## 代码沙箱增强

```text
用户代码
  ↓
AST 安全审计 → 拦截危险 import/eval/exec
  ↓
代码包装 → 注入变量序列化钩子 (locals() → JSON)
  ↓
Docker CGroups / Subprocess 执行
  ↓
解析 stderr 中的 __PYPAD_VARIABLES__ 标记
  ↓
返回: stdout + stderr + variables + errorDetail
```

## Pythonic 风格分析

基于 AST 的静态分析引擎，检测 8 类风格问题：
- use-list-comprehension: for+append → 列表推导式
- use-isinstance: type(x)==T → isinstance(x, T)
- no-bare-except: 裸 except → 指定异常类型
- simplify-bool-compare: == True/False → 直接判断
- use-join: 循环中字符串 += → ''.join()
- use-with-open: open() → with open() as f
- use-truthiness: len(x)==0 → not x
