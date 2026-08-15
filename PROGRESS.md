# PyPad Progress Ledger (进度总账)

> **Overall Project Completion: ~80%**  
> Phase 0-7 核心功能已全部实现并验证，E2E 测试通过。剩余工作：前端测试、参赛材料。

---

## 1. 阶段状态总览 (Phase Status Overview)

| Phase | 名称 | 状态 | 测试证据 |
| :--- | :--- | :--- | :--- |
| **Phase 0** | 项目基线与治理规范 | **DONE** ✅ | `PROJECT.md`, `ROADMAP.md`, `ACCEPTANCE.md`, `pypad_constitution.md` |
| **Phase 1** | 需求与核心架构收敛 | **DONE** ✅ | `schema.sql`, `models.py`, Vue 3 SPA Views |
| **Phase 2** | 后端基础设施与核心 API | **DONE** ✅ | `test_api.py` 24 passed |
| **Phase 3** | 教材与文档智能导入 | **DONE** ✅ (Markdown only) | `test_textbook_parser.py` 2 passed |
| **Phase 4** | 动态知识图谱与向量检索 | **DONE** ✅ | `test_rag.py` 3 passed + Qdrant 本地持久化 |
| **Phase 5** | 学习系统与在线代码沙箱 | **DONE** ✅ | `test_sandbox.py` 6 passed |
| **Phase 6** | AI Tutor 与智能诊断 | **DONE** ✅ | SSE 流式对话 + RAG 上下文已实现 |
| **Phase 7** | 完整闭环与数据联动 | **DONE** ✅ | `test_e2e.py` 48 passed，完整学习闭环验证 |
| **Phase 8** | 测试与参赛交付 | **IN_PROGRESS** ⏳ | 后端 85 项测试全通过，参赛材料待准备 |

---

## 2. 模块细化进度 (Detailed Feature Matrix)

### 1. 全屏拓扑与筛选控制台 (Knowledge Map & Universe)
- [x] 全屏 100vw × 100vh VueFlow / Three.js 拓扑渲染
- [x] 顶部居中胶囊形玻璃态筛选控制台
- [x] 3D 太空自转与 16s 弥散光晕双重背景动画
- **Status**: DONE ✅

### 2. 教材精讲与 Monaco 编辑器 (Knowledge Panel & Workspace)
- [x] 教材要点、避雷、示例代码展开抽屉
- [x] 一键注入 Monaco 编辑器并自动唤起工作区
- [x] Monaco 编辑器 Traceback 错误行整行红光高亮
- [x] AI 导师中文智能故障诊断提示
- **Status**: DONE ✅

### 3. 代码沙箱与安全防护 (Sandbox Execution)
- [x] AST 静态代码安全扫描（禁止危险 Import/Call）
- [x] 5 秒超时强杀与 50KB 内存输出截断
- [x] Docker 容器级 CGroups 内存 (`--memory=128m`) 与 CPU (`--cpus=0.5`) 硬隔离器 (`docker_runner.py`)
- **Status**: DONE ✅

### 4. AI Tutor 导师与 RAG (AI Tutor & Vector RAG)
- [x] 右下角 FloatingBall 与 AgentPanel 对话抽屉解耦
- [x] LLM SSE 渐进打字机推流 (`/api/agent/chat-stream`)
- [x] 全局统一 AI 配置中心（DeepSeek / OpenAI / Ollama / Mock）
- [x] TF-IDF 余弦相似度 Vector RAG 检索引擎 (`rag_service.py`)
- [x] Qdrant 向量数据库集成，本地持久化存储 + fastembed 嵌入 (`qdrant_rag_service.py`)
- [x] Composite 引擎自动切换：Qdrant 优先，TF-IDF 降级兜底
- **Status**: DONE ✅

### 5. 学习闭环与拓扑推荐 (Session & Topological Recommendation)
- [x] 艾宾浩斯遗忘曲线衰减算法 ($R(t) = \text{score} \cdot e^{-\Delta t / 7}$)
- [x] 练习打分与用户等级实时刷新
- [x] DAG 拓扑排序动态学习路径推荐引擎 (`topological_path.py` + `GET /api/user/recommend-path`)
- **Status**: DONE ✅

### 6. 教材解析导入引擎 (Textbook Parser Engine)
- [x] Markdown 教材目录树提取与代码块智能切割 (`textbook_parser.py`)
- [x] 自动生成 KnowledgeNode / KnowledgeEdge 存库与 RAG 实时热索引更新 (`POST /api/textbook/upload`)
- ~~PDF / DOCX 解析~~ (不在需求范围内)
- **Status**: DONE ✅

### 7. 前端测试覆盖 (Frontend Test Coverage)
- [ ] Vue 组件单元测试
- [ ] 前端 E2E 测试 (Playwright / Cypress)
- **Status**: TODO 🔴

### 8. 参赛交付材料 (Competition Delivery)
- [ ] 参赛演示视频
- [ ] 答辩文档 (`docs/competition/`)
- [ ] Demo 数据预置
- **Status**: TODO 🔴

---

## 3. 自动化测试证据链 (Test Ledger)

| 测试套件 | 文件 | 通过 | 失败 |
| :--- | :--- | :--- | :--- |
| API 测试 | `tests/test_api.py` | 24 | 0 |
| 代码沙箱测试 | `tests/test_sandbox.py` | 6 | 0 |
| Vector RAG 测试 | `tests/test_rag.py` | 3 | 0 |
| 拓扑推荐引擎测试 | `tests/test_topological.py` | 2 | 0 |
| 教材解析引擎测试 | `tests/test_textbook_parser.py` | 2 | 0 |
| **E2E 集成测试** | `tests/test_e2e.py` | **48** | **0** |
| **总计** | | **85** | **0** |

> 最后验证时间: 2024 年项目当前提交  
> 命令: `source venv/bin/activate && python tests/test_*.py`

---

## 4. 关键未完成项 (Critical Remaining Work)

| 优先级 | 任务 | 影响范围 |
| :--- | :--- | :--- |
| **P2** | 前端组件测试 | 前端质量保障 |
| **P3** | 参赛材料准备 | 比赛交付 |

---

## 5. 已知问题 (Known Issues)

1. AI Agent 的 `/api/agent/plan` 和 `/api/agent/practice` 端点为占位实现，未接入 LLM。
2. 无前端自动化测试覆盖。
3. Qdrant 客户端在解释器退出时有 sqlite3 线程清理警告（不影响功能）。
