# PyPad Acceptance Standards & Definition of Done (验收标准与完成定义)

> [!WARNING]
> **红线原则**：严禁任何假完成行为！严禁使用静态 Mock 冒充真实业务逻辑、严禁返回硬编码 JSON 伪造结果、严禁为了让测试通过而篡改测试断言。

---

## 1. 单项 Feature 结构规范

每个 Feature 在设计与开发时必须包含以下完整结构：

```text
Feature
│
├── Goal (功能目标)
├── Scope (作用范围)
├── Requirements (功能要求)
├── Acceptance Criteria (验收标准)
├── Tests (自动化测试)
├── E2E (端到端验证)
└── Definition of Done (完成定义)
```

例如 **AI Tutor 模块**的验收结构：

```text
Feature: AI Tutor

功能目标：
用户能够针对当前 Python 知识点与报错代码与 AI 导师进行实时流式辅导互动。

必须实现清单：
[ ] 获取当前知识点与上下文 (Knowledge Context)
[ ] 获取用户当前学习状态与历史代码 (Learning State)
[ ] RAG 检索知识库关联内容 (RAG Retrieval)
[ ] 构造严密 Prompt 上下文 (Context Construction)
[ ] LLM Streaming 实时流式响应 (SSE / WebSocket)
[ ] AI 回答正确渲染 (Markdown & Code Highlighting)
[ ] 对话历史持久化 (Conversation Storage)
[ ] 关联保存学习行为与反馈 (Behavior Logging)
[ ] 智能代码报错归因与针对性纠错指导 (Error Diagnosis)
[ ] 前端 UI 实时交互与加载态展示 (Frontend Component)
[ ] API 自动化测试覆盖 (API Test)
[ ] E2E 端到端真实交互验证 (E2E Test)
```

---

## 2. 全局完成定义 (Definition of Done - DoD)

任何任务只有**同时**满足以下所有条件，才能在 `PROGRESS.md` 和 Commit 信息中标记为 `DONE`：

1. **Implementation Complete**：核心功能代码完整编写，架构层次清晰。
2. **Integration Complete**：前后端打通，数据库/Qdrant/沙箱等依赖正常交互。
3. **Tests Complete**：编写并运行单元测试与 API 测试，无报错无遗漏。
4. **Error Handling Complete**：对异常边界、网络超时、格式错误有健全的 Try-Catch 与 HTTP 错误码。
5. **Documentation Updated**：同步更新相关架构文档、API 注释与 `PROGRESS.md`。
6. **Acceptance Criteria Satisfied**：功能要求清单逐条满足。
7. **E2E Verification Passed**：在真实运行环境（非 Mock 模式）下完成端到端验证。

> 未能同时满足以上 7 条的任务，状态必须标记为 `IN_PROGRESS` 或 `BLOCKED`。

---

## 3. 反假完成红线 (No Fake Completion Rules)

禁止以下任何“造假”或“掩耳盗铃”行为：

1. **假 API**：写一个空 Routing 函数返回 `{"status": "ok"}` 冒充实现。
2. **硬编码 JSON**：在 API 中直接 `return {"data": [...]}` 冒充数据库或 LLM 结果。
3. **Mock 替代生产逻辑**：在正式代码中使用 `mock_response()` 冒充底层真实 API/服务。
4. **TODO 标记完成**：用 `# TODO: implement this` 占位却在进度中标记已完成。
5. **单边实现**：只写前端页面没有后端 API 支持，或只写 API 无法通过前端闭环操作。
6. **忽略异常**：用裸 `try: ... except: pass` 吞掉错误，冒充系统稳定。
7. **篡改测试**：为了让 `pytest` 显示绿色而删掉断言或将期望值改为实际报错值。

---

## 4. 证据链机制 (Evidence Chain)

每次宣布功能完成或提交 Gate 评审时，必须出示以下**证据链**：

```text
Status: DONE
Evidence:
- Code Files: [pypad-backend/routers/xxx.py](file:///Users/jabar/code/PyPad/pypad-backend/routers/xxx.py)
- Unit Tests: X passed (pytest output hash/logs)
- API Tests: Y passed
- E2E Test: Real execution log / screenshot
- Manual Verification: Confirmed visually & functionally
- Commit ID: abc123def
```

无法提供完整证据链的任务，一律视为未完成。

---

## 5. 事实确定性与 Schema 强制校验 (Fact Determinism & Schema Rules)

1. **AI 角色定位**：AI 仅为项目事实的解释者，非决定者。
2. **事实来源**：完成度、模块状态、测试结果均由源代码、运行日志、DB 记录与 Git Log 等结构化事实客观决定。
3. **零推测与 UNKNOWN 回退**：缺少证据链项时必须标记为 `UNKNOWN`，严禁猜测或脑补事实。
4. ** Schema 校验**：所有进度与验收报告必须满足结构化 JSON Schema 约束，缺少 required 字段即判定生成失败。
5. **模型一致性**：在相同的 Project Facts 下，任何模型得出的数值与状态判定必须完全一致。

