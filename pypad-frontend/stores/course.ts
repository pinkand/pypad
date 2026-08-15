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
      console.error('Failed to load courses from backend:', err)
      courses.value = []
    } finally {
      loading.value = false
    }
  }

  const fetchChapters = async (courseId: string) => {
    try {
      const res = await chapterApi.getChapters(courseId)
      chapters.value = (res as any).chapters || res || []
    } catch (err) {
      console.error('Failed to load chapters from backend:', err)
      chapters.value = []
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
