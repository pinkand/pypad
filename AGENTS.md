# Agent Guidance — PyPad

## Pre-flight Protocol

执行任何代码修改前，依次读取：
1. `PROJECT.md` — 核心闭环
2. `ROADMAP.md` — 当前 Phase 与 Gate
3. `PROGRESS.md` — 完成状态
4. `ACCEPTANCE.md` — 验收标准
5. `.agents/rules/pypad_constitution.md` — 宪法
6. `python tests/test_api.py` — 测试基线

## 完成报告格式

```json
{
  "current_phase": "Phase X",
  "current_feature": "Feature Name",
  "status": "DONE | IN_PROGRESS | BLOCKED",
  "completion_percentage": 45,
  "completed_items": [{ "item": "...", "evidence": "file:///path#L10" }],
  "uncompleted_items": ["..."],
  "verification": {
    "unit_tests": { "passed": 22, "failed": 0 },
    "e2e_tests": { "passed": 0, "failed": 0 },
    "git_commit": "abc123"
  },
  "known_issues": [],
  "blockers": [],
  "next_step": "..."
}
```
