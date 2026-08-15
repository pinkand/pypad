# PyPad 前端组件与按钮命名注册表

> 本文档列出项目中每一个 Vue 组件、按钮、交互元素的命名、位置与功能，方便精准定位和修改。

---

## 目录结构

```text
pypad-frontend/
├── App.vue                              # 根组件
├── main.ts                              # 应用入口
├── views/
│   ├── LoginView.vue                    # 登录/注册页
│   └── MainView.vue                     # 主页面（承载所有子组件）
├── components/
│   ├── universe/
│   │   └── KnowledgeUniverse.vue        # 3D 知识宇宙（Three.js）
│   ├── knowledge/
│   │   ├── KnowledgePanel.vue           # 知识详情面板（全屏）
│   │   └── LearningGuidePanel.vue       # 左侧学习指南面板
│   ├── map/
│   │   ├── KnowledgeMap.vue             # 2D 知识图谱（VueFlow）
│   │   ├── MapNode.vue                  # 图谱节点
│   │   ├── MapEdge.vue                  # 图谱连线
│   │   └── ContextMenu.vue             # 右键上下文菜单
│   ├── workspace/
│   │   └── CodingWorkspace.vue          # 代码工作区（Monaco Editor）
│   ├── agent/
│   │   ├── ChatWindow.vue               # AI 聊天窗口
│   │   ├── TaskPanel.vue                # 任务面板
│   │   └── CodeEditor.vue               # 代码编辑器入口页
│   ├── ai/
│   │   ├── FloatingBall.vue             # 右下角悬浮球 + 导航标签
│   │   └── AgentPanel.vue               # AI 助手面板容器
│   ├── user/
│   │   ├── UserChip.vue                 # 左下角用户头像
│   │   └── ProfileDrawer.vue            # 用户资料抽屉
│   └── common/
│       └── PerformanceMonitor.vue       # 性能监控浮窗
├── stores/                              # Pinia 状态管理
├── services/
│   └── api.ts                           # API 接口层
├── router/
│   └── index.ts                         # 路由配置
├── types/
│   ├── knowledge.ts                     # 知识相关类型定义
│   ├── agent.ts                         # AI 助手类型定义
│   └── user.ts                          # 用户类型定义
└── utils/
    ├── constants.ts                     # 常量定义
    ├── color.ts                         # 颜色工具
    └── storage.ts                       # localStorage 工具
```

---

## 1. App.vue — 根组件

| 元素 | 类型 | 功能 |
|:---|:---|:---|
| `<RouterView />` | 路由出口 | 渲染当前路由对应的页面 |
| `<PerformanceMonitor />` | 性能监控 | 右下角 FPS/内存监控浮窗 |

**挂载时自动执行：**
- `userStore.restoreSession()` — 恢复登录状态
- `userStore.loadDashboardStats()` — 加载仪表盘统计
- `userStore.loadStudyRecords()` — 加载学习记录

---

## 2. LoginView.vue — 登录/注册页

**路由：** `/login`

| 元素 | ID/名称 | 类型 | 功能 |
|:---|:---|:---|:---|
| 用户名输入框 | `input-username` | `<input>` | 输入用户名 |
| 邮箱输入框 | `input-email` | `<input>` | 输入邮箱（仅注册模式） |
| 显示名称输入框 | `input-displayName` | `<input>` | 输入显示名称（仅注册模式） |
| 密码输入框 | `input-password` | `<input>` | 输入密码 |
| 错误提示 | `error-msg` | `<div>` | 显示登录/注册错误信息 |
| 提交按钮 | `btn-submit` | `<button type="submit">` | 登录或注册 |
| 切换模式按钮 | `btn-toggle-mode` | `<button>` | 切换登录/注册模式 |
| 跳过链接 | `link-skip` | `<router-link>` | 跳过登录直接进入主页 |

**状态变量：**
- `isLogin` — 当前是否为登录模式
- `loading` — 提交中状态
- `errorMsg` — 错误信息

---

## 3. MainView.vue — 主页面

**路由：** `/`, `/universe`, `/map`, `/map/:nodeId`, `/agent`, `/dashboard`

| 子组件 | 层级 | 功能 |
|:---|:---|:---|
| `<KnowledgeUniverse />` | Layer 0 | 3D 知识宇宙背景 |
| `<LearningGuidePanel />` | Layer 1 | 左侧学习指南 |
| `<KnowledgePanel />` | Layer 2 | 知识详情全屏面板 |
| `<UserChip />` | Layer 2 | 左下角用户头像 |
| `<ProfileDrawer />` | Layer 4 | 用户资料抽屉 |
| `<FloatingBall />` | Layer 3 | 右下角悬浮球 |
| `<AgentPanel />` | Layer 4 | AI 助手面板 |
| `<CodingWorkspace />` | Layer 5 | 代码工作区全屏覆盖 |
| 通知容器 | Overlay | 全局 Toast 通知 |

**URL 同步：**
- `?nodeId=xxx` — 自动打开对应知识点面板

---

## 4. KnowledgeUniverse.vue — 3D 知识宇宙

**位置：** 主页面背景层（Layer 0）

| 元素 | 类型 | 功能 |
|:---|:---|:---|
| `<canvas>` | `canvasRef` | Three.js WebGL 渲染画布 |
| `<div css-container>` | `cssContainerRef` | CSS2D 渲染器容器（HTML 卡片） |
| 标题 "PyPad" | `.universe-title h1` | 左上角项目标题 |
| 副标题 "知识流动系统" | `.universe-title p` | 左上角副标题 |

**动态生成的节点卡片（CSS2DObject）：**

| 元素 | CSS 类名 | 功能 |
|:---|:---|:---|
| 节点卡片 | `.node-card` | 可点击的知识节点 |
| 根节点卡片 | `.node-card.node-root` | Python核心根节点 |
| 卡片内容 | `.card-content` | 卡片主体容器 |
| 状态指示点 | `.card-dot` | 显示掌握度颜色 |
| 节点标题 | `.card-title` | 知识点名称 |
| 展开/收起指示器 | `.expand-indicator` | `+` / `-` 图标 |
| 进度条背景 | `.progress-bar-bg` | 掌握度进度条背景 |
| 进度条填充 | `.progress-bar-fill` | 掌握度进度条填充 |
| 进度文本 | `.progress-text` | 掌握度百分比 |
| 卡片底部状态 | `.card-footer` | 已掌握/学习中/薄弱/未学习 |

**交互行为：**
- 点击节点卡片 → 展开/收起子节点 + 粒子聚合动画 + 打开知识面板
- 鼠标移动 → 粒子跟随鼠标引力效果

---

## 5. LearningGuidePanel.vue — 左侧学习指南

**位置：** 主页面左侧（Layer 1）

| 元素 | CSS 类名 | 类型 | 功能 |
|:---|:---|:---|:---|
| 面板容器 | `.learning-guide-panel` | `<div>` | 学习指南面板 |
| 折叠按钮 | `.toggle-btn` | `<button>` | 展开/收起面板 |
| **学习状态区域** | | | |
| 区域标题 "学习状态" | `.section-title` | `<h3>` | 区域标题 |
| 已掌握统计 | `.stat-row` (mastered) | `<div>` | `已掌握 X/Y` |
| 学习中统计 | `.stat-row` (learning) | `<div>` | `学习中 X/Y` |
| 薄弱统计 | `.stat-row` (weak) | `<div>` | `薄弱 X/Y` |
| 未学习统计 | `.stat-row` (unlearned) | `<div>` | `未学习 X/Y` |
| 状态点 | `.status-dot` | `<span>` | 颜色指示点 |
| **推荐学习路径区域** | | | |
| 区域标题 "推荐学习路径" | `.section-title` | `<h3>` | 区域标题 |
| 推荐节点列表 | `.node-list` | `<ul>` | 推荐节点列表 |
| 推荐节点项 | `.node-item` | `<li>` | 可点击，打开对应知识点面板 |
| **需要复习区域** | | | |
| 区域标题 "需要复习" | `.section-title` | `<h3>` | 区域标题 |
| 薄弱节点列表 | `.node-list` | `<ul>` | 薄弱节点列表 |
| 薄弱节点项 | `.node-item.warning` | `<li>` | 可点击，打开对应知识点面板 |

---

## 6. KnowledgePanel.vue — 知识详情面板

**位置：** 全屏覆盖（Layer 2, z-index: 60）

| 元素 | CSS 类名 | 类型 | 功能 |
|:---|:---|:---|:---|
| 面板容器 | `.knowledge-panel` | `<div>` | 全屏知识面板 |
| **顶部导航栏** | | | |
| 知识点标题 | `.node-title` | `<h2>` | 当前知识点名称 |
| 知识点分类 | `.node-category` | `<span>` | 教材名 · 分类 |
| 教材卡片切换按钮 | `.toggle-textbook-btn` | `<button>` | 展开/收起左侧教材卡片 |
| 关闭按钮 | `.close-btn` | `<button>` | 关闭知识面板 |
| **全屏图谱区域** | | | |
| 图谱容器 | `.full-map-wrapper` | `<div>` | 承载 KnowledgeMap |
| **左侧教材卡片（浮动）** | | | |
| 教材卡片容器 | `.floating-textbook-card` | `<div>` | 左侧浮动教材卡 |
| 精讲概览卡 | `.textbook-card.overview-card` | `<div>` | 📖 教材精讲与实战背景 |
| 核心要点卡 | `.textbook-card.points-card` | `<div>` | 📌 核心知识要点 |
| 踩坑避雷卡 | `.textbook-card.pitfalls-card` | `<div>` | ⚠️ 踩坑避雷与注意事项 |
| 代码示例卡 | `.textbook-card.code-card` | `<div>` | 💻 教材项目实操代码 |
| 代码预览 | `.code-preview` | `<pre>` | 代码块展示 |
| 载入工作区按钮 | `.btn-load-code` | `<button>` | 将代码注入 Monaco 编辑器 |
| **底部操作栏（浮动）** | | | |
| 操作栏容器 | `.floating-panel-footer` | `<div>` | 底部浮动操作区 |
| AI 导师精讲按钮 | `.btn.btn-primary` | `<button>` | 打开 AI 助手讲解当前知识点 |
| 生成实战练习按钮 | `.btn.btn-secondary` | `<button>` | 打开 AI 助手生成练习题 |

---

## 7. KnowledgeMap.vue — 2D 知识图谱

**位置：** KnowledgePanel 内部全屏区域

| 元素 | CSS 类名 | 类型 | 功能 |
|:---|:---|:---|:---|
| **顶部筛选工具栏** | | | |
| 工具栏容器 | `.map-toolbar` | `<div>` | 居中胶囊形工具栏 |
| 搜索输入框 | `.map-search-input` | `<input>` | 搜索知识点名称/描述 |
| 分类筛选 | `.map-select` | `<select>` | 按分类筛选节点 |
| 掌握度筛选 | `.map-select` | `<select>` | 按掌握度筛选节点 |
| 清除筛选按钮 | `.clear-filter-btn` | `<button>` | 清除所有筛选条件 |
| **统计信息** | | | |
| 节点统计 | `.map-stats` | `<div>` | `X / Y 个知识点` |
| **VueFlow 图谱** | | | |
| 自定义节点 | `<MapNode>` | 组件 | 知识节点卡片 |
| 自定义连线 | `<MapEdge>` | 组件 | 知识关系连线 |
| 背景网格 | `<Background>` | 组件 | VueFlow 背景 |
| 控制器 | `<Controls>` | 组件 | 缩放/适应控件 |
| 小地图 | `<MiniMap>` | 组件 | 右下角小地图 |
| **右键菜单** | | | |
| 上下文菜单 | `<ContextMenu>` | 组件 | 节点右键操作菜单 |

---

## 8. MapNode.vue — 图谱节点

**位置：** KnowledgeMap 内部

| 元素 | 类型 | 功能 |
|:---|:---|:---|
| 节点容器 | `<div>` | 可点击的知识节点卡片 |
| 输入连接点 | `<Handle type="target">` | VueFlow 左侧连接点 |
| 节点名称 | `<h4>` | 知识点名称 |
| 掌握度徽章 | `<span>` | `X%` 掌握度 |
| 描述文本 | `<p>` | 知识点描述（2行截断） |
| 分类标签 | `<span>` | 知识点分类 |
| 重要性指示器 | `<span>` | 黄色圆点（数量=重要度） |
| 输出连接点 | `<Handle type="source">` | VueFlow 右侧连接点 |

---

## 9. MapEdge.vue — 图谱连线

**位置：** KnowledgeMap 内部

| 元素 | 类型 | 功能 |
|:---|:---|:---|
| 连线路径 | `<path>` | 贝塞尔曲线连线 |

**颜色规则：**
- `prerequisite` → 蓝色 `#3b82f6`
- `extends` → 紫色 `#8b5cf6`
- 其他 → 灰色 `#6b7280`
- `soft` 强度 → 虚线

---

## 10. ContextMenu.vue — 右键菜单

**位置：** KnowledgeMap 内部

| 元素 | 类型 | 功能 |
|:---|:---|:---|
| 菜单容器 | `<div>` | 右键弹出菜单 |
| AI 解释按钮 | `<button>` (explain) | 💡 触发 AI 解释当前知识点 |
| 生成练习按钮 | `<button>` (practice) | 📝 触发 AI 生成练习题 |
| 加入学习计划按钮 | `<button>` (plan) | 📋 加入学习计划 |
| 查看错误记录按钮 | `<button>` (errors) | ❌ 查看错误记录 |

---

## 11. CodingWorkspace.vue — 代码工作区

**位置：** 全屏覆盖（Layer 5, z-index: 50）

| 元素 | CSS 类名 | 类型 | 功能 |
|:---|:---|:---|:---|
| 工作区容器 | `.workspace-overlay` | `<div>` | 全屏毛玻璃覆盖 |
| **顶部导航栏** | | | |
| 关闭按钮 | `.close-btn` | `<button>` | 关闭工作区 |
| 文件名 | `.file-name` | `<span>` | `main.py` |
| 状态点 | `.status-dot` | `<span>` | 绿色保存状态 |
| **模式切换** | | | |
| Teach 模式按钮 | `.seg-btn` (Teach) | `<button>` | 切换到教学模式 |
| Practice 模式按钮 | `.seg-btn` (Practice) | `<button>` | 切换到练习模式 |
| Code 模式按钮 | `.seg-btn` (Code) | `<button>` | 切换到自由编码模式 |
| **左侧面板** | | | |
| **Teach 模式** | | | |
| AI 讲义标题 | `.panel-header-small h3` | `<h3>` | `AI 讲义` |
| 学习徽章 | `.badge.info-badge` | `<span>` | `Learning` |
| 知识点标题 | `.teach-content h2` | `<h2>` | 从后端 aiSummary 加载 |
| 知识点概览 | `.teach-content p` | `<p>` | 从后端 aiSummary 加载 |
| 核心要点列表 | `.teach-content ul` | `<ul>` | 从后端 aiSummary.keyPoints 加载 |
| 常见陷阱列表 | `.teach-content ul` | `<ul>` | 从后端 aiSummary.commonPitfalls 加载 |
| **Practice 模式** | | | |
| 实战练习标题 | `.panel-header-small h3` | `<h3>` | `实战练习` |
| 挑战徽章 | `.badge.warning-badge` | `<span>` | `Challenge` |
| 练习题标题 | `.practice-content h2` | `<h2>` | 从后端 practice API 加载 |
| 练习题描述 | `.practice-content p` | `<p>` | 从后端 practice API 加载 |
| 测试用例列表 | `.test-cases` | `<div>` | 从后端 testCases 加载 |
| 测试用例项 | `.test-case` | `<div>` | 输入/预期输出 |
| **Code 模式** | | | |
| AI Tutor 标题 | `.panel-header-small h3` | `<h3>` | `AI Tutor` |
| 活跃徽章 | `.badge` | `<span>` | `Active` |
| 当前知识点 | `.tutor-text` | `<p>` | 当前选中知识点名称 |
| 知识描述 | `.tutor-text` | `<p>` | 当前选中知识点描述 |
| AI 代码解释入口 | `.task-card` | `<div>` | 点击触发 AI 代码解释 |
| **编辑器区域** | | | |
| Monaco 编辑器 | `<vue-monaco-editor>` | 组件 | Python 代码编辑器 |
| **工具栏按钮** | | | |
| Run 按钮 | `.action-btn.run-btn` | `<button>` | ▶ 运行代码 |
| Submit 按钮 | `.action-btn.submit-btn` | `<button>` | ✈ 提交练习（仅 Practice 模式） |
| Hint 按钮 | `.action-btn.ai-btn` | `<button>` | 💡 获取提示（仅 Practice 模式） |
| Review 按钮 | `.action-btn.ai-btn` | `<button>` | 🧪 AI 代码审查（仅 Code 模式） |
| Explain 按钮 | `.action-btn.ai-btn` | `<button>` | 📖 AI 代码解释（Teach/Code 模式） |
| **输出区域** | | | |
| Console 标题 | `.panel-header-small h3` | `<h3>` | `Console` |
| 终端输出 | `.terminal-output pre` | `<pre>` | 代码运行输出 |
| AI 评价容器 | `.ai-evaluation` | `<div>` | AI 反馈信息 |
| AI 评价图标 | `.eval-header svg` | `<svg>` | 成功/警告/错误图标 |
| AI 评价标题 | `.eval-header span` | `<span>` | `AI Insights` |
| AI 评价内容 | `.eval-message` | `<p>` | AI 反馈详情文本 |

---

## 12. FloatingBall.vue — 悬浮球 + 导航标签

**位置：** 主页面右下角

| 元素 | CSS 类名 | 类型 | 功能 |
|:---|:---|:---|:---|
| 悬浮球容器 | `.floating-ball-wrapper` | `<div>` | 定位容器 |
| **快捷导航标签** | | | |
| 标签容器 | `.nav-tags` | `<div>` | 标签列表容器 |
| AI 导师标签 | `.nav-tag` (agent) | `<button>` | 🎓 打开 AI 助手面板 |
| 代码工作区标签 | `.nav-tag` (workspace) | `<button>` | 💻 打开代码工作区 |
| 教材精讲标签 | `.nav-tag` (teach) | `<button>` | 📖 打开教学模式工作区 |
| 实战练习标签 | `.nav-tag` (practice) | `<button>` | ✏️ 打开练习模式工作区 |
| 薄弱点标签 | `.nav-tag` (weak) | `<button>` | ⚠️ 跳转到第一个薄弱知识点 |
| 学习统计标签 | `.nav-tag` (dashboard) | `<button>` | 📊 跳转到学习仪表盘 |
| **主悬浮球** | | | |
| 悬浮球按钮 | `.floating-ball` | `<button>` | 展开/收起导航标签 |
| 发光效果 | `.glow-effect` | `<div>` | 内发光装饰 |
| 图标 | `.icon` | `<svg>` | 烧瓶/实验图标 |

**交互行为：**
- 点击悬浮球 → 展开/收起导航标签
- 点击标签 → 执行对应跳转/操作
- 展开时图标旋转 45°

---

## 13. AgentPanel.vue — AI 助手面板

**位置：** 主页面右下角悬浮（z-index: 55）

| 元素 | CSS 类名 | 类型 | 功能 |
|:---|:---|:---|:---|
| 面板容器 | `.agent-panel` | `<div>` | AI 助手面板 |
| **标签页切换** | | | |
| Chat 标签 | `.tab-btn` (chat) | `<button>` | 切换到聊天 |
| Tasks 标签 | `.tab-btn` (task) | `<button>` | 切换到任务 |
| Code 标签 | `.tab-btn` (code) | `<button>` | 切换到代码编辑器入口 |
| 关闭按钮 | `.close-btn` | `<button>` | 关闭面板 |
| **内容区域** | | | |
| Chat 窗口 | `<ChatWindow>` | 组件 | AI 聊天窗口 |
| Task 面板 | `<TaskPanel>` | 组件 | 学习任务列表 |
| Code 编辑器入口 | `<CodeEditor>` | 组件 | 代码工作区启动页 |

---

## 14. ChatWindow.vue — AI 聊天窗口

**位置：** AgentPanel 内部

| 元素 | CSS 类名 | 类型 | 功能 |
|:---|:---|:---|:---|
| **头部** | | | |
| Agent 头像 | `.agent-avatar` | `<div>` | 当前 Agent 类型图标 |
| Agent 名称 | `.agent-name` | `<span>` | 当前 Agent 中文名 |
| Agent 状态 | `.agent-status` | `<span>` | `在线` + 绿色脉冲点 |
| **Agent 切换标签** | | | |
| 知识导师标签 | `.agent-tab` (tutor) | `<button>` | 📚 切换到导师模式 |
| 练习生成标签 | `.agent-tab` (practice) | `<button>` | ✏️ 切换到练习模式 |
| 代码分析标签 | `.agent-tab` (coder) | `<button>` | 💻 切换到代码分析模式 |
| 学习规划标签 | `.agent-tab` (planner) | `<button>` | 📋 切换到规划模式 |
| 记忆管理标签 | `.agent-tab` (memory) | `<button>` | 🧠 切换到记忆管理模式 |
| 清空对话按钮 | `.clear-btn` | `<button>` | 🗑 清空聊天记录 |
| **消息区域** | | | |
| 消息容器 | `.messages-area` | `<div>` | 可滚动消息列表 |
| **空状态** | | | |
| 空状态容器 | `.empty-chat` | `<div>` | 无消息时显示 |
| 空状态图标 | `.empty-orb` | `<div>` | 浮动发光球 |
| 空状态标题 | `.empty-title` | `<h3>` | Agent 名称 |
| 空状态描述 | `.empty-desc` | `<p>` | 引导文案 |
| **快捷操作芯片（空状态）** | | | |
| 芯片容器 | `.quick-chips` | `<div>` | 快捷操作芯片组 |
| 解释知识点芯片 | `.quick-chip` (explain) | `<button>` | 💡 解释知识点 |
| 生成练习芯片 | `.quick-chip` (practice) | `<button>` | ✏️ 生成练习 |
| 分析代码芯片 | `.quick-chip` (analyze) | `<button>` | 🔍 分析代码 |
| 制定计划芯片 | `.quick-chip` (plan) | `<button>` | 📅 制定计划 |
| **消息列表** | | | |
| 消息行（用户） | `.message-row--user` | `<div>` | 用户消息（右侧蓝色气泡） |
| 消息行（AI） | `.message-row--ai` | `<div>` | AI 消息（左侧白色气泡） |
| AI 消息头像 | `.msg-avatar` | `<div>` | Agent 图标 |
| 用户气泡 | `.bubble--user` | `<div>` | 蓝色圆角气泡 |
| AI 气泡 | `.bubble--ai` | `<div>` | 白色毛玻璃气泡 |
| 气泡内容 | `.bubble-content` | `<div>` | 消息文本 |
| 气泡时间 | `.bubble-time` | `<div>` | 消息时间戳 |
| **输入区域** | | | |
| 快捷操作行 | `.quick-actions-row` | `<div>` | 有消息时的快捷芯片 |
| 输入容器 | `.input-wrapper` | `<div>` | 输入框容器（聚焦时高亮） |
| 文本输入框 | `.chat-input` | `<textarea>` | 消息输入（Enter 发送） |
| 发送按钮 | `.send-btn` | `<button>` | ✈ 发送消息 |
| **思考指示器** | | | |
| 思考气泡 | `.typing-bubble` | `<div>` | AI 正在输入 |
| 思考点动画 | `.typing-dots` | `<div>` | 三个跳动的点 |

---

## 15. TaskPanel.vue — 任务面板

**位置：** AgentPanel 内部

| 元素 | 类型 | 功能 |
|:---|:---|:---|
| 标题 "学习任务" | `<h3>` | 面板标题 |
| 待开始数量 | `<p>` | `X 个待开始` |
| **进行中任务** | | |
| 区域标题 "进行中" | `<h4>` | 分组标题 |
| 任务卡片 | `<div>` | 进行中的任务 |
| 任务类型图标 | `<span>` | 学习/练习/调试/复习图标 |
| 任务标题 | `<span>` | 任务名称 |
| 任务状态标签 | `<span>` | 进行中/待开始/已完成 |
| 任务描述 | `<p>` | 任务详情 |
| 完成按钮 | `<button>` | ✅ 标记为已完成 |
| 暂停按钮 | `<button>` | ⏸ 标记为待开始 |
| **待开始任务** | | |
| 区域标题 "待开始" | `<h4>` | 分组标题 |
| 开始按钮 | `<button>` | ▶ 标记为进行中 |
| **已完成任务** | | |
| 区域标题 "已完成" | `<h4>` | 分组标题 |
| 任务卡片（灰色） | `<div>` | 已完成的任务（删除线） |
| **空状态** | | |
| 空状态图标 | `<div>` | 任务清单图标 |
| 空状态文案 | `<p>` | "暂无学习任务" |

---

## 16. CodeEditor.vue — 代码编辑器入口

**位置：** AgentPanel 内部（Code 标签）

| 元素 | CSS 类名 | 类型 | 功能 |
|:---|:---|:---|:---|
| 启动器容器 | `.glass-launcher` | `<div>` | 毛玻璃卡片 |
| 图标 | `.launcher-icon` | `<div>` | 文件图标 |
| 标题 | `.launcher-title` | `<h3>` | `AI Coding Workspace` |
| 描述 | `.launcher-desc` | `<p>` | 功能说明 |
| 进入按钮 | `.launch-btn` | `<button>` | `Enter Workspace` |

---

## 17. UserChip.vue — 用户头像

**位置：** 主页面左下角（z-index: 20）

| 元素 | CSS 类名 | 类型 | 功能 |
|:---|:---|:---|:---|
| 用户头像按钮 | `.user-chip` | `<button>` | 打开/关闭用户资料抽屉 |
| 头像图片 | `.avatar` | `<img>` | DiceBear 随机头像 |
| 未读徽章 | `.badge` | `<div>` | 未读消息数量 |

---

## 18. ProfileDrawer.vue — 用户资料抽屉

**位置：** 主页面左下角悬浮（z-index: 55）

| 元素 | CSS 类名 | 类型 | 功能 |
|:---|:---|:---|:---|
| 抽屉容器 | `.profile-drawer` | `<div>` | 用户资料面板 |
| **头部** | | | |
| 头像大图 | `.avatar-large` | `<img>` | 用户头像 |
| 用户名 | `.username` | `<h2>` | 用户昵称 |
| 等级 | `.level` | `<span>` | `Level X 知识探索者` |
| 关闭按钮 | `.close-btn` | `<button>` | 关闭抽屉 |
| **标签页导航** | | | |
| 资料标签 | `.tab-btn` (profile) | `<button>` | 👤 资料 |
| AI 配置标签 | `.tab-btn` (ai) | `<button>` | 🤖 AI 配置 |
| 设置标签 | `.tab-btn` (system) | `<button>` | ⚙️ 设置 |
| **Tab 1: 资料** | | | |
| 进度条背景 | `.progress-bar-bg` | `<div>` | 全局掌握度进度条 |
| 进度条填充 | `.progress-bar-fill` | `<div>` | 掌握度填充 |
| 进度文本 | `.progress-text` | `<div>` | `全局知识掌握度 X%` |
| 用户昵称输入 | `.form-input` | `<input>` | 修改用户昵称 |
| 绑定邮箱输入 | `.form-input` | `<input>` | 修改邮箱 |
| 学习目标输入 | `.form-input` | `<input>` | 修改学习目标 |
| 保存资料按钮 | `.save-btn.btn-primary` | `<button>` | `保存资料修改` |
| **Tab 2: AI 配置** | | | |
| Provider 选择 | `.form-select` | `<select>` | 选择 AI 提供商 |
| API Key 输入 | `.form-input` | `<input>` | 输入 API Key |
| 显示/隐藏 Key | `.toggle-eye-btn` | `<button>` | 👁 切换密码可见性 |
| Base URL 输入 | `.form-input` | `<input>` | 输入 API 地址 |
| Model 名称输入 | `.form-input` | `<input>` | 输入模型名称 |
| Temperature 滑块 | `.form-range` | `<input range>` | 创造力调节 (0-1) |
| 保存 AI 配置按钮 | `.save-btn.btn-primary` | `<button>` | `测试并保存全局 AI 配置` |
| **Tab 3: 设置** | | | |
| 背景画风选择 | `.form-select` | `<select>` | 🌌 高阶弥散流光 / ⚪ 原版极简画风 |
| 主题切换按钮 | `.menu-btn` | `<button>` | 🌙/☀ 切换暗色/浅色模式 |
| 通知数量徽章 | `.badge` | `<span>` | 未读通知数 |
| 通知列表 | `.notification-list` | `<ul>` | 系统通知列表 |
| 退出账号按钮 | `.menu-btn.text-danger` | `<button>` | 🚪 `退出当前账号` |

---

## 19. PerformanceMonitor.vue — 性能监控

**位置：** 全局右下角（z-index: 50）

| 元素 | 类型 | 功能 |
|:---|:---|:---|
| 监控面板 | `<div>` | FPS + 内存显示 |
| FPS 数值 | `<span>` | 当前帧率（颜色编码） |
| 内存数值 | `<span>` | 当前内存使用量 |
| 关闭按钮 | `<button>` | 隐藏监控面板 |
| 触发按钮 | `<button>` | 右下角图表图标，点击显示监控 |

**快捷键：** `Ctrl+P` 切换显示

---

## 20. Stores 状态管理

| Store | 文件 | 核心状态 | 核心方法 |
|:---|:---|:---|:---|
| `useAppStore` | `stores/app.ts` | `currentView`, `panelOpen`, `agentOpen`, `isWorkspaceOpen` | `openPanel()`, `toggleAgent()`, `openWorkspace()` |
| `useKnowledgeStore` | `stores/knowledge.ts` | `nodes`, `edges`, `masteryMap`, `selectedNode` | `loadData()`, `selectNode()`, `setNodeMastery()` |
| `useUserStore` | `stores/user.ts` | `authUser`, `profile`, `stats`, `aiConfig` | `login()`, `register()`, `logout()`, `saveAiConfig()` |
| `useCourseStore` | `stores/course.ts` | `courses`, `chapters`, `currentCourse` | `fetchCourses()`, `fetchChapters()` |
| `usePracticeStore` | `stores/practice.ts` | `practices`, `currentPractice` | `fetchPracticesByNode()`, `submitPractice()` |
| `useSessionStore` | `stores/session.ts` | `currentSession`, `eventLogs` | `startSession()`, `recordEvent()`, `endSession()` |
| `useWorkspaceStore` | `stores/workspace.ts` | `currentCode`, `stdout`, `stderr` | `runCode()`, `requestAIReview()` |
| `useAgentStore` | `stores/agent.ts` | `messages`, `currentAgent`, `tasks` | `addMessage()`, `setAgent()`, `loadHistory()` |
| `useProjectStore` | `stores/project.ts` | `projects`, `currentProject` | `fetchProjects()`, `loadProject()` |
| `useReviewStore` | `stores/review.ts` | `reviews`, `currentReview` | `fetchUserReviews()`, `getReviewById()` |

---

## 21. API 接口层 (services/api.ts)

| API 模块 | 方法 | 后端端点 | 功能 |
|:---|:---|:---|:---|
| `authApi` | `register()` | `POST /api/auth/register` | 用户注册 |
| | `login()` | `POST /api/auth/login` | 用户登录 |
| | `me()` | `GET /api/auth/me` | 获取当前用户信息 |
| `knowledgeApi` | `getNodes()` | `GET /api/knowledge/nodes` | 获取所有知识节点 |
| | `getNode(id)` | `GET /api/knowledge/nodes/{id}` | 获取单个知识节点 |
| | `getRelations()` | `GET /api/knowledge/relations` | 获取知识关系边 |
| | `getCategories()` | `GET /api/knowledge/categories` | 获取知识分类列表 |
| `userApi` | `getKnowledge()` | `GET /api/user/knowledge` | 获取用户掌握度 |
| | `updateKnowledge()` | `POST /api/user/knowledge` | 更新掌握度 |
| | `recordStudy()` | `POST /api/user/study` | 记录学习行为 |
| | `getStudyRecords()` | `GET /api/user/study-records` | 获取学习记录 |
| `agentApi` | `chat()` | `POST /api/agent/chat` | AI 对话（同步） |
| | `getHistory()` | `GET /api/agent/history` | 获取聊天历史 |
| | `generatePlan()` | `POST /api/agent/plan` | 生成学习计划 |
| | `generatePractice()` | `POST /api/agent/practice` | 生成练习题 |
| `dashboardApi` | `getOverview()` | `GET /api/dashboard/overview` | 仪表盘概览 |
| | `getProgress()` | `GET /api/dashboard/progress` | 学习进度 |
| `courseApi` | `getCourses()` | `GET /api/courses` | 获取课程列表 |
| | `getCourse(id)` | `GET /api/courses/{id}` | 获取单个课程 |
| | `getCourseTree(id)` | `GET /api/courses/{id}/tree` | 获取课程树 |
| `chapterApi` | `getChapters()` | `GET /api/chapters` | 获取章节列表 |
| | `getSections(id)` | `GET /api/chapters/{id}/sections` | 获取小节列表 |
| `projectApi` | `getProjects()` | `GET /api/projects` | 获取项目列表 |
| | `getProject(id)` | `GET /api/projects/{id}` | 获取单个项目 |
| `practiceApi` | `getPracticesByNode()` | `GET /api/practices` | 获取知识点练习 |
| | `generateAIPractice()` | `POST /api/practices/generate-ai` | AI 生成练习题 |
| | `submitPractice()` | `POST /api/practices/{id}/submit` | 提交练习代码 |
| `sessionApi` | `startSession()` | `POST /api/sessions/start` | 开始学习会话 |
| | `recordEvent()` | `POST /api/sessions/{id}/events` | 记录会话事件 |
| | `endSession()` | `POST /api/sessions/{id}/end` | 结束学习会话 |
| | `getTimeline()` | `GET /api/sessions/{id}/timeline` | 获取会话时间线 |
| `workspaceApi` | `runCode()` | `POST /api/workspace/run` | 运行代码 |
| | `getRunHistory()` | `GET /api/workspace/runs/{id}` | 获取运行历史 |
| | `requestAIReview()` | `POST /api/workspace/ai-review` | AI 代码审查 |
| `reviewApi` | `getReview(id)` | `GET /api/reviews/{id}` | 获取代码审查 |
| | `getUserReviews()` | `GET /api/reviews/user/{id}` | 获取用户审查列表 |
| `analyticsApi` | `getOverview()` | `GET /api/analytics/overview` | 分析概览 |

---

## 22. 路由配置 (router/index.ts)

| 路径 | 名称 | 组件 | 页面标题 |
|:---|:---|:---|:---|
| `/login` | `login` | `LoginView` | 登录 |
| `/` | `main` | `MainView` | PyPad |
| `/universe` | `universe` | `MainView` | 知识宇宙 |
| `/map` | `map` | `MainView` | 知识图谱 |
| `/map/:nodeId` | `map-node` | `MainView` | 知识图谱 |
| `/agent` | `agent` | `MainView` | AI学习助手 |
| `/dashboard` | `dashboard` | `MainView` | 学习仪表盘 |

---

## 23. 常量定义 (utils/constants.ts)

| 常量 | 值 | 用途 |
|:---|:---|:---|
| `MASTERY_THRESHOLDS.excellent` | `90` | 已掌握阈值 |
| `MASTERY_THRESHOLDS.good` | `60` | 学习中阈值 |
| `MASTERY_THRESHOLDS.weak` | `1` | 薄弱阈值 |
| `AGENT_LABELS.tutor` | `AI导师` | Agent 中文名 |
| `AGENT_LABELS.practice` | `练习生成器` | Agent 中文名 |
| `AGENT_LABELS.coder` | `代码分析师` | Agent 中文名 |
| `AGENT_LABELS.planner` | `学习规划师` | Agent 中文名 |
| `AGENT_LABELS.memory` | `记忆管理器` | Agent 中文名 |
