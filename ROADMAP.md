# PyPad 路线图

> **闸门铁律**：前一阶段 Gate 未通过，禁止进入下一阶段。

## 阶段概览

| Phase | 名称 | Gate |
|-------|------|------|
| 0 | 项目基线与治理规范 | ✅ |
| 1 | 需求与核心架构收敛 | ✅ |
| 2 | 后端基础设施与核心 API | ✅ |
| 3 | 教材智能导入 (Markdown) | ✅ |
| 4 | 动态知识图谱与向量检索 | ✅ |
| 5 | 学习系统与代码沙箱 | ✅ |
| 6 | AI Tutor 与智能诊断 | ✅ |
| 7 | 完整闭环与数据联动 | ✅ |
| 8 | 测试与参赛交付 | 🔴 |

## Gate 0 ✅ — 项目基线
- [x] 治理文档建立 (PROJECT/ROADMAP/ACCEPTANCE/ARCHITECTURE/PROGRESS/宪法)
- [x] 测试框架可用

## Gate 1 ✅ — 架构收敛
- [x] 数据库 Schema 定义完整
- [x] 前端路由与组件框架就位
- [x] 数据模型关系校验无错

## Gate 2 ✅ — 后端 API
- [x] Auth JWT 注册/登录/Me
- [x] 知识节点与图谱 Endpoint
- [x] 代码执行 `/api/workspace/run`
- [x] test_api.py 24 项 PASS

## Gate 3 ✅ — 教材导入
- [x] Markdown 解析 → 知识节点 + 依赖关系
- [x] RAG 索引自动更新
- [x] test_textbook_parser.py 2 项 PASS

## Gate 4 ✅ — 知识图谱 & RAG
- [x] 动态增删节点与边
- [x] 搜索/筛选/高亮
- [x] RAG 检索上下文
- [x] Qdrant 向量库集成
- [x] test_rag.py 3 项 PASS

## Gate 5 ✅ — 学习系统 & 沙箱
- [x] AST 安全扫描 + 超时强杀
- [x] Session 追踪 + 练习评分
- [x] test_sandbox.py 6 项 PASS

## Gate 6 ✅ — AI Tutor
- [x] SSE 流式对话
- [x] RAG 上下文增强
- [x] 对话持久化
- [ ] LLM 失败重试与降级

## Gate 7 ✅ — 完整闭环
- [x] 掌握度更新 + 艾宾浩斯衰减
- [x] DAG 拓扑排序推荐
- [x] test_e2e.py 48 项 PASS
- [ ] Dashboard 掌握度雷达图

## Gate 8 🔴 — 测试与交付
- [x] 后端测试 112 项全通过（含 27 项新功能测试）
- [x] 前端 7 个页面补全
- [x] Code Quality & Pythonic Style Review（AST 静态分析 + LLM 增强）
- [x] Variable Memory Visualization（沙箱变量捕获 + 树形展开 UI）
- [ ] 前端组件测试
- [ ] 参赛演示视频与文档
