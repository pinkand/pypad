# Agent Guidance & Pre-flight Protocol for PyPad

> **Mandatory Agent Instructions**: Every AI assistant starting a turn on PyPad MUST execute the Pre-flight protocol before making any code modifications.

---

## Pre-flight Protocol (启动必定步骤)

在执行任何代码修改任务前，Agent 必须依次读取并校验：

1. **读取最高事实**：`PROJECT.md`（确认核心 10 步闭环）
2. **读取路线图与闸门**：`ROADMAP.md`（确认当前处于哪个 Phase 及 Gate 准入条件）
3. **读取进度总账**：`PROGRESS.md`（确认当前已完成、未完成与已知问题）
4. **读取验收标准**：`ACCEPTANCE.md`（确认 DoD 与证据链要求）
5. **检查宪法约束**：`.agents/rules/pypad_constitution.md`
6. **检查当前 Git 提交状态与最新测试运行**：`python tests/test_api.py`

---

## 必须遵循的协同机制

```text
               PyPad Project
                     │
                PROJECT.md
                     │
                ROADMAP.md
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
      Feature               Architecture
         │
     Acceptance (ACCEPTANCE.md)
         │
       Agent (Read Constitution)
         │
      Coding (No Mock, No Cheating)
         │
       Tests (python tests/test_api.py)
         │
        E2E
         │
       Review
         │
    Progress Ledger (PROGRESS.md)
         │
       Gate (Gate Review)
         │
    Next Phase
```

---

## 开发完成后必须输出的报告模板 (JSON Schema Rule)

报告必须严格遵循以下 JSON Schema 结构（缺少 required 字段即判定失败）：

```json
{
  "current_phase": "Phase X",
  "current_feature": "Feature Name",
  "status": "DONE | IN_PROGRESS | BLOCKED | UNKNOWN",
  "completion_percentage": 45,
  "completed_items": [
    {
      "item": "Item Description",
      "evidence": "file:///path/to/code#L10-L20"
    }
  ],
  "uncompleted_items": [
    "Uncompleted Item Description"
  ],
  "verification": {
    "unit_tests": { "passed": 22, "failed": 0, "log_evidence": "Command log snippet" },
    "e2e_tests": { "passed": 0, "failed": 0, "status": "UNKNOWN | PASS | FAIL" },
    "git_commit": "abc123def"
  },
  "known_issues": [],
  "blockers": [],
  "next_step": "Next step or Gate review"
}
```

