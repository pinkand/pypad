# PyPad 进度总账

> **Overall: ~90%** — 后端核心功能全部完成，前端页面已补全，新增代码质量分析与变量可视化。

## 阶段状态

| Phase | 名称 | 状态 |
|-------|------|------|
| 0 | 项目基线与治理规范 | ✅ DONE |
| 1 | 需求与核心架构收敛 | ✅ DONE |
| 2 | 后端基础设施与核心 API | ✅ DONE |
| 3 | 教材智能导入 (Markdown) | ✅ DONE |
| 4 | 动态知识图谱与向量检索 | ✅ DONE |
| 5 | 学习系统与在线代码沙箱 | ✅ DONE |
| 6 | AI Tutor 与智能诊断 | ✅ DONE |
| 7 | 完整闭环与数据联动 | ✅ DONE |
| 8 | 测试与参赛交付 | ⏳ IN_PROGRESS |

## 新增功能 (Phase 8 增强)

### 🔍 Code Quality & Pythonic Style Review
- **后端**: `analyze_pythonic_style()` — AST 静态分析引擎，检测 8 类 Pythonic 风格问题
- **后端**: `/api/workspace/style-review` 轻量端点（无需 LLM）
- **后端**: `/api/workspace/ai-review` 已集成风格分析分数到 LLM prompt
- **前端**: `StyleReviewCard.vue` — 风格评分环形图 + 问题列表 + 点击跳转行号
- **测试**: 13 项风格分析单元测试

### 🎛️ Variable Memory Visualization
- **后端**: `sandbox_runner.py` 增加变量捕获钩子，执行后序列化 `locals()` 为 JSON
- **后端**: 支持 int/float/str/bool/list/tuple/dict/set/frozenset/None/bytes/complex/Decimal/datetime/class 实例
- **后端**: `/api/workspace/run` 响应新增 `variables` 字段
- **前端**: `VariableInspector.vue` — 树形展开变量面板，类型标签着色
- **前端**: `CodingWorkspace.vue` 输出区新增 Console/变量/风格 三 Tab 切换
- **测试**: 14 项变量捕获单元测试

## 测试证据

| 测试套件 | 通过 |
|----------|------|
| API 测试 | 24 |
| 代码沙箱测试 | 6 |
| Vector RAG 测试 | 3 |
| 拓扑推荐引擎测试 | 2 |
| 教材解析引擎测试 | 2 |
| 新功能测试 (变量捕获 + 风格分析 + API) | 27 |
| E2E 集成测试 | 48 |
| **总计** | **112** |

## 待完成

- [ ] 前端组件测试覆盖
- [ ] 参赛演示视频与答辩文档

## 已知问题

1. `/api/agent/plan` 和 `/api/agent/practice` 端点为占位实现
2. Qdrant 退出时有 sqlite3 线程清理警告（不影响功能）
