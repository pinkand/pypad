export const MASTERY_COLORS = {
  excellent: 'var(--status-mastered)',
  good: 'var(--status-learning)',
  weak: 'var(--status-weak)',
  unlearned: 'var(--status-unlearned)'
} as const

export const MASTERY_THRESHOLDS = {
  excellent: 90,
  good: 60,
  weak: 1
} as const

export const KNOWLEDGE_DOMAINS = [
  '基础语法',
  '数据类型',
  '控制流',
  '函数',
  '面向对象',
  '高级特性'
] as const

export const NODE_CATEGORIES = [
  '基础语法',
  '数据类型',
  '控制流',
  '函数',
  '面向对象',
  '模块与包',
  '文件IO',
  '异常处理',
  '迭代器与生成器',
  '装饰器',
  '异步编程',
  '网络编程',
  '数据库',
  'Web框架',
  '测试',
  '性能优化',
  '设计模式',
  '并发编程',
] as const

export const AGENT_LABELS: Record<string, string> = {
  planner: '学习规划师',
  tutor: 'AI导师',
  coder: '代码分析师',
  practice: '练习生成器',
  memory: '记忆管理器',
}
