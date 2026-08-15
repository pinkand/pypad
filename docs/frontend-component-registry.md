# PyPad 前端组件注册表

## 目录结构

```text
pypad-frontend/
├── App.vue                          # 根组件
├── main.ts                          # 入口
├── views/
│   ├── LoginView.vue                # 登录/注册
│   ├── MainView.vue                 # 知识宇宙主页（含顶部导航）
│   ├── DashboardView.vue            # 学习仪表盘
│   ├── CoursesView.vue              # 课程中心
│   ├── ProjectsView.vue             # 项目实战
│   ├── PracticeView.vue             # 练习中心
│   ├── AgentView.vue                # AI 导师
│   ├── AnalyticsView.vue            # 学习分析
│   └── TextbooksView.vue            # 教材管理
├── components/
│   ├── universe/KnowledgeUniverse   # 3D 知识宇宙 (Three.js)
│   ├── knowledge/KnowledgePanel     # 知识详情面板
│   ├── knowledge/LearningGuidePanel # 左侧学习指南
│   ├── map/KnowledgeMap             # 2D 图谱 (VueFlow)
│   ├── map/MapNode / MapEdge        # 图谱节点与连线
│   ├── map/ContextMenu              # 右键菜单
│   ├── workspace/CodingWorkspace    # Monaco 代码工作区
│   ├── ai/FloatingBall              # 右下角悬浮球
│   ├── ai/AgentPanel                # AI 助手面板
│   ├── agent/ChatWindow             # AI 聊天窗口
│   ├── agent/TaskPanel              # 任务面板
│   ├── agent/CodeEditor             # 代码编辑器入口
│   ├── user/UserChip                # 用户头像
│   ├── user/ProfileDrawer           # 用户资料抽屉
│   └── common/PerformanceMonitor    # 性能监控
├── stores/                          # Pinia 状态管理
│   ├── app.ts / user.ts / knowledge.ts
│   ├── course.ts / practice.ts / session.ts
│   ├── workspace.ts / agent.ts / project.ts / review.ts
├── services/api.ts                  # API 接口层
├── router/index.ts                  # 路由配置
├── types/                           # TypeScript 类型
└── utils/                           # 工具函数
```

## 路由表

| 路径 | 页面 | 说明 |
|------|------|------|
| `/login` | LoginView | 登录注册 |
| `/` | MainView | 3D 知识宇宙 |
| `/map` | MainView | 2D 知识图谱 |
| `/dashboard` | DashboardView | 学习仪表盘 |
| `/courses` | CoursesView | 课程浏览 |
| `/projects` | ProjectsView | 项目实战 |
| `/practice` | PracticeView | 练习中心 |
| `/agent` | AgentView | AI 导师 |
| `/analytics` | AnalyticsView | 学习分析 |
| `/textbooks` | TextbooksView | 教材管理 |

## API 接口

| 模块 | 端点 | 功能 |
|------|------|------|
| Auth | `/api/auth/register\|login\|me` | 用户认证 |
| Knowledge | `/api/knowledge/nodes\|graph\|search\|rag-context` | 知识图谱 |
| Courses | `/api/courses\|chapters` | 课程章节 |
| Practices | `/api/practices\|generate-ai\|submit` | 练习系统 |
| Sessions | `/api/sessions/start\|events\|end\|timeline` | 学习会话 |
| Workspace | `/api/workspace/run\|ai-review` | 代码执行 |
| Agent | `/api/agent/chat\|chat-stream\|history` | AI 对话 |
| Dashboard | `/api/dashboard/overview\|progress` | 仪表盘 |
| User | `/api/user/knowledge\|study\|recommend-path` | 用户数据 |
| Analytics | `/api/analytics/overview` | 学习分析 |
| Textbook | `/api/textbook/upload` | 教材导入 |
