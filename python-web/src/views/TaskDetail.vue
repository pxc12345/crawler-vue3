<template>
  <div class="task-detail-page">
    <NavBar />
    <div class="detail-content">
      <div class="detail-header">
        <button class="btn-back" @click="$router.back()">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
        </button>
        <div class="header-info">
          <h1 class="detail-title">{{ task.name }}</h1>
          <div class="header-meta">
            <span class="task-status-tag" :class="'status-' + task.status">
              <span class="status-dot"></span>
              {{ statusLabel(task.status) }}
            </span>
            <button class="btn-version" @click="task.id && $router.push(`/tasks/${task.id}/versions`)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="6" y1="3" x2="6" y2="15"/>
                <circle cx="18" cy="6" r="3"/>
                <circle cx="6" cy="18" r="3"/>
                <path d="M18 9a9 9 0 0 1-9 9"/>
              </svg>
              版本历史
            </button>
          </div>
        </div>
      </div>

      <div class="tab-nav">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >{{ tab.label }}</button>
      </div>

      <div class="tab-content">
        <div v-if="activeTab === 'info'" class="tab-panel info-panel">
          <div class="config-form">
            <div class="form-row">
              <div class="form-group full">
                <label class="form-label">任务名称</label>
                <input v-model="form.name" type="text" class="form-input" :disabled="!editing" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group full">
                <label class="form-label">目标 URL</label>
                <input v-model="form.url" type="text" class="form-input" :disabled="!editing" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">执行周期（分钟）</label>
                <input v-model.number="form.intervalMinutes" type="number" class="form-input" :disabled="!editing" placeholder="例如：30" min="1" />
              </div>
              <div class="form-group">
                <label class="form-label">并发数</label>
                <input v-model="form.concurrency" type="number" class="form-input" :disabled="!editing" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">请求间隔 (ms)</label>
                <input v-model="form.interval" type="number" class="form-input" :disabled="!editing" />
              </div>
              <div class="form-group">
                <label class="form-label">最大重试次数</label>
                <input v-model="form.maxRetries" type="number" class="form-input" :disabled="!editing" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group full">
                <label class="form-label">请求头 (JSON)</label>
                <textarea v-model="form.headers" class="form-textarea" :disabled="!editing" rows="3"></textarea>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <template v-if="!editing">
              <button class="action-btn primary" @click="editing = true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
                编辑
              </button>
            </template>
            <template v-else>
              <button class="action-btn success" @click="saveConfig">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                保存
              </button>
              <button class="action-btn cancel" @click="cancelEdit">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
                取消
              </button>
            </template>
          </div>
        </div>

        <div v-if="activeTab === 'logs'" class="tab-panel logs-panel">
          <div class="log-controls">
            <div class="log-control-left">
              <label class="auto-scroll-label">
                <input type="checkbox" v-model="autoScroll" />
                <span>自动滚动</span>
              </label>
            </div>
            <div class="log-control-right">
              <button class="btn-refresh-log" @click="refreshLogs" :disabled="logsLoading">
                {{ logsLoading ? '加载中...' : '刷新日志' }}
              </button>
              <button class="btn-clear-log" @click="logs = []">清空日志</button>
            </div>
          </div>
          <div class="log-viewer" ref="logViewerRef">
            <div v-for="(line, idx) in logs" :key="idx" class="log-line" :class="line.type">
              <span class="log-time">{{ line.time }}</span>
              <span class="log-level" :class="line.type">{{ line.level }}</span>
              <span class="log-msg" v-html="line.message"></span>
            </div>
            <div v-if="logs.length === 0" class="log-empty">暂无日志输出</div>
          </div>
        </div>

        <div v-if="activeTab === 'records'" class="tab-panel records-panel">
          <div class="timeline">
            <div v-for="record in executionRecords" :key="record.id" class="timeline-item">
              <div class="timeline-dot" :class="'dot-' + record.status"></div>
              <div class="timeline-card">
                <div class="timeline-card-top">
                  <span class="record-version">v{{ record.version }}</span>
                  <span class="record-status" :class="'status-' + record.status">{{ statusLabel(record.status) }}</span>
                </div>
                <div class="timeline-card-meta">
                  <span>持续时间: {{ record.duration }}</span>
                  <span>采集数据: {{ record.dataCount }} 条</span>
                </div>
                <div class="timeline-card-time">{{ record.time }}</div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'preview'" class="tab-panel preview-panel">
          <div class="preview-placeholder">
            <div class="preview-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                <line x1="8" y1="21" x2="16" y2="21"/>
                <line x1="12" y1="17" x2="12" y2="21"/>
              </svg>
            </div>
            <p class="preview-text">查看数据预览请前往</p>
            <button class="action-btn primary" @click="$router.push('/data-preview')">
              数据预览页面
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import NavBar from '../components/NavBar.vue'
import { taskAPI } from '../api/task'
import { systemAPI } from '../api/system'

const route = useRoute()
const activeTab = ref('info')
const editing = ref(false)
const autoScroll = ref(true)
const logViewerRef = ref(null)

const task = ref({})

const tabs = [
  { key: 'info', label: '基础信息' },
  { key: 'logs', label: '运行日志' },
  { key: 'records', label: '执行记录' },
  { key: 'preview', label: '数据预览' }
]

const statusLabelMap = { running: '运行中', pending: '待执行', completed: '已完成', failed: '失败' }
function statusLabel(status) { return statusLabelMap[status] || status }

function minutesToCron(minutes) {
  if (!minutes || minutes < 1) return '*/30 * * * *'
  return `*/${minutes} * * * *`
}

function cronToMinutes(cron) {
  if (!cron) return 30
  const match = cron.match(/^\*\/(\d+)\s+\*\s+\*\s+\*\s+\*$/)
  if (match) return parseInt(match[1]) || 30
  return 30
}

const form = reactive({
  name: '',
  url: '',
  intervalMinutes: 30,
  concurrency: 0,
  interval: 0,
  maxRetries: 0,
  headers: ''
})

const formBackup = ref(null)

function loadForm() {
  const t = task.value
  const config = t.config || {}
  if (typeof config === 'string') {
    try { config = JSON.parse(config) } catch (e) { config = {} }
  }
  form.name = t.name || ''
  form.url = t.target_url || config.target_url || ''
  form.intervalMinutes = cronToMinutes(t.cron_expr || config.cron)
  form.concurrency = t.concurrency || config.concurrency || 0
  form.interval = t.interval_seconds || config.interval_seconds || config.interval || 0
  form.maxRetries = t.retry_count || config.maxRetries || 0
  form.headers = typeof config.headers === 'object' ? JSON.stringify(config.headers) : (config.headers || '')
  formBackup.value = { ...form }
}

function cancelEdit() {
  if (formBackup.value) {
    Object.assign(form, formBackup.value)
  }
  editing.value = false
}

async function saveConfig() {
  try {
    const config = {
      target_url: form.url,
      cron_expr: minutesToCron(form.intervalMinutes),
      concurrency: form.concurrency,
      interval_seconds: form.interval,
      maxRetries: form.maxRetries,
      headers: form.headers
    }
    const res = await taskAPI.updateTask(task.value.id, {
      name: form.name,
      config: config
    })
    if (res.data.success) {
      task.value.name = form.name
      task.value.target_url = form.url
      task.value.cron_expr = minutesToCron(form.intervalMinutes)
      task.value.concurrency = form.concurrency
      task.value.interval_seconds = form.interval
      task.value.retry_count = form.maxRetries
      task.value.config = config
      editing.value = false
      ElMessage.success('保存成功')
    } else {
      ElMessage.error(res.data.message || '保存失败')
    }
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const executionRecords = ref([])
const logs = ref([])
const logsLoading = ref(false)

async function fetchTask() {
  // 跳过无效的 task id
  if (!route.params.id || route.params.id === 'new' || route.params.id === 'undefined') {
    return
  }
  try {
    const res = await taskAPI.getTask(route.params.id)
    if (res.data.success) {
      task.value = res.data.data
      loadForm()
    }
  } catch (e) {
    console.error('获取任务详情失败:', e)
  }
}

async function fetchVersions() {
  // 跳过无效的 task id
  if (!route.params.id || route.params.id === 'new' || route.params.id === 'undefined') {
    return
  }
  try {
    const res = await taskAPI.getVersions(route.params.id)
    if (res.data.success) {
      const versions = res.data.data || []
      executionRecords.value = versions.map((v, index) => ({
        id: v.id,
        version: v.version_index || (versions.length - index),
        status: 'completed',
        duration: 'N/A',
        dataCount: 0,
        time: v.created_at || '',
        changeLog: v.change_log || ''
      }))
    }
  } catch (e) {
    console.error('获取版本列表失败:', e)
  }
}

async function refreshLogs() {
  logsLoading.value = true
  try {
    const res = await systemAPI.getLogs({ source: 'crawler_task', limit: 200, page_size: 200 })
    if (res.data.success) {
      const logList = res.data.data?.list || []
      logs.value = logList.map(item => ({
        time: item.created_at ? item.created_at.split(' ')[1] || item.created_at : '',
        type: item.level ? item.level.toLowerCase() : 'info',
        level: item.level || 'INFO',
        message: item.message || ''
      }))
    }
  } catch (e) {
    console.error('获取日志失败:', e)
  } finally {
    logsLoading.value = false
  }
}

onMounted(() => {
  fetchTask()
})

watch(activeTab, (val) => {
  if (val === 'records') {
    fetchVersions()
  }
  if (val === 'logs' && autoScroll.value) {
    nextTick(() => {
      if (logViewerRef.value) {
        logViewerRef.value.scrollTop = logViewerRef.value.scrollHeight
      }
    })
  }
})
</script>

<style scoped>
.task-detail-page {
  min-height: 100vh;
  background-color: #0d1117;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.018) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.018) 1px, transparent 1px);
  background-size: 40px 40px;
}

.task-detail-page::before {
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

.detail-content {
  max-width: 960px;
  margin: 0 auto;
  padding: 40px 24px 80px;
  position: relative;
  z-index: 1;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 28px;
}

.btn-back {
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(22, 27, 34, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.25s ease;
  flex-shrink: 0;
}

.btn-back:hover {
  color: rgba(255, 255, 255, 0.85);
  border-color: rgba(255, 255, 255, 0.15);
}

.btn-back svg {
  width: 20px;
  height: 20px;
}

.header-info {
  flex: 1;
  min-width: 0;
}

.detail-title {
  font-size: 24px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 8px;
  letter-spacing: -0.4px;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.task-status-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
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

.status-pending { background: rgba(76, 110, 245, 0.12); color: #7c8aff; }
.status-pending .status-dot { background: #7c8aff; }
.status-completed { background: rgba(255, 255, 255, 0.05); color: rgba(255, 255, 255, 0.4); }
.status-completed .status-dot { background: rgba(255, 255, 255, 0.35); }
.status-failed { background: rgba(239, 68, 68, 0.12); color: #f87171; }
.status-failed .status-dot { background: #f87171; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.btn-version {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.45);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-version:hover {
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.15);
}

.btn-version svg {
  width: 14px;
  height: 14px;
}

.tab-nav {
  display: flex;
  gap: 4px;
  background: rgba(22, 27, 34, 0.5);
  border-radius: 12px;
  padding: 5px;
  margin-bottom: 24px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.tab-btn {
  flex: 1;
  padding: 11px 20px;
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.4);
  background: transparent;
  border: none;
  border-radius: 9px;
  cursor: pointer;
  transition: all 0.25s ease;
}

.tab-btn:hover {
  color: rgba(255, 255, 255, 0.7);
}

.tab-btn.active {
  background: rgba(76, 110, 245, 0.15);
  color: #7c8aff;
  font-weight: 600;
}

.tab-panel {
  background: rgba(22, 27, 34, 0.55);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 28px;
}

.config-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group.full {
  grid-column: 1 / -1;
}

.form-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.4);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-input {
  width: 100%;
  padding: 11px 16px;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.85);
  outline: none;
  transition: all 0.25s ease;
}

.form-input:focus {
  border-color: rgba(76, 110, 245, 0.4);
  box-shadow: 0 0 0 3px rgba(76, 110, 245, 0.08);
}

.form-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-textarea {
  width: 100%;
  padding: 11px 16px;
  font-size: 13px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.85);
  outline: none;
  resize: vertical;
  transition: all 0.25s ease;
}

.form-textarea:focus {
  border-color: rgba(76, 110, 245, 0.4);
}

.form-textarea:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 11px 22px;
  font-size: 13px;
  font-weight: 600;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.25s ease;
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.6);
}

.action-btn svg { width: 16px; height: 16px; }

.action-btn.primary {
  background: linear-gradient(135deg, #4c6ef5, #7c3aed);
  color: #fff;
  border: none;
  box-shadow: 0 4px 14px rgba(76, 110, 245, 0.3);
}

.action-btn.primary:hover { box-shadow: 0 6px 20px rgba(76, 110, 245, 0.45); transform: translateY(-1px); }

.action-btn.success {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border-color: rgba(16, 185, 129, 0.2);
}

.action-btn.success:hover { background: rgba(16, 185, 129, 0.22); }

.action-btn.cancel {
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.5);
}

.action-btn.cancel:hover { background: rgba(255, 255, 255, 0.08); color: rgba(255, 255, 255, 0.75); }

.log-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 14px;
  margin-bottom: 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.auto-scroll-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
}

.auto-scroll-label input {
  accent-color: #4c6ef5;
}

.btn-clear-log {
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 500;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.15);
  border-radius: 8px;
  color: #f87171;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-clear-log:hover {
  background: rgba(239, 68, 68, 0.15);
}

.log-viewer {
  height: 480px;
  overflow-y: auto;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 12px;
  line-height: 1.8;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  padding: 16px;
}

.log-viewer::-webkit-scrollbar { width: 6px; }
.log-viewer::-webkit-scrollbar-track { background: transparent; }
.log-viewer::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.08); border-radius: 3px; }

.log-line {
  display: flex;
  gap: 10px;
}

.log-time {
  color: rgba(255, 255, 255, 0.2);
  flex-shrink: 0;
}

.log-level {
  width: 50px;
  flex-shrink: 0;
  font-weight: 600;
}

.log-level.info { color: #7c8aff; }
.log-level.warn { color: #fbbf24; }
.log-level.error { color: #f87171; }

.log-msg { color: rgba(255, 255, 255, 0.55); }

.log-msg :deep(.kw) { color: #7c8aff; }
.log-msg :deep(.err) { color: #f87171; }

.log-line.error .log-msg { color: #f87171; }
.log-line.warn .log-msg { color: #fbbf24; }

.log-empty {
  text-align: center;
  color: rgba(255, 255, 255, 0.15);
  padding: 60px 0;
  font-size: 13px;
}

.timeline {
  position: relative;
  padding-left: 32px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 11px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: rgba(255, 255, 255, 0.06);
}

.timeline-item {
  position: relative;
  margin-bottom: 24px;
}

.timeline-item:last-child { margin-bottom: 0; }

.timeline-dot {
  position: absolute;
  left: -26px;
  top: 16px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.1);
  background: #0d1117;
}

.timeline-dot.dot-completed {
  border-color: #34d399;
  background: #34d399;
  box-shadow: 0 0 8px rgba(52, 211, 153, 0.4);
}

.timeline-dot.dot-failed {
  border-color: #f87171;
  background: #f87171;
  box-shadow: 0 0 8px rgba(248, 113, 113, 0.4);
}

.timeline-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 16px 20px;
}

.timeline-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.record-version {
  font-size: 13px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.7);
}

.record-status {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 10px;
}

.record-status.status-completed { background: rgba(16, 185, 129, 0.12); color: #34d399; }
.record-status.status-failed { background: rgba(239, 68, 68, 0.12); color: #f87171; }

.timeline-card-meta {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.3);
  margin-bottom: 6px;
}

.timeline-card-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.2);
}

.preview-panel {
  text-align: center;
  padding: 60px 20px;
}

.preview-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.preview-icon {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.03);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.15);
}

.preview-icon svg { width: 32px; height: 32px; }

.preview-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.3);
}

@media (max-width: 768px) {
  .detail-content { padding: 24px 16px 64px; }
  .detail-title { font-size: 20px; }
  .form-row { grid-template-columns: 1fr; }
  .tab-nav { overflow-x: auto; }
  .tab-btn { flex: none; }
}
</style>