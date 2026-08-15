# PyPad Roadmap & Phase Gates (路线图与阶段闸门)

> [!CAUTION]
> **闸门铁律**：前一阶段的 Gate 未通过前，严格禁止进入下一阶段开发。拒绝任何"带病推进"或"先写后面的代码再补测试"的行为。

---

## 阶段概览 (Phases Overview)

```text
Phase 0: 项目基线与治理规范 (Baseline & Governance)      ➔ Gate 0 ✅
Phase 1: 需求与核心架构收敛 (Requirements & Architecture)  ➔ Gate 1 ✅
Phase 2: 后端基础设施与基础 API (Backend Infra & APIs)     ➔ Gate 2 ✅
Phase 3: 教材与文档智能导入 (Textbook Importer)            ➔ Gate 3 ✅ (Markdown only)
Phase 4: 动态知识图谱与向量检索 (Knowledge Graph & RAG)     ➔ Gate 4 ✅
Phase 5: 学习系统与代码沙箱 (Learning System & Sandbox)     ➔ Gate 5 ✅
Phase 6: AI Tutor 与智能诊断 (AI Tutor & Feedback)         ➔ Gate 6 ✅
Phase 7: 完整闭环与数据联动 (Complete Closed Loop E2E)      ➔ Gate 7 ✅
Phase 8: 测试与参赛交付 (Testing & Competition Delivery)    ➔ Gate 8 🔴
```

---

## Phase 0 — 项目基线与治理规范

- **目标**：建立项目最高真相源、演进路线图、验收标准、控制宪法与自动化测试基线。
- **交付物**：`PROJECT.md`, `ROADMAP.md`, `ACCEPTANCE.md`, `ARCHITECTURE.md`, `PROGRESS.md`, `pypad_constitution.md`

### Gate 0 准入/准出条件
- [x] 全套治理规范文档建立完成。
- [x] 开发宪法写入 `.agents/rules/` 与根目录。
- [x] 后端 API 单元测试框架可用 (`python tests/test_api.py`)。

---

## Phase 1 — 需求与核心架构收敛

- **目标**：明确前端 View 架构与后端数据模型（User, Course, KnowledgeNode, KnowledgeEdge, LearningSession, CodeSession, Practice, Mastery）。
- **交付物**：数据库 Schema (`schema.sql`, `models.py`), Vue 3 核心路由与组件框架。

### Gate 1 准入/准出条件
- [x] 数据库表结构定义完整，支持 SQLite 与 MySQL 兼容切换。
- [x] 前端路由图层（Dashboard, Graph View, Workspace, Admin, AI Tutor Sidepanel）全量就位。
- [x] 后端数据模型模型关系校验无错。

---

## Phase 2 — 后端基础设施与核心 API

- **目标**：实现用户认证、知识节点 CRUD、课程章节接口、代码试运行接口与面板统计。
- **交付物**：`auth.py`, `main.py`, `routers/graph.py`, 基础测试集。

### Gate 2 准入/准出条件
- [x] Auth JWT 注册/登录/Me 验证通过。
- [x] 知识节点与图谱 Endpoint 可正常返回 JSON 数据。
- [x] Workspace `/api/workspace/run` 基础代码执行可用。
- [x] `test_api.py` 24 个测试点全量 PASS。

---

## Phase 3 — 教材智能导入 (Markdown Textbook Importer)

- **目标**：实现 Markdown 文件上传、章节识别、知识点自动切分与依赖关系提取。
- **交付物**：`textbook_parser.py`, 章节提取器, 知识点解析器, RAG 热索引更新。
- **说明**：PDF / DOCX 解析不在需求范围内，仅支持 Markdown 格式教材。

### Gate 3 准入/准出条件
- [x] Markdown 规范结构解析生成。
- [x] Heading 层级（H1/H2/H3）正确识别为知识节点。
- [x] 代码块智能切割并关联到对应知识点。
- [x] KnowledgeNode 与依赖 Relation 正确提取并写入 DB。
- [x] 上传后自动触发 RAG 索引更新。
- [x] `test_textbook_parser.py` 2 项测试 PASS。

---

## Phase 4 — 动态知识图谱与向量检索 (Knowledge Graph & RAG)

- **目标**：基于知识点关联构建可交互关系图谱，提供高相关性 RAG 检索上下文。
- **交付物**：Cytoscape.js 知识图谱高亮与交互, RAG 检索 API, RAG 构造器。

### Gate 4 准入/准出条件
- [x] 知识图谱支持动态增删节点与边更新（`POST /api/textbook/upload`）。
- [x] 支持按分类、关键字、依赖路径高亮过滤（`GET /api/knowledge/search`）。
- [x] RAG 检索接口返回知识点关联上下文（`GET /api/knowledge/rag-context`）。
- [x] TF-IDF 余弦相似度 RAG 引擎可用（`rag_service.py`）。
- [x] `test_rag.py` 3 项测试 PASS。
- [x] Qdrant 向量数据库集成（本地持久化 + fastembed 嵌入，`qdrant_rag_service.py`）。

---

## Phase 5 — 学习系统与在线代码沙箱 (Learning System & Sandbox)

- **目标**：提供沉浸式学习流程、隔离安全的 Python 代码执行沙箱。
- **交付物**：Subprocess / Docker 隔离沙箱, Session 追踪系统, 练习评分系统。

### Gate 5 准入/准出条件
- [x] AST 静态代码安全扫描（禁止危险 Import/Call）。
- [x] 5 秒超时强杀与 50KB 内存输出截断。
- [x] 支持 Standard Output, Standard Error 正确捕获。
- [x] 学习 Session 能够精确追踪用户在每个知识点的停留、代码提交与练习事件。
- [x] 练习提交后自动计算得分并更新 UserMastery。
- [x] `test_sandbox.py` 6 项测试 PASS。

---

## Phase 6 — AI Tutor 与智能诊断 (AI Tutor & Feedback)

- **目标**：基于学习状态与代码报错提供实时 AI 流式对话与诊断反馈。
- **交付物**：`llm_service.py` SSE 流式输出, RAG 上下文增强, 对话持久化。

### Gate 6 准入/准出条件
- [x] AI Tutor 支持 Server-Sent Events (SSE) 实时打字机输出（`/api/agent/chat-stream`）。
- [x] 结合当前知识点与 RAG 检索上下文生成定向辅导。
- [x] 辅导对话自动关联持久化到数据库（`ChatMessage` 表）。
- [x] 支持多种 LLM 后端（DeepSeek / OpenAI / Ollama / Mock）。
- [ ] LLM 失败重试与降级机制（当前仅 try-except fallback）。

---

## Phase 7 — 完整闭环与数据联动 (Complete Closed Loop E2E)

- **目标**：连接「教材 ➔ 知识 ➔ 学习 ➔ 编程 ➔ 练习 ➔ 诊断 ➔ 掌握度更新 ➔ 下一步推送」完整链路。
- **交付物**：掌握度衰减与更新算法, 个性化推荐 Engine, E2E 全自动化测试。

### Gate 7 准入/准出条件
- [x] 练习提交后能够自动计算得分并更新能力掌握度（`submit_practice` API）。
- [x] 艾宾浩斯遗忘曲线衰减算法实现（$R(t) = \text{score} \cdot e^{-\Delta t / 7}$）。
- [x] DAG 拓扑排序动态学习路径推荐引擎（`/api/user/recommend-path`）。
- [x] 完成从注册用户到学习完整课程的端到端 E2E 自动化测试（`test_e2e.py` 48 passed）。
- [ ] Dashboard 掌握度雷达图与推荐学习路径实时同步更新。

---

## Phase 8 — 测试与参赛交付 (Testing & Competition Delivery)

- **目标**：全系统测试覆盖、参赛材料打包与最终交付。
- **交付物**：E2E 测试套件, 演示 Demo 数据, 比赛答辩材料 (`docs/competition/`)。

### Gate 8 准入/准出条件
- [x] 后端单元测试 37 项 100% 通过。
- [x] 前后端 E2E 集成测试 48 项 100% 通过。
- [ ] 前端组件测试覆盖。
- [ ] 参赛演示视频与文档就位。
