import { defineStore } from 'pinia'
import { ref } from 'vue'
import { taskAPI } from '../api/task'

export const useCrawlerStore = defineStore('crawler', () => {
  const tasks = ref([])
  const templates = ref([])
  const versions = ref([])
  const favorites = ref([])
  const loading = ref(false)
  const currentTask = ref(null)

  async function fetchTasks(params) {
    loading.value = true
    try {
      const response = await taskAPI.getTasks(params)
      tasks.value = response.data.data || response.data
      return response.data
    } finally {
      loading.value = false
    }
  }

  async function fetchTaskById(id) {
    loading.value = true
    try {
      const response = await taskAPI.getTask(id)
      currentTask.value = response.data.data || response.data
      return response.data
    } finally {
      loading.value = false
    }
  }

  async function createTask(data) {
    const response = await taskAPI.createTask(data)
    if (response.data.success) {
      tasks.value.push(response.data.data)
    }
    return response.data
  }

  async function updateTask(id, data) {
    const response = await taskAPI.updateTask(id, data)
    if (response.data.success) {
      const index = tasks.value.findIndex(t => t.id === id)
      if (index !== -1) {
        tasks.value[index] = { ...tasks.value[index], ...response.data.data }
      }
      if (currentTask.value && currentTask.value.id === id) {
        currentTask.value = { ...currentTask.value, ...response.data.data }
      }
    }
    return response.data
  }

  async function deleteTask(id) {
    const response = await taskAPI.deleteTask(id)
    if (response.data.success) {
      tasks.value = tasks.value.filter(t => t.id !== id)
      if (currentTask.value && currentTask.value.id === id) {
        currentTask.value = null
      }
    }
    return response.data
  }

  async function startTask(id) {
    const response = await taskAPI.startTask(id)
    if (response.data.success) {
      const index = tasks.value.findIndex(t => t.id === id)
      if (index !== -1) {
        tasks.value[index] = { ...tasks.value[index], status: 'running' }
      }
      if (currentTask.value && currentTask.value.id === id) {
        currentTask.value = { ...currentTask.value, status: 'running' }
      }
    }
    return response.data
  }

  async function stopTask(id) {
    const response = await taskAPI.stopTask(id)
    if (response.data.success) {
      const index = tasks.value.findIndex(t => t.id === id)
      if (index !== -1) {
        tasks.value[index] = { ...tasks.value[index], status: 'stopped' }
      }
      if (currentTask.value && currentTask.value.id === id) {
        currentTask.value = { ...currentTask.value, status: 'stopped' }
      }
    }
    return response.data
  }

  async function fetchTemplates() {
    const response = await taskAPI.getTemplates()
    templates.value = response.data.data || response.data
    return response.data
  }

  async function createTemplate(data) {
    const response = await taskAPI.createTemplate(data)
    if (response.data.success) {
      templates.value.push(response.data.data)
    }
    return response.data
  }

  async function deleteTemplate(id) {
    const response = await taskAPI.deleteTemplate(id)
    if (response.data.success) {
      templates.value = templates.value.filter(t => t.id !== id)
    }
    return response.data
  }

  async function fetchVersions(taskId) {
    const response = await taskAPI.getVersions(taskId)
    versions.value = response.data.data || response.data
    return response.data
  }

  async function rollbackVersion(taskId, versionIndex) {
    const response = await taskAPI.rollbackVersion(taskId, versionIndex)
    return response.data
  }

  async function fetchFavorites() {
    const response = await taskAPI.getFavorites()
    favorites.value = response.data.data || response.data
    return response.data
  }

  async function toggleFavorite(taskId) {
    const isFav = favorites.value.some(f => f.id === taskId || f.task_id === taskId)
    if (isFav) {
      const response = await taskAPI.removeFavorite(taskId)
      if (response.data.success) {
        favorites.value = favorites.value.filter(f => f.id !== taskId && f.task_id !== taskId)
      }
      return response.data
    } else {
      const response = await taskAPI.addFavorite(taskId)
      if (response.data.success) {
        favorites.value.push(response.data.data)
      }
      return response.data
    }
  }

  return {
    tasks,
    templates,
    versions,
    favorites,
    loading,
    currentTask,
    fetchTasks,
    fetchTaskById,
    createTask,
    updateTask,
    deleteTask,
    startTask,
    stopTask,
    fetchTemplates,
    createTemplate,
    deleteTemplate,
    fetchVersions,
    rollbackVersion,
    fetchFavorites,
    toggleFavorite
  }
})