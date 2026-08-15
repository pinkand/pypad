# PyPad — Project Single Source of Truth (唯一真相源)

> [!IMPORTANT]
> **声明**：本文件是 PyPad 项目的最高事实来源与最高层目标定义。
> 任何 AI Agent、开发者或代码修改，在发生冲突时均必须无条件遵循本文件的产品定位与核心闭环。未经明确人工许可，不得自行篡改项目目标。

---

## 1. 项目定位 (Product Positioning)

**PyPad 是一个 AI 驱动的 Python Learning OS（Python 学习操作系统）。**

它不仅是一个在线编程工具或教辅 UI，而是一个能够将非结构化教材转化为结构化知识图谱、根据用户实时掌握度动态生成学习路径、并提供智能闭环辅导的完整学习操作系统。

---

## 2. 核心目标 (Core Objectives)

1. **建立 Python 知识体系**：覆盖从基础语法到高级应用的完整、结构化 Python 知识大纲。
2. **教材自动结构化**：将 PDF、DOCX、Markdown 等教材智能解析为结构化章节与知识点。
3. **建立知识点关系图谱**：自动提取知识点之间的先修、依赖、关联关系，可视化展示图谱。
4. **生成个性化学习路径**：根据用户的学习目标、已有基础与实时能力评估，动态规划最佳路径。
5. **提供在线 Python 编程环境**：集成基于 Web 的 IDE (Monaco Editor)，支持安全、高效的代码执行与实时反馈。
6. **提供 AI Tutor (智能导师)**：具备 RAG 知识库与对话能力，针对当前知识点与代码报错提供精准引导。
7. **自动生成练习与代码题**：基于知识点和用户错误偏好，动态生成定制化习题与打分契约。
8. **精准记录学习行为**：全量追踪阅读时间、代码运行次数、试错轨迹与练习得分。
9. **动态调整学习路径**：基于实际掌握度算法，实时更新能力图谱并重构后续学习计划。
10. **形成完整学习闭环**：实现从教材输入到能力评估出站的全自动化、智能化闭环。

---

## 3. 核心闭环 (Core Closed Loop)

PyPad 的全流程闭环定义如下：

```text
教材 (Textbook)
  ↓
结构化知识 (Structured Knowledge)
  ↓
知识关系图谱 (Knowledge Graph & Relations)
  ↓
个性化学习路径 (Learning Path)
  ↓
沉浸式学习 (Interactive Learning)
  ↓
在线编程实践 (Code Workspace & Sandbox)
  ↓
智能练习与测评 (Practices & Evaluation)
  ↓
AI Tutor 实时反馈 (AI Feedback & Guidance)
  ↓
掌握度评估 (Mastery Assessment)
  ↓
动态调整下一步学习目标 (Next Learning Target)
```

---

## 4. 治理与改动约束 (Governance Rules)

1. **绝对禁令**：禁止任何偏离上述 10 步闭环的旁支开发。
2. **架构收敛**：新增模块必须明确映射到闭环中的某一个环节。
3. **完成判定**：只有当输入到输出的闭环链路打通且测试通过时，对应功能才算真正完成。
