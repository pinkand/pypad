# PyPad 竞品分析摘要

> 基于 Hyperskill、Dataquest、Khan Academy、roadmap.sh、Studyield、LearnHouse 等 30+ 平台分析。

## PyPad 定位

**AI-Native Python Learning OS** — 融合知识图谱、学习路径、在线编程、AI 辅导、掌握度评估的完整学习操作系统。

## 最值得借鉴的 12 个设计

| 来源 | 能力 | PyPad 应用 |
|------|------|-----------|
| roadmap.sh | 知识地图 | 升级知识图谱为可交互路线图 |
| Hyperskill | 项目驱动 | Project-First 学习模式 |
| Dataquest | 课程→练习→项目 | 完善学习路径流程 |
| Brilliant | 交互式学习 | 增强代码编辑器交互 |
| Duolingo | 每日循环+个性化 | Next Best Action + Review Engine |
| Khan Academy | 掌握度系统 | 多维度技能画像 |
| LeetCode | 挑战引擎 | Pattern-based 练习 |
| Exercism | 代码审查 | 增强 AI Code Review |
| Jupyter | Notebook | 考虑 Notebook 集成 |
| nbgrader | 自动评分 | 完善评估系统 |
| Studyield | AI+知识图谱 | 多 Agent + Teach-back |
| LearnHouse | 现代 LMS | 参考模块化架构 |

## 建议六层架构

```text
Learner OS (目标/画像/进度/AI)
  ↓
Knowledge Graph (概念/技能/关系)
  ↓
Learning Engine (路径/掌握度/复习/推荐)
  ↓
Practice Engine (测验/挑战/代码/Notebook)
  ↓
Project Engine (项目/仓库/测试/审查)
  ↓
AI Layer (导师/审查员/规划师/Agent)
```

## 核心数据模型建议

```
User → Goal, LearningPath, SkillProfile, KnowledgeState,
       PracticeHistory, ProjectHistory, ErrorHistory, LearningEvents

Knowledge → Concept, Skill, Pattern, Example, Exercise, Project, Resource

Relations → prerequisite, related, used_by, tested_by, practiced_by
```

## 优先实施建议

| 阶段 | 内容 | 参考 |
|------|------|------|
| 短期 | 交互式学习模块、每日学习循环、技能画像 | Brilliant, Duolingo, Khan Academy |
| 中期 | 项目系统、挑战引擎、代码审查增强 | Hyperskill, LeetCode, Exercism |
| 长期 | 学习分析、多 Agent 教学、平台生态 | Studyield, Khanmigo, Udemy |

## 参考产品优先级

| 产品 | 价值 | 重点 |
|------|------|------|
| Hyperskill | ⭐⭐⭐⭐⭐ | 项目驱动学习 |
| Dataquest | ⭐⭐⭐⭐⭐ | 课程→练习→项目 |
| Khan Academy | ⭐⭐⭐⭐⭐ | 掌握度系统 |
| roadmap.sh | ⭐⭐⭐⭐⭐ | 知识地图 |
| Studyield | ⭐⭐⭐⭐⭐ | AI+知识图谱+分析 |
| LearnHouse | ⭐⭐⭐⭐⭐ | 现代 LMS 架构 |
| Jupyter/nbgrader | ⭐⭐⭐⭐⭐ | Notebook+自动评分 |
| Brilliant | ⭐⭐⭐⭐ | 交互式设计 |
| Duolingo | ⭐⭐⭐⭐ | 每日学习循环 |
| Exercism | ⭐⭐⭐⭐ | 代码审查 |
