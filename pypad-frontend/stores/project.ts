import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { Project } from '@/types/knowledge'
import { projectApi } from '@/services/api'

export const useProjectStore = defineStore('project', () => {
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)
  const loading = ref(false)

  const fetchProjects = async () => {
    loading.value = true
    try {
      const res = await projectApi.getProjects()
      projects.value = (res as any).projects || res || []
    } catch (err) {
      projects.value = []
    } finally {
      loading.value = false
    }
  }

  const loadProject = async (id: string) => {
    loading.value = true
    try {
      const res = await projectApi.getProject(id)
      currentProject.value = (res as any).project || res
    } catch (err) {
      currentProject.value = null
    } finally {
      loading.value = false
    }
  }

  return {
    projects,
    currentProject,
    loading,
    fetchProjects,
    loadProject
  }
})
