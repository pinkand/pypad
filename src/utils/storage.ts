// localStorage 工具函数

const STORAGE_PREFIX = 'python-learning-os'

// 获取存储键名
const getKey = (key: string) => `${STORAGE_PREFIX}:${key}`

// 保存数据到localStorage
export const saveToStorage = <T>(key: string, data: T): void => {
  try {
    const serializedData = JSON.stringify(data)
    localStorage.setItem(getKey(key), serializedData)
  } catch (error) {
    console.error('Failed to save to localStorage:', error)
  }
}

// 从localStorage读取数据
export const loadFromStorage = <T>(key: string, defaultValue: T): T => {
  try {
    const serializedData = localStorage.getItem(getKey(key))
    if (serializedData === null) {
      return defaultValue
    }
    return JSON.parse(serializedData) as T
  } catch (error) {
    console.error('Failed to load from localStorage:', error)
    return defaultValue
  }
}

// 从localStorage删除数据
export const removeFromStorage = (key: string): void => {
  try {
    localStorage.removeItem(getKey(key))
  } catch (error) {
    console.error('Failed to remove from localStorage:', error)
  }
}

// 清空所有应用数据
export const clearStorage = (): void => {
  try {
    const keys = Object.keys(localStorage)
    keys.forEach(key => {
      if (key.startsWith(STORAGE_PREFIX)) {
        localStorage.removeItem(key)
      }
    })
  } catch (error) {
    console.error('Failed to clear localStorage:', error)
  }
}

// 检查localStorage是否可用
export const isStorageAvailable = (): boolean => {
  try {
    const testKey = '__storage_test__'
    localStorage.setItem(testKey, 'test')
    localStorage.removeItem(testKey)
    return true
  } catch {
    return false
  }
}

// 导出存储键名常量
export const STORAGE_KEYS = {
  USER_PROFILE: 'user-profile',
  KNOWLEDGE_MASTERY: 'knowledge-mastery',
  STUDY_RECORDS: 'study-records',
  WRONG_QUESTIONS: 'wrong-questions',
  LEARNING_PATHS: 'learning-paths',
  AGENT_MEMORY: 'agent-memory',
  APP_SETTINGS: 'app-settings'
} as const