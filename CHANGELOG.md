# Changelog

## [Phase 0-7] 已完成

- 治理框架：PROJECT.md / ROADMAP.md / ACCEPTANCE.md / ARCHITECTURE.md / PROGRESS.md / 宪法
- 后端 API：Auth、Knowledge Graph、Courses、Workspace、Sessions、Practices、Agent、Dashboard
- 前端 SPA：Vue 3 + Vite + Tailwind + Monaco + Three.js + Cytoscape.js + VueFlow
- 代码沙箱：AST 安全扫描 + Subprocess/Docker 隔离
- RAG 引擎：Qdrant 向量库 + TF-IDF 降级兜底
- 学习闭环：艾宾浩斯遗忘曲线 + DAG 拓扑排序推荐
- 测试：API 24 项 + E2E 48 项全通过

## [Phase 8] 前端页面补全

- 新增 7 个独立页面：Dashboard / Courses / Projects / Practice / Agent / Analytics / Textbooks
- 更新路由：所有页面独立路由，不再全部指向 MainView
- 新增顶部导航栏
