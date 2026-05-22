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
            <button class="btn-version" @click="$router.push(`/tasks/${task.id}/versions`)">
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
                <label class="form-label">Cron 表达式</label>
                <input v-model="form.cron" type="text" class="form-input" :disabled="!editing" placeholder="0 */6 * * *" />
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
            <button class="btn-clear-log" @click="logs = []">清空日志</button>
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
import NavBar from '../components/NavBar.vue'

const route = useRoute()
const activeTab = ref('info')
const editing = ref(false)
const autoScroll = ref(true)
const logViewerRef = ref(null)
let logTimer = null

const task = ref({
  id: route.params.id,
  name: '电商商品数据采集',
  url: 'https://example-shop.com/products',
  status: 'running',
  cron: '0 */6 * * *',
  concurrency: 5,
  interval: 2000,
  maxRetries: 3,
  headers: '{"User-Agent": "Mozilla/5.0", "Accept": "application/json"}'
})

const tabs = [
  { key: 'info', label: '基础信息' },
  { key: 'logs', label: '运行日志' },
  { key: 'records', label: '执行记录' },
  { key: 'preview', label: '数据预览' }
]

const statusLabelMap = { running: '运行中', pending: '待执行', completed: '已完成', failed: '失败' }
function statusLabel(status) { return statusLabelMap[status] || status }

const form = reactive({
  name: '',
  url: '',
  cron: '',
  concurrency: 0,
  interval: 0,
  maxRetries: 0,
  headers: ''
})

const formBackup = ref(null)

function loadForm() {
  form.name = task.value.name
  form.url = task.value.url
  form.cron = task.value.cron
  form.concurrency = task.value.concurrency
  form.interval = task.value.interval
  form.maxRetries = task.value.maxRetries
  form.headers = task.value.headers
  formBackup.value = { ...form }
}

function cancelEdit() {
  if (formBackup.value) {
    Object.assign(form, formBackup.value)
  }
  editing.value = false
}

function saveConfig() {
  task.value.name = form.name
  task.value.url = form.url
  task.value.cron = form.cron
  task.value.concurrency = form.concurrency
  task.value.interval = form.interval
  task.value.maxRetries = form.maxRetries
  task.value.headers = form.headers
  editing.value = false
}

const executionRecords = ref([
  { id: 1, version: 3, status: 'completed', duration: '2h 15m', dataCount: 4820, time: '2026-05-21 14:30' },
  { id: 2, version: 2, status: 'completed', duration: '2h 08m', dataCount: 4570, time: '2026-05-20 08:15' },
  { id: 3, version: 1, status: 'failed', duration: '0h 45m', dataCount: 320, time: '2026-05-19 16:00' },
  { id: 4, version: 1, status: 'completed', duration: '2h 30m', dataCount: 5100, time: '2026-05-18 06:00' }
])

const logTemplates = [
  { type: 'info', level: 'INFO', msg: '任务初始化完成，开始执行数据采集...' },
  { type: 'info', level: 'INFO', msg: '正在连接目标站点: {url}' },
  { type: 'info', level: 'INFO', msg: '连接成功，开始解析页面结构...' },
  { type: 'info', level: 'INFO', msg: '发现 <span class="kw">128</span> 条目标数据记录' },
  { type: 'info', level: 'INFO', msg: '分页处理: 第 <span class="kw">1</span> 页, 已采集 <span class="kw">50</span> 条' },
  { type: 'info', level: 'INFO', msg: '分页处理: 第 <span class="kw">2</span> 页, 已采集 <span class="kw">100</span> 条' },
  { type: 'warn', level: 'WARN', msg: '请求延迟较高: <span class="kw">3.2s</span>, 当前重试第 <span class="kw">1</span> 次' },
  { type: 'info', level: 'INFO', msg: '分页处理: 第 <span class="kw">3</span> 页, 已采集 <span class="kw">128</span> 条' },
  { type: 'error', level: 'ERROR', msg: '解析页面 <span class="kw">#product-list</span> 时出现异常: <span class="err">Element not found</span>' },
  { type: 'warn', level: 'WARN', msg: '触发反爬检测，切换代理 IP: <span class="kw">192.168.1.100</span>' },
  { type: 'info', level: 'INFO', msg: '数据清洗完成，有效记录: <span class="kw">4820</span> 条' },
  { type: 'info', level: 'INFO', msg: '数据已写入数据库，本次任务执行完毕' }
]

const logs = ref([])

function generateLogs() {
  if (activeTab.value !== 'logs') return
  const tmpl = logTemplates[Math.floor(Math.random() * logTemplates.length)]
  const now = new Date()
  const time = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`
  logs.value.push({
    time,
    type: tmpl.type,
    level: tmpl.level,
    message: tmpl.msg
  })
  if (logs.value.length > 200) {
    logs.value = logs.value.slice(-200)
  }
  if (autoScroll.value) {
    nextTick(() => {
      if (logViewerRef.value) {
        logViewerRef.value.scrollTop = logViewerRef.value.scrollHeight
      }
    })
  }
}

onMounted(() => {
  loadForm()
  logTimer = setInterval(generateLogs, 1500)
})

onBeforeUnmount(() => {
  if (logTimer) clearInterval(logTimer)
})

watch(activeTab, (val) => {
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