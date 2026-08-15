# PyPad Development Constitution (项目开发宪法)

> **最高指示**：所有参与 PyPad 开发的 AI Agent（包括 Codex, Claude, Cursor, Gemini Agent）与人类开发者，均必须无条件遵守本宪法。

---

## 1. Mission (核心使命)

PyPad 是一个 AI 驱动的 Python Learning OS。

所有开发工作必须严格服务于以下核心闭环：

```text
教材 ➔ 结构化知识 ➔ 知识关系 ➔ 学习路径 ➔ 学习 ➔ 编程实践 ➔ 练习 ➔ AI反馈 ➔ 掌握度评估 ➔ 个性化下一步学习
```

不得偏离该核心闭环。

---

## 2. Source of Truth (唯一事实来源)

以下文件是项目的最高事实来源：

- `PROJECT.md`
- `ROADMAP.md`
- `ACCEPTANCE.md`
- `ARCHITECTURE.md`

如果代码、临时说明或 AI 推测与这些文件冲突：**优先遵循项目文档，并报告冲突。不得自行修改项目目标。**

---

## 3. Scope Discipline (范围纪律)

执行任务时：
1. 只解决当前任务。
2. 不擅自增加无关功能。
3. 不因为实现困难而降低需求。
4. 不删除需求中的核心能力。
5. **不使用 Mock、Placeholder、TODO 冒充完成。**
6. 不通过硬编码制造“看起来能运行”的结果。
7. 不为了测试通过而修改测试标准。
8. 发现架构问题可以报告，但不得擅自扩大任务范围。

---

## 4. Definition of Done (完成定义)

任何任务只有同时满足：
- Implementation complete
- Integration complete
- Tests complete
- Error handling complete
- Documentation updated
- Acceptance criteria satisfied
- E2E verification passed

才能标记为 `DONE`。否则必须标记为 `IN_PROGRESS` 或 `BLOCKED`。

---

## 5. No Fake Completion (禁止假完成)

严格禁止以下行为：
- 写一个假 API。
- 返回固定 JSON 冒充真实数据。
- 使用 Mock 冒充生产逻辑。
- 用 TODO 代替实现。
- 用注释描述未来功能但标记完成。
- 只实现前端而没有后端。
- 只实现 API 而没有业务闭环。
- 只让正常路径工作而忽略异常情况。

---

## 6. Change Control (变更控制)

如果发现当前需求与架构存在冲突：
**停止扩大实现。**

先报告：
1. 冲突是什么
2. 为什么冲突
3. 影响哪些模块
4. 推荐解决方案
5. 哪个方案最符合 PyPad 长期目标

未经确认不得改变核心架构或产品目标。

---

## 7. Verification (验证原则)

每完成一个功能：
1. 静态检查
2. 单元测试
3. API 测试
4. 集成测试
5. E2E 测试
6. 人工验证

**必须在 `PROGRESS.md` 中记录测试结果与证据。**

---

## 8. Progress Reporting (结构化事实报告)

每次任务结束或进行进度汇报时，必须基于确凿的系统事实输出报告。报告格式必须包含以下结构化 JSON（或严格对应 JSON 字段的表述）：

```json
{
  "current_phase": "Phase X",
  "current_feature": "Feature Name",
  "status": "DONE | IN_PROGRESS | BLOCKED | UNKNOWN",
  "completion_percentage": 45,
  "completed_items": [
    {
      "item": "Description",
      "evidence": "file:///path/to/code#L10-L20"
    }
  ],
  "uncompleted_items": [
    "Description"
  ],
  "verification": {
    "unit_tests": { "passed": 22, "failed": 0, "log_evidence": "Command output snippet" },
    "e2e_tests": { "passed": 0, "failed": 0, "status": "UNKNOWN | PASS | FAIL" },
    "git_commit": "abc123def"
  },
  "known_issues": [],
  "blockers": [],
  "next_step": "Description"
}
```

不得使用“基本完成”、“差不多完成”等任何主观模糊表述。

---

## 9. Failure Handling (阻塞与未知状态处理)

如果无确凿证据证明完成：**严禁猜测，严禁伪造完成。**
- 若由于依赖或错误导致阻塞，明确标记为：`BLOCKED`
- 若缺少测试证据或系统事实不足，明确标记为：`UNKNOWN`

---

## 10. Priority (优先级排序)

优先级定义：
- **P0**: 核心学习闭环（教材 ➔ 知识 ➔ 路径 ➔ 编程 ➔ AI ➔ 掌握度）
- **P1**: 核心业务功能（Auth, Course, Workspace, Practices）
- **P2**: 数据与基础设施（Qdrant, Sandbox, DB Models）
- **P3**: 测试与稳定性（E2E Tests, CI Pipeline）
- **P4**: UI/UX 细节优化
- **P5**: 非核心扩展

**不得为了 P4/P5 工作而延迟 P0/P1。**

---

## 11. Fact Interpreter Principle (事实解释器原则)

AI 不是项目进度的决定者，而是项目事实的解释者。

1. 项目完成度、模块状态、测试状态、Git 状态、E2E 状态必须由系统提供的结构化事实决定。
2. AI **不得创造、修改、补全、猜测**任何事实。
3. 所有结论必须能够引用对应 `evidence`（包含精确文件路径、代码行号、测试日志或 Commit Hash）。
4. 如果没有足够证据，状态**必须输出 UNKNOWN**，不得推测。
5. 所有报告必须严格遵循结构化格式，缺少 required field 均视为生成失败。
6. `DONE` 状态必须无条件满足预定义的 Definition of Done。
7. 在相同的 Project Facts 下，任何模型均必须得出完全一致的状态和完成度数值。模型之间只允许在解释、风险分析和改进建议上存在差异。

