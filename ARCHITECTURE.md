# PyPad Architecture & System Design (系统架构设计)

> [!NOTE]
> 本文档定义 PyPad 的系统技术栈、整体架构分层、数据流图与模块依赖关系。

---

## 1. 技术栈 (Technology Stack)

| 层级 | 技术选型 | 说明 |
| :--- | :--- | :--- |
| **前端 (Frontend)** | Vue 3 + TypeScript + Vite | 极速响应响应式 SPA 架构 |
| **UI & 样式** | Tailwind CSS + Element Plus / Lucide | 现代化美观深色/亮色主题交互 |
| **编辑器 & 图谱** | Monaco Editor + Cytoscape.js | 独立 IDE 体验与高性能知识图谱渲染 |
| **后端 (Backend)** | Python 3.10+ FastAPI | 高性能异步 RESTful / SSE API 服务 |
| **ORM & 数据库** | SQLModel + SQLite / MySQL | 关系型存储（用户、课程、知识节点、答题轨迹） |
| **向量数据库** | Qdrant (or In-memory Vector Index) | 教材知识点与问答 RAG 语义检索 |
| **代码执行沙箱** | Subprocess / Docker Container | 隔离安全的 Python 代码执行与资源限制 |
| **AI 大模型服务** | OpenAI / Ollama / DeepSeek API | 兼容多模型接入与流式响应 |

---

## 2. 系统整体架构 (System Architecture Diagram)

```text
[ 用户端 Browser (Vue 3 SPA) ]
  ├── Dashboard View (面板)
  ├── Graph View (知识图谱 - Cytoscape.js)
  ├── Workspace View (代码编辑器 - Monaco Editor)
  └── AI Tutor Sidepanel (智能导师侧边栏)
         │
         │ REST API / SSE Streaming
         ▼
[ 后端 API Gateway (FastAPI) ]
  ├── Auth Router (/api/auth)
  ├── Knowledge Router (/api/knowledge)
  ├── Course Router (/api/courses)
  ├── Workspace Router (/api/workspace)
  ├── Sessions Router (/api/sessions)
  ├── Practices Router (/api/practices)
  ├── Agent Router (/api/agent)
  └── Dashboard Router (/api/dashboard)
         │
  ┌──────┴───────────────────────────┬───────────────────────────┐
  ▼                                  ▼                           ▼
[ Data Layer ]            [ AI & RAG Engine ]          [ Code Sandbox ]
  ├── MySQL / SQLite         ├── Qdrant Vector Store      ├── Subprocess Runner
  └── SQLModel ORM           ├── RAG Context Extractor    └── Docker Execution
                             └── LLM Streaming Service        (Resource limits)
```

---

## 3. 核心数据模型 (Data Models)

- **User**: 用户账户、角色、配置。
- **Course & Chapter**: 课程与章节结构。
- **KnowledgeNode**: 知识点（标题、分类、内容、难度、代码示例）。
- **KnowledgeEdge**: 知识点关系（源节点、目标节点、关系类型如 `prerequisite`, `related`）。
- **LearningSession**: 用户学习会话（开始时间、结束时间、事件日志）。
- **CodeSession / Workspace**: 提交运行的代码与运行结果（Status, Stdout, Stderr, ExecTime）。
- **Practice & Submission**: 练习题与用户提交得分。
- **UserMastery**: 用户在特定知识点上的掌握度评分与最近复习时间。

---

## 4. 数据闭环流动路径 (Closed Loop Data Flow)

1. **教材导入**: Importer Service 读取文件 ➔ 切分 Chapter/KnowledgeNode ➔ 写入 SQL ➔ 向量化存入 Qdrant。
2. **学习路径导航**: 提取 UserMastery + KnowledgeEdge ➔ 计算 Topo Sort & 欠缺知识点 ➔ 前端图谱推荐路径。
3. **沉浸编程实践**: Monaco Editor 编辑代码 ➔ POST `/api/workspace/run` ➔ 代码沙箱隔离执行 ➔ 返回 Stdout/Stderr。
4. **AI 智能辅导**: 用户点击 AI 诊断或发送消息 ➔ RAG 提取 Knowledge Context + Sandbox Output ➔ LLM 生成定向辅导 ➔ 持久化对话日志。
5. **掌握度更新**: Practice 判定提交结果 ➔ 结合运行成功率与重试次数 ➔ 算法更新 UserMastery ➔ 重置下一阶段学习目标。
