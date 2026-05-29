<template>
  <div class="tasks-page">
    <NavBar />
    <div class="tasks-content">
      <div class="page-header">
        <div class="header-left">
          <h1 class="page-title">任务管理</h1>
          <span class="task-count">{{ filteredTasks.length }} 个任务</span>
        </div>
        <button class="btn-create" @click="$router.push('/tasks/new')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          新建任务
        </button>
      </div>

      <div class="filter-bar">
        <div class="filter-left">
          <div class="status-filter">
            <button
              v-for="s in statusOptions"
              :key="s.value"
              class="status-btn"
              :class="{ active: activeStatus === s.value }"
              @click="activeStatus = s.value"
            >{{ s.label }}</button>
          </div>
          <div class="search-input-wrapper">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.35-4.35"/>
            </svg>
            <input
              v-model="searchKeyword"
              type="text"
              class="search-input"
              placeholder="搜索任务名称或URL..."
              @keyup.enter="handleSearch"
            />
          </div>
        </div>
        <div class="filter-right">
          <button class="btn-refresh" @click="fetchTasks">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="23 4 23 10 17 10"/>
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
            </svg>
          </button>
        </div>
      </div>

      <div v-if="loading" class="skeleton-list">
        <div v-for="n in 5" :key="n" class="skeleton-card">
          <div class="skeleton-line w-60"></div>
          <div class="skeleton-line w-40"></div>
          <div class="skeleton-line w-80"></div>
        </div>
      </div>

      <div v-else-if="filteredTasks.length === 0" class="empty-state">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
            <line x1="8" y1="21" x2="16" y2="21"/>
            <line x1="12" y1="17" x2="12" y2="21"/>
          </svg>
        </div>
        <p class="empty-text">暂无任务数据</p>
        <p class="empty-desc">点击上方"新建任务"按钮创建您的第一个爬虫任务</p>
      </div>

      <div v-else class="task-list">
        <div
          v-for="task in paginatedTasks"
          :key="task.id"
          class="task-card"
          @click="openTaskDetail(task)"
        >
          <div class="task-card-top">
            <div class="task-card-left">
              <div class="task-favorite" :class="{ starred: task.favorite }" @click.stop="toggleFavorite(task)">
                <svg viewBox="0 0 24 24" :fill="task.favorite ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                </svg>
              </div>
              <div class="task-info">
                <h3 class="task-name">{{ task.name }}</h3>
                <p class="task-url">{{ task.url }}</p>
              </div>
            </div>
            <div class="task-card-right">
              <span class="task-status-tag" :class="'status-' + task.status">
                <span class="status-dot"></span>
                {{ statusLabel(task.status) }}
              </span>
            </div>
          </div>

          <div class="task-card-meta">
            <div v-if="task.createdAt" class="task-meta-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                <line x1="16" y1="2" x2="16" y2="6"/>
                <line x1="8" y1="2" x2="8" y2="6"/>
                <line x1="3" y1="10" x2="21" y2="10"/>
              </svg>
              <span>{{ task.createdAt }}</span>
            </div>
            <div class="task-meta-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
              <span>{{ getRealtimeExecutionTime(task) }}</span>
            </div>
            <div class="task-meta-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 20V10"/>
                <path d="M12 20V4"/>
                <path d="M6 20v-6"/>
              </svg>
              <span>{{ getRealtimeDataCount(task) }} 条数据</span>
            </div>
          </div>

          <div class="task-card-progress">
            <div class="progress-header">
              <span class="progress-label">成功率</span>
              <span class="progress-value" :class="task.status === 'completed' ? 'high' : task.status === 'failed' ? 'low' : getRealtimeSuccessRate(task) >= 90 ? 'high' : getRealtimeSuccessRate(task) >= 60 ? 'mid' : 'low'">{{ getRealtimeSuccessRate(task) }}%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" :class="task.status === 'completed' ? 'high' : task.status === 'failed' ? 'low' : getRealtimeSuccessRate(task) >= 90 ? 'high' : getRealtimeSuccessRate(task) >= 60 ? 'mid' : 'low'" :style="{ width: getRealtimeSuccessRate(task) + '%' }"></div>
            </div>
            <div v-if="displayTaskError(task)" class="error-tip" :title="task._errorMessage">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              <span class="error-tip-text">{{ formatTaskError(task._errorMessage) }}</span>
            </div>
          </div>

          <div class="task-card-actions" @click.stop>
            <button
              v-if="task.status === 'running'"
              class="task-btn btn-stop"
              @click="stopTask(task)"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" stroke="none">
                <rect x="6" y="4" width="4" height="16"/>
                <rect x="14" y="4" width="4" height="16"/>
              </svg>
              停止
            </button>
            <button
              v-else
              class="task-btn btn-start"
              @click="startTask(task)"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" stroke="none">
                <polygon points="5 3 19 12 5 21 5 3"/>
              </svg>
              启动
            </button>
            <button
              v-if="canRestartTask(task)"
              class="task-btn btn-restart"
              @click="restartTask(task)"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="23 4 23 10 17 10"/>
                <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
              </svg>
              重新启动
            </button>
            <button class="task-btn btn-edit" @click="openTaskEdit(task)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
              编辑
            </button>
            <button class="task-btn btn-delete" @click="deleteTask(task)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              </svg>
              删除
            </button>
          </div>
        </div>
      </div>

      <div v-if="filteredTasks.length > 0 && !loading" class="pagination">
        <button class="page-btn" :disabled="currentPage <= 1" @click="currentPage--">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
        </button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <button class="page-btn" :disabled="currentPage >= totalPages" @click="currentPage++">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import NavBar from '../components/NavBar.vue'
import { taskAPI } from '../api/task'
import { crawlerAPI } from '../api/crawler'
import { buildTaskRunCreatePayload, shouldCloneTaskBeforeStart } from '../utils/taskCopy'

const router = useRouter()
const loading = ref(true)
const tasks = ref([])
const total = ref(0)
const searchKeyword = ref('')
const activeStatus = ref('all')
const currentPage = ref(1)
const pageSize = 10
let updateTimer = null
const tick = ref(0)

// 记录每个任务开始时的时间戳（用于前端计时）
const taskStartTimes = ref({})

const statusOptions = [
  { label: '全部', value: 'all' },
  { label: '运行中', value: 'running' },
  { label: '待执行', value: 'pending' },
  { label: '已完成', value: 'completed' },
  { label: '失败', value: 'failed' }
]

const statusLabelMap = { running: '运行中', pending: '待执行', completed: '已完成', failed: '失败' }
function statusLabel(status) { return statusLabelMap[status] || status }

// 监听筛选条件变化，自动重新获取数据
watch(activeStatus, () => {
  currentPage.value = 1
  fetchTasks()
})

const filteredTasks = computed(() => {
  return tasks.value
})

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

const paginatedTasks = computed(() => {
  return tasks.value
})

function handleSearch() {
  currentPage.value = 1
  fetchTasks()
}

async function toggleFavorite(task) {
  try {
    const isFav = task.is_favorite || task.favorite
    let res
    if (isFav) {
      res = await taskAPI.removeFavorite(task.id)
    } else {
      res = await taskAPI.addFavorite(task.id)
    }
    if (res.data.success) {
      task.is_favorite = !isFav
      task.favorite = !isFav
      ElMessage.success(res.data.message)
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

function openTaskDetail(task) {
  router.push({ path: `/tasks/${task.id}` })
}

function openTaskEdit(task) {
  router.push({ path: `/tasks/${task.id}`, query: { edit: '1' } })
}

function applyRunningState(task) {
  task.status = 'running'
  task._startTime = Date.now()
  task._dataCount = 0
  task._currentPage = 0
  task._succeededPages = 0
  task._totalPages = task._totalPages || 1
  taskStartTimes.value[task.id] = task._startTime
}

async function syncTaskFromServer(taskId) {
  try {
    const res = await taskAPI.getTask(taskId)
    if (res.data.success) {
      const idx = tasks.value.findIndex(t => String(t.id) === String(taskId))
      if (idx >= 0) {
        tasks.value[idx] = mapTaskFromApi(res.data.data)
      }
    }
  } catch (e) {
    console.error('同步任务状态失败:', e)
  }
}

async function copyAndStartTask(task) {
  const detailRes = await taskAPI.getTask(task.id)
  if (!detailRes.data.success) {
    throw new Error(detailRes.data.message || '获取任务详情失败')
  }
  const source = detailRes.data.data
  const createPayload = buildTaskRunCreatePayload(source)
  const createRes = await taskAPI.createTask(createPayload)
  if (!createRes.data.success) {
    throw new Error(createRes.data.message || '创建新任务失败')
  }
  const newTaskId = createRes.data.data?.task_id
  if (!newTaskId) {
    throw new Error('未返回新任务 ID')
  }
  const startRes = await taskAPI.startTask(newTaskId)
  if (!startRes.data.success) {
    throw new Error(startRes.data.message || '启动新任务失败')
  }
  return newTaskId
}

async function directStartTask(task, successMessage = '任务已启动') {
  const startRes = await taskAPI.startTask(task.id)
  if (!startRes.data.success) {
    throw new Error(startRes.data.message || '启动失败')
  }
  applyRunningState(task)
  await syncTaskFromServer(task.id)
  ElMessage.success(successMessage)
  return task.id
}

async function runTaskStartFlow(task) {
  const needClone = shouldCloneTaskBeforeStart(task)
  if (needClone) {
    const newTaskId = await copyAndStartTask(task)
    currentPage.value = 1
    await fetchTasks()
    const newTask = tasks.value.find(t => String(t.id) === String(newTaskId))
    if (newTask) {
      applyRunningState(newTask)
    }
    ElMessage.success(`已复制并启动新任务 #${newTaskId}`)
    return newTaskId
  }
  return directStartTask(task)
}

function canRestartTask(task) {
  return task.status !== 'running' && shouldCloneTaskBeforeStart(task)
}

async function stopTask(task) {
  try {
    const res = await taskAPI.stopTask(task.id)
    if (res.data.success) {
      delete taskStartTimes.value[task.id]
      await syncTaskFromServer(task.id)
      ElMessage.success('任务已停止')
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (e) {
    const msg = e.response?.data?.message || e.message || '操作失败'
    ElMessage.error(msg)
  }
}

async function startTask(task) {
  try {
    await runTaskStartFlow(task)
  } catch (e) {
    const msg = e.response?.data?.message || e.message || '操作失败'
    ElMessage.error(msg)
  }
}

async function restartTask(task) {
  try {
    await directStartTask(task, '任务已重新启动')
  } catch (e) {
    const msg = e.response?.data?.message || e.message || '操作失败'
    ElMessage.error(msg)
  }
}

async function deleteTask(task) {
  try {
    await ElMessageBox.confirm(
      `确定要删除任务「${task.name}」吗？此操作不可撤销。`,
      '确认删除',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    const res = await taskAPI.deleteTask(task.id)
    if (res.data.success) {
      tasks.value = tasks.value.filter(t => t.id !== task.id)
      total.value = Math.max(0, total.value - 1)
      ElMessage.success('删除成功')
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (e) {
    if (e !== 'cancel' && e !== 'close') {
      ElMessage.error('删除失败')
    }
  }
}

function normalizeStatus(status) {
  const s = (status || 'pending').toLowerCase()
  if (s === 'error') return 'failed'
  return s
}

function formatTaskError(msg) {
  if (!msg) return ''
  const text = String(msg).replace(/\s+/g, ' ').trim()
  return text.length > 160 ? `${text.slice(0, 160)}…` : text
}

function displayTaskError(task) {
  if (!task._errorMessage) return false
  return task.status === 'failed' || task.status === 'stopped'
}

function mapTaskFromApi(item) {
  const crawlerStatus = item.crawler_status || {}
  const engineMatches = crawlerStatus.task_id != null
    && String(crawlerStatus.task_id) === String(item.id)
  const liveStatus = engineMatches ? crawlerStatus : {}
  // 处理时间：优先使用实时 elapsed_seconds
  const elapsed = liveStatus.elapsed_seconds || item.execution_time || 0
  const hours = Math.floor(elapsed / 3600)
  const minutes = Math.floor((elapsed % 3600) / 60)
  const seconds = elapsed % 60
  let executionTime
  if (hours > 0) {
    executionTime = `${hours}h ${minutes}m`
  } else if (minutes > 0) {
    executionTime = `${minutes}m ${seconds}s`
  } else {
    executionTime = `${seconds}s`
  }

  // 成功率以数据库统计为准
  let successRate = parseFloat(item.success_rate)
  if (Number.isNaN(successRate)) successRate = 0

  const taskStatus = normalizeStatus(item.status)
  const config = item.config && typeof item.config === 'object' ? item.config : {}
  const lastExec = config._last_execution || {}
  const errorMessage = (
    item.error_message
    || liveStatus.error_message
    || lastExec.error_message
    || ''
  )

  // 记录任务开始时间（如果任务正在运行）
  if (taskStatus === 'running' && !taskStartTimes.value[item.id]) {
    taskStartTimes.value[item.id] = Date.now() - (elapsed * 1000)
  } else if (taskStatus !== 'running') {
    delete taskStartTimes.value[item.id]
  }

  return {
    id: item.id,
    name: item.name,
    url: item.target_url || item.url || '',
    createdAt: item.created_at || '',
    status: taskStatus,
    config,
    data_count: item.data_count || liveStatus.collected_count || 0,
    _executionTime: elapsed,
    _startTime: taskStartTimes.value[item.id],
    _dataCount: item.data_count || liveStatus.collected_count || 0,
    _currentPage: liveStatus.current_page || 0,
    _totalPages: liveStatus.total_pages || item.config?.total_pages || 1,
    _succeededPages: liveStatus.succeeded_pages || 0,
    _errorMessage: errorMessage,
    executionTime: executionTime,
    dataCount: item.data_count || liveStatus.collected_count || 0,
    successRate: successRate,
    favorite: item.is_favorite === 1 || item.is_favorite === true || item.favorite === true,
    is_favorite: item.is_favorite === 1 || item.is_favorite === true || item.favorite === true
  }
}

// 计算实时执行时间（依赖 tick 触发每秒重算）
function getRealtimeExecutionTime(task) {
  void tick.value
  if (task.status === 'running' && task._startTime) {
    const elapsed = Math.floor((Date.now() - task._startTime) / 1000)
    const hours = Math.floor(elapsed / 3600)
    const minutes = Math.floor((elapsed % 3600) / 60)
    const seconds = elapsed % 60
    if (hours > 0) return `${hours}h ${minutes}m`
    if (minutes > 0) return `${minutes}m ${seconds}s`
    return `${seconds}s`
  }
  return task.executionTime
}

// 计算实时数据量
function getRealtimeDataCount(task) {
  void tick.value
  if (task.status === 'running') {
    return task._dataCount ?? 0
  }
  return task.dataCount ?? 0
}

// 计算实时成功率（基于成功采集页数 / 总页数）
function getRealtimeSuccessRate(task) {
  void tick.value
  if (task.status === 'completed') {
    return Math.round(task.successRate ?? 0)
  }
  if (task.status === 'failed') {
    return Math.round(task.successRate ?? 0)
  }
  if (task.status !== 'running') {
    return Math.round(task.successRate ?? 0)
  }
  const totalPages = Math.max(1, task._totalPages || 1)
  const succeededPages = task._succeededPages || 0
  return Math.round((succeededPages / totalPages) * 100)
}

async function fetchTasks() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize
    }
    if (activeStatus.value !== 'all') {
      params.status = activeStatus.value
    }
    if (searchKeyword.value.trim()) {
      params.keyword = searchKeyword.value.trim()
    }
    const res = await taskAPI.getTasks(params)
    if (res.data.success) {
      const data = res.data.data
      tasks.value = (data.list || []).map(mapTaskFromApi)
      total.value = data.total || 0
    } else {
      ElMessage.error(res.data.message || '获取任务列表失败')
      tasks.value = []
      total.value = 0
    }
  } catch (e) {
    console.error('获取任务列表失败:', e)
    tasks.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchTasks()
  // 每秒更新运行中任务的状态
  updateTimer = setInterval(() => {
    const hasRunningTasks = tasks.value.some(t => t.status === 'running')
    if (hasRunningTasks) {
      tick.value += 1
      crawlerAPI.getStatus().then(res => {
        if (res.data.success) {
          const engineStatus = res.data.data
          const engineTaskId = engineStatus.task_id
          let shouldRefreshList = false
          tasks.value.forEach(task => {
            if (task.status === 'running' && engineTaskId && String(engineTaskId) === String(task.id)) {
              task._dataCount = engineStatus.collected_count || 0
              task._currentPage = engineStatus.current_page || 0
              task._totalPages = engineStatus.total_pages || task._totalPages || 1
              task._succeededPages = engineStatus.succeeded_pages || 0
              if (engineStatus.elapsed_seconds != null) {
                task._executionTime = engineStatus.elapsed_seconds
              }
              if (engineStatus.error_message) {
                task._errorMessage = engineStatus.error_message
              }
              if (engineStatus.status === 'error') {
                task.status = 'failed'
              }
              if (['completed', 'idle', 'error', 'stopped'].includes(engineStatus.status)) {
                shouldRefreshList = true
              }
            }
          })
          if (shouldRefreshList) {
            fetchTasks()
          }
        }
      }).catch(() => {})
    }
  }, 1000)
})

onUnmounted(() => {
  if (updateTimer) {
    clearInterval(updateTimer)
  }
})
</script>

<style scoped>
.tasks-page {
  min-height: 100vh;
  background-color: var(--bg-primary);
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.018) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.018) 1px, transparent 1px);
  background-size: 40px 40px;
}

.tasks-page::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background:
    radial-gradient(ellipse 80% 60% at 50% -20%, rgba(76, 110, 245, 0.06), transparent),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(16, 185, 129, 0.04), transparent);
  pointer-events: none;
  z-index: 0;
}

.tasks-content {
  max-width: 1080px;
  margin: 0 auto;
  padding: 40px 24px 80px;
  position: relative;
  z-index: 1;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 14px;
}

.page-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

.task-count {
  font-size: 13px;
  color: var(--text-muted);
  font-weight: 500;
}

.btn-create {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 22px;
  background: var(--gradient-primary);
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 4px 16px rgba(var(--accent-rgb), 0.3);
}

.btn-create:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(76, 110, 245, 0.45);
}

.btn-create svg {
  width: 18px;
  height: 18px;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.status-filter {
  display: flex;
  gap: 4px;
  background: var(--bg-card);
  border-radius: 10px;
  padding: 4px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.status-btn {
  padding: 7px 15px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.status-btn:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.04);
}

.status-btn.active {
  color: var(--active-color);
  background: var(--active-bg);
  font-weight: 600;
}

.search-input-wrapper {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: var(--text-muted);
  pointer-events: none;
}

.search-input {
  width: 240px;
  padding: 10px 14px 10px 40px;
  font-size: 13px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  outline: none;
  transition: all 0.25s ease;
}

.search-input::placeholder {
  color: var(--text-muted);
}

.search-input:focus {
  border-color: rgba(76, 110, 245, 0.4);
  box-shadow: 0 0 0 3px rgba(76, 110, 245, 0.08);
}

.btn-refresh {
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.25s ease;
}

.btn-refresh:hover {
  color: var(--text-primary);
  border-color: rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.05);
}

.btn-refresh svg {
  width: 18px;
  height: 18px;
}

.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.skeleton-card {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 28px;
  border: 1px solid var(--border-color);
}

.skeleton-line {
  height: 14px;
  background: var(--border-color);
  border-radius: 7px;
  margin-bottom: 10px;
  animation: shimmer 1.5s ease-in-out infinite;
}

.skeleton-line.w-60 { width: 60%; }
.skeleton-line.w-40 { width: 40%; }
.skeleton-line.w-80 { width: 80%; }

@keyframes shimmer {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
  border-radius: 20px;
  background: var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.empty-icon svg {
  width: 36px;
  height: 36px;
}

.empty-text {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 13px;
  color: var(--text-muted);
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-card {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 22px 26px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.task-card:hover {
  background: var(--bg-card);
  border-color: rgba(255, 255, 255, 0.12);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
}

.task-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 14px;
}

.task-card-left {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  flex: 1;
  min-width: 0;
}

.task-favorite {
  padding-top: 2px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.25s ease;
  flex-shrink: 0;
}

.task-favorite:hover,
.task-favorite.starred {
  color: #fbbf24;
}

.task-favorite svg {
  width: 18px;
  height: 18px;
}

.task-info {
  flex: 1;
  min-width: 0;
}

.task-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
  letter-spacing: -0.2px;
}

.task-url {
  font-size: 12px;
  color: var(--text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-status-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-running {
  background: rgba(16, 185, 129, 0.12);
  color: #34d399;
}
.status-running .status-dot {
  background: #34d399;
  box-shadow: 0 0 6px rgba(52, 211, 153, 0.5);
  animation: pulse 1.5s ease-in-out infinite;
}

.status-pending {
  background: rgba(76, 110, 245, 0.12);
  color: #7c8aff;
}
.status-pending .status-dot {
  background: #7c8aff;
}

.status-completed {
  background: rgba(46, 204, 113, 0.15);
  color: #2ecc71;
  border: 1px solid rgba(46, 204, 113, 0.3);
}
.status-completed .status-dot {
  background: #2ecc71;
}

.status-running {
  background: rgba(52, 152, 219, 0.15);
  color: #3498db;
  border: 1px solid rgba(52, 152, 219, 0.3);
}
.status-running .status-dot {
  background: #3498db;
}

.status-pending {
  background: rgba(155, 89, 182, 0.15);
  color: #9b59b6;
  border: 1px solid rgba(155, 89, 182, 0.3);
}
.status-pending .status-dot {
  background: #9b59b6;
}

.status-failed {
  background: rgba(239, 68, 68, 0.12);
  color: var(--error-text, #f87171);
  border: 1px solid rgba(239, 68, 68, 0.3);
}
.status-failed .status-dot {
  background: var(--error-text, #f87171);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.task-card-meta {
  display: flex;
  gap: 24px;
  margin-bottom: 14px;
}

.task-meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
}

.task-meta-item svg {
  width: 14px;
  height: 14px;
  color: var(--text-muted);
}

.task-card-progress {
  margin-bottom: 16px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.progress-label {
  font-size: 11px;
  color: var(--text-muted);
}

.progress-value {
  font-size: 12px;
  font-weight: 700;
}

.progress-value.high { color: #34d399; }
.progress-value.mid { color: #fbbf24; }
.progress-value.low { color: #f87171; }

.progress-bar {
  height: 5px;
  background: var(--border-color);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s ease;
}

.progress-fill.high { background: linear-gradient(90deg, #34d399, #10b981); }
.progress-fill.mid { background: linear-gradient(90deg, #fbbf24, #f59e0b); }
.progress-fill.low { background: linear-gradient(90deg, #f87171, #ef4444); }

.error-tip {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  margin-top: 8px;
  padding: 8px 10px;
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.35);
  border-radius: 8px;
  font-size: 11px;
  color: var(--error-text, #fca5a5);
  line-height: 1.45;
}

.error-tip svg {
  flex-shrink: 0;
  width: 14px;
  height: 14px;
  margin-top: 1px;
}

.error-tip-text {
  flex: 1;
  word-break: break-word;
}

.task-card-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding-top: 14px;
  border-top: 1px solid var(--border-color);
}

.task-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 7px 14px;
  font-size: 12px;
  font-weight: 600;
  background: var(--border-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.task-btn svg {
  width: 14px;
  height: 14px;
}

.task-btn:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.08);
}

.task-btn.btn-start:hover {
  color: #34d399;
  border-color: rgba(16, 185, 129, 0.3);
  background: rgba(16, 185, 129, 0.1);
}

.task-btn.btn-restart:hover {
  color: #60a5fa;
  border-color: rgba(59, 130, 246, 0.3);
  background: rgba(59, 130, 246, 0.1);
}

.task-btn.btn-stop:hover {
  color: #fbbf24;
  border-color: rgba(245, 158, 11, 0.3);
  background: rgba(245, 158, 11, 0.1);
}

.task-btn.btn-edit:hover {
  color: var(--active-color);
  border-color: rgba(var(--accent-rgb), 0.3);
  background: var(--active-bg);
}

.task-btn.btn-delete:hover {
  color: #f87171;
  border-color: rgba(239, 68, 68, 0.3);
  background: rgba(239, 68, 68, 0.1);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 32px;
}

.page-btn {
  width: 38px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.25s ease;
}

.page-btn:hover:not(:disabled) {
  color: var(--text-primary);
  border-color: rgba(255, 255, 255, 0.15);
}

.page-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-btn svg {
  width: 18px;
  height: 18px;
}

.page-info {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-left {
    flex-direction: column;
    align-items: stretch;
  }

  .search-input {
    width: 100%;
  }

  .task-card-top {
    flex-direction: column;
    gap: 10px;
  }

  .task-card-actions {
    flex-wrap: wrap;
  }
}

@media (max-width: 560px) {
  .tasks-content {
    padding: 24px 16px 64px;
  }

  .page-title {
    font-size: 22px;
  }

  .status-filter {
    overflow-x: auto;
  }
}
</style>