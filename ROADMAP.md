# PyPad Roadmap & Phase Gates (路线图与阶段闸门)

> [!CAUTION]
> **闸门铁律**：前一阶段的 Gate 未通过前，严格禁止进入下一阶段开发。拒绝任何“带病推进”或“先写后面的代码再补测试”的行为。

---

## 阶段概览 (Phases Overview)

```text
Phase 0: 项目基线与治理规范 (Baseline & Governance)  ➔ Gate 0
Phase 1: 需求与核心架构收敛 (Requirements & Architecture) ➔ Gate 1
Phase 2: 后端基础设施与基础 API (Backend Infra & APIs) ➔ Gate 2
Phase 3: 教材与文档智能导入 (Textbook Importer) ➔ Gate 3
Phase 4: 动态知识图谱与向量检索 (Knowledge Graph & RAG) ➔ Gate 4
Phase 5: 学习系统与代码沙箱 (Learning System & Sandbox) ➔ Gate 5
Phase 6: AI Tutor 与智能诊断 (AI Tutor & Feedback) ➔ Gate 6
Phase 7: 完整闭环与数据联动 (Complete Closed Loop E2E) ➔ Gate 7
Phase 8: 测试与参赛交付 (Testing & Competition Delivery) ➔ Gate 8
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
- [x] `test_api.py` 22 个测试点全量 PASS。

---

## Phase 3 — 教材与文档智能导入 (Importer)

- **目标**：实现 PDF/DOCX/Markdown 文件上传、文本结构提取、章节识别与知识点自动切分。
- **交付物**：`importer_service.py`, 章节提取器, 知识点解析器, 向量化同步服务。

### Gate 3 准入/准出条件
- [ ] PDF 文件可正常解析导入。
- [ ] DOCX 文件可正常解析导入。
- [ ] Markdown 规范结构解析生成。
- [ ] Chapter 与 Section 层级正确识别。
- [ ] KnowledgePoint 与 依赖 Relation 正确提取。
- [ ] 结构化数据成功写入 DB，向量数据写入 Qdrant。
- [ ] 至少使用 1 份真实 Python 电子教材完成全流程 E2E 导入验证。

---

## Phase 4 — 动态知识图谱与向量检索 (Knowledge Graph & RAG)

- **目标**：基于知识点关联构建可交互关系图谱，基于 Qdrant 提供高相关性 RAG 检索上下文。
- **交付物**：Cytoscape.js 知识图谱高亮与交互, Qdrant 检索 API, RAG 构造器。

### Gate 4 准入/准出条件
- [ ] 知识图谱支持动态增删节点与边更新。
- [ ] 支持按分类、关键字、依赖路径高亮过滤。
- [ ] RAG 检索接口可在 <300ms 内返回知识点关联上下文。
- [ ] 图谱与 RAG 检索的集成测试通过。

---

## Phase 5 — 学习系统与在线代码沙箱 (Learning System & Sandbox)

- **目标**：提供沉浸式学习流程、单步调试/运行 Monaco IDE、隔离安全的 Python 代码执行沙箱。
- **交付物**：Docker / Subprocess 隔离沙箱, Session 追踪系统, Monaco 代码分析。

### Gate 5 准入/准出条件
- [ ] 代码执行隔离防越权（禁止恶意系统调用与无限循环超时）。
- [ ] 支持 Standard Output, Standard Error, Standard Input 正确捕获。
- [ ] 学习 Session 能够精确追踪用户在每个知识点的停留、代码提交与练习事件。
- [ ] 沙箱性能与并发压力测试通过。

---

## Phase 6 — AI Tutor 与智能诊断

- **目标**：基于学习状态与代码报错提供实时 AI 流式对话与诊断反馈。
- **交付物**：`llm_service.py` SSE 流式输出, 报错智能诊断器, 答疑持久化。

### Gate 6 准入/准出条件
- [ ] AI Tutor 支持 Server-Sent Events (SSE) 实时打字机输出。
- [ ] 结合当前知识点与代码报错上下文生成定向辅导。
- [ ] 辅导对话与学习行为自动关联持久化到数据库。
- [ ] 支持 LLM 失败重试与降级机制。

---

## Phase 7 — 完整闭环与数据联动 (Complete Closed Loop E2E)

- **目标**：连接「教材 ➔ 知识 ➔ 学习 ➔ 编程 ➔ 练习 ➔ 诊断 ➔ 掌握度更新 ➔ 下一步推送」完整链路。
- **交付物**：掌握度衰减与更新算法, 个性化推荐 Engine, E2E 全自动化测试。

### Gate 7 准入/准出条件
- [ ] 练习提交后能够自动计算得分并更新能力掌握度。
- [ ] Dashboard 掌握度雷达图与推荐学习路径实时同步更新。
- [ ] 完成从注册用户到学习完整课程的端到端 E2E 自动化测试。

---

## Phase 8 — 测试与参赛交付 (Testing & Competition Delivery)

- **目标**：全系统性能调优、部署自动化、参赛材料打包与最终交付。
- **交付物**：Docker Compose 一键部署, 演示 Demo 数据, 比赛答辩材料 (`docs/competition/`)。

### Gate 8 准入/准出条件
- [ ] 全部单元测试、接口测试与 E2E 测试 100% 通过。
- [ ] Docker Compose 无缝构建运行。
- [ ] 参赛演示视频与文档就位。
