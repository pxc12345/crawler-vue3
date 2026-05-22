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
          @click="$router.push(`/tasks/${task.id}`)"
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
            <div class="task-meta-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
              <span>{{ task.executionTime }}</span>
            </div>
            <div class="task-meta-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 20V10"/>
                <path d="M12 20V4"/>
                <path d="M6 20v-6"/>
              </svg>
              <span>{{ task.dataCount }} 条数据</span>
            </div>
          </div>

          <div class="task-card-progress">
            <div class="progress-header">
              <span class="progress-label">成功率</span>
              <span class="progress-value" :class="task.successRate >= 90 ? 'high' : task.successRate >= 60 ? 'mid' : 'low'">{{ task.successRate }}%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" :class="task.successRate >= 90 ? 'high' : task.successRate >= 60 ? 'mid' : 'low'" :style="{ width: task.successRate + '%' }"></div>
            </div>
          </div>

          <div class="task-card-actions" @click.stop>
            <button
              class="task-btn"
              :class="task.status === 'running' ? 'btn-stop' : 'btn-start'"
              @click="toggleTaskStatus(task)"
            >
              <svg v-if="task.status === 'running'" viewBox="0 0 24 24" fill="currentColor" stroke="none">
                <rect x="6" y="4" width="4" height="16"/>
                <rect x="14" y="4" width="4" height="16"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="currentColor" stroke="none">
                <polygon points="5 3 19 12 5 21 5 3"/>
              </svg>
              {{ task.status === 'running' ? '停止' : '启动' }}
            </button>
            <button class="task-btn btn-edit" @click="$router.push(`/tasks/${task.id}`)">
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
import { ref, computed, onMounted } from 'vue'
import NavBar from '../components/NavBar.vue'

const loading = ref(true)
const tasks = ref([])
const searchKeyword = ref('')
const activeStatus = ref('all')
const currentPage = ref(1)
const pageSize = 10

const statusOptions = [
  { label: '全部', value: 'all' },
  { label: '运行中', value: 'running' },
  { label: '待执行', value: 'pending' },
  { label: '已完成', value: 'completed' },
  { label: '失败', value: 'failed' }
]

const statusLabelMap = { running: '运行中', pending: '待执行', completed: '已完成', failed: '失败' }
function statusLabel(status) { return statusLabelMap[status] || status }

const filteredTasks = computed(() => {
  let result = tasks.value
  if (activeStatus.value !== 'all') {
    result = result.filter(t => t.status === activeStatus.value)
  }
  if (searchKeyword.value.trim()) {
    const kw = searchKeyword.value.toLowerCase()
    result = result.filter(t => t.name.toLowerCase().includes(kw) || t.url.toLowerCase().includes(kw))
  }
  return result
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredTasks.value.length / pageSize)))

const paginatedTasks = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredTasks.value.slice(start, start + pageSize)
})

function toggleFavorite(task) {
  task.favorite = !task.favorite
}

function toggleTaskStatus(task) {
  if (task.status === 'running') {
    task.status = 'pending'
  } else {
    task.status = 'running'
  }
}

function deleteTask(task) {
  const confirmed = window.confirm(`确定要删除任务「${task.name}」吗？此操作不可撤销。`)
  if (confirmed) {
    tasks.value = tasks.value.filter(t => t.id !== task.id)
  }
}

async function fetchTasks() {
  loading.value = true
  await new Promise(r => setTimeout(r, 600))
  tasks.value = [
    { id: 1, name: '电商商品数据采集', url: 'https://example-shop.com/products', status: 'running', executionTime: '2h 15m', dataCount: 4820, successRate: 98.5, favorite: true },
    { id: 2, name: '新闻资讯爬取', url: 'https://news-portal.com/latest', status: 'pending', executionTime: '0h 0m', dataCount: 0, successRate: 0, favorite: false },
    { id: 3, name: '社交媒体评论采集', url: 'https://social-media.com/posts', status: 'running', executionTime: '1h 08m', dataCount: 2150, successRate: 87.3, favorite: true },
    { id: 4, name: '房价数据监控', url: 'https://housing-data.com/listings', status: 'completed', executionTime: '4h 32m', dataCount: 12350, successRate: 99.1, favorite: false },
    { id: 5, name: '竞品价格追踪', url: 'https://competitor-prices.com/catalog', status: 'failed', executionTime: '0h 45m', dataCount: 320, successRate: 28.6, favorite: false },
    { id: 6, name: '天气数据采集', url: 'https://weather-api.com/forecast', status: 'completed', executionTime: '0h 18m', dataCount: 9600, successRate: 100, favorite: true },
    { id: 7, name: '论文摘要爬取', url: 'https://academic-db.com/papers', status: 'pending', executionTime: '0h 0m', dataCount: 0, successRate: 0, favorite: false },
    { id: 8, name: '招聘信息汇总', url: 'https://jobs-board.com/listings', status: 'running', executionTime: '3h 05m', dataCount: 3400, successRate: 92.7, favorite: false },
    { id: 9, name: '金融数据采集', url: 'https://finance-data.com/markets', status: 'failed', executionTime: '1h 20m', dataCount: 150, successRate: 15.2, favorite: false },
    { id: 10, name: '视频元数据采集', url: 'https://video-platform.com/api', status: 'completed', executionTime: '2h 50m', dataCount: 7800, successRate: 96.8, favorite: true },
    { id: 11, name: '商品评论爬取', url: 'https://review-site.com/products', status: 'pending', executionTime: '0h 0m', dataCount: 0, successRate: 0, favorite: false },
    { id: 12, name: '地图POI数据', url: 'https://map-service.com/poi', status: 'running', executionTime: '5h 12m', dataCount: 25600, successRate: 94.3, favorite: false }
  ]
  loading.value = false
}

onMounted(() => {
  fetchTasks()
})
</script>

<style scoped>
.tasks-page {
  min-height: 100vh;
  background-color: #0d1117;
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
  color: rgba(255, 255, 255, 0.9);
  letter-spacing: -0.5px;
}

.task-count {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.35);
  font-weight: 500;
}

.btn-create {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 22px;
  background: linear-gradient(135deg, #4c6ef5, #7c3aed);
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 4px 16px rgba(76, 110, 245, 0.3);
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
  background: rgba(22, 27, 34, 0.6);
  border-radius: 10px;
  padding: 4px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.status-btn {
  padding: 7px 15px;
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.45);
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.status-btn:hover {
  color: rgba(255, 255, 255, 0.75);
  background: rgba(255, 255, 255, 0.04);
}

.status-btn.active {
  color: #7c8aff;
  background: rgba(76, 110, 245, 0.15);
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
  color: rgba(255, 255, 255, 0.25);
  pointer-events: none;
}

.search-input {
  width: 240px;
  padding: 10px 14px 10px 40px;
  font-size: 13px;
  background: rgba(22, 27, 34, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.85);
  outline: none;
  transition: all 0.25s ease;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.2);
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
  background: rgba(22, 27, 34, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.45);
  cursor: pointer;
  transition: all 0.25s ease;
}

.btn-refresh:hover {
  color: rgba(255, 255, 255, 0.85);
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
  background: rgba(22, 27, 34, 0.5);
  border-radius: 16px;
  padding: 28px;
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.skeleton-line {
  height: 14px;
  background: rgba(255, 255, 255, 0.04);
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
  background: rgba(255, 255, 255, 0.03);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.1);
}

.empty-icon svg {
  width: 36px;
  height: 36px;
}

.empty-text {
  font-size: 18px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.35);
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.2);
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-card {
  background: rgba(22, 27, 34, 0.55);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 22px 26px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.task-card:hover {
  background: rgba(22, 27, 34, 0.8);
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
  color: rgba(255, 255, 255, 0.2);
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
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 4px;
  letter-spacing: -0.2px;
}

.task-url {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.3);
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
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.4);
}
.status-completed .status-dot {
  background: rgba(255, 255, 255, 0.35);
}

.status-failed {
  background: rgba(239, 68, 68, 0.12);
  color: #f87171;
}
.status-failed .status-dot {
  background: #f87171;
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
  color: rgba(255, 255, 255, 0.35);
}

.task-meta-item svg {
  width: 14px;
  height: 14px;
  color: rgba(255, 255, 255, 0.2);
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
  color: rgba(255, 255, 255, 0.3);
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
  background: rgba(255, 255, 255, 0.06);
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

.task-card-actions {
  display: flex;
  gap: 8px;
  padding-top: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.task-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 7px 14px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.2s ease;
}

.task-btn svg {
  width: 14px;
  height: 14px;
}

.task-btn:hover {
  color: rgba(255, 255, 255, 0.85);
  background: rgba(255, 255, 255, 0.08);
}

.task-btn.btn-start:hover {
  color: #34d399;
  border-color: rgba(16, 185, 129, 0.3);
  background: rgba(16, 185, 129, 0.1);
}

.task-btn.btn-stop:hover {
  color: #fbbf24;
  border-color: rgba(245, 158, 11, 0.3);
  background: rgba(245, 158, 11, 0.1);
}

.task-btn.btn-edit:hover {
  color: #7c8aff;
  border-color: rgba(76, 110, 245, 0.3);
  background: rgba(76, 110, 245, 0.1);
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
  background: rgba(22, 27, 34, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.25s ease;
}

.page-btn:hover:not(:disabled) {
  color: rgba(255, 255, 255, 0.85);
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
  color: rgba(255, 255, 255, 0.4);
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