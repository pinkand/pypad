import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { Course, Chapter, Section } from '@/types/knowledge'
import { courseApi, chapterApi } from '@/services/api'

export const useCourseStore = defineStore('course', () => {
  const courses = ref<Course[]>([])
  const currentCourse = ref<Course | null>(null)
  const chapters = ref<Chapter[]>([])
  const currentChapter = ref<Chapter | null>(null)
  const currentSection = ref<Section | null>(null)
  const loading = ref(false)

  const activeCourseId = computed(() => currentCourse.value?.id || null)

  const fetchCourses = async () => {
    loading.value = true
    try {
      const res = await courseApi.getCourses()
      courses.value = (res as any).courses || res || []
      if (courses.value.length > 0 && !currentCourse.value) {
        currentCourse.value = courses.value[0]!
      }
    } catch (err) {
      console.warn('Fallback to local default course data')
      courses.value = [
        {
          id: 'py-course-1',
          title: 'Python 程序设计项目化教程',
          description: '清华大学出版社出版 · 11大项目驱动全流程学习 (基础语法、数据结构、OOP、文件IO与AI编程)',
          level: 'beginner',
          category: 'Python项目化',
          sortOrder: 1,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        }
      ]
      currentCourse.value = courses.value[0]!
    } finally {
      loading.value = false
    }
  }

  const fetchChapters = async (courseId: string) => {
    try {
      const res = await chapterApi.getChapters(courseId)
      chapters.value = (res as any).chapters || res || []
    } catch (err) {
      chapters.value = [
        { id: "chap-1", courseId: "py-course-1", title: "项目1：猜价赢大奖", description: "Python开发环境搭建与编程规范", sortOrder: 1 },
        { id: "chap-2", courseId: "py-course-1", title: "项目2：简单计算器", description: "基本输入输出、数据类型与运算符", sortOrder: 2 },
        { id: "chap-3", courseId: "py-course-1", title: "项目3：健康数据分析", description: "条件分支与循环控制流结构", sortOrder: 3 },
        { id: "chap-4", courseId: "py-course-1", title: "项目4：词语踪迹寻觅", description: "字符串处理、检索与切片操作", sortOrder: 4 },
        { id: "chap-5", courseId: "py-course-1", title: "项目5：核心价值观问答挑战", description: "列表与元组容器数据结构", sortOrder: 5 },
        { id: "chap-6", courseId: "py-course-1", title: "项目6：公益图书角管理系统", description: "函数定义、参数传递与模块化设计", sortOrder: 6 },
        { id: "chap-7", courseId: "py-course-1", title: "项目7：校园热点话题统计", description: "字典与集合的高效查找与统计", sortOrder: 7 },
        { id: "chap-8", courseId: "py-course-1", title: "项目8：天气预报应用程序", description: "模块化开发、内置标准库与第三方包", sortOrder: 8 },
        { id: "chap-9", courseId: "py-course-1", title: "项目9：个人财务管理系统", description: "面向对象编程 (OOP) 核心理念", sortOrder: 9 },
        { id: "chap-10", courseId: "py-course-1", title: "项目10：销售数据分析", description: "文件 I/O 操作与数据持久化存储", sortOrder: 10 },
        { id: "chap-11", courseId: "py-course-1", title: "项目11：居民肺活量监测", description: "异常捕获处理与程序健壮性设计", sortOrder: 11 },
      ]
    }
  }

  const selectCourse = (course: Course) => {
    currentCourse.value = course
    fetchChapters(course.id)
  }

  return {
    courses,
    currentCourse,
    chapters,
    currentChapter,
    currentSection,
    activeCourseId,
    loading,
    fetchCourses,
    fetchChapters,
    selectCourse
  }
})
