<template>
  <div class="page">
    <NavBar />
    <div class="content">
      <div class="page-header">
        <h1 class="page-title">系统日志</h1>
        <div class="header-actions">
          <button class="btn-action" @click="refreshLogs">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
            刷新
          </button>
          <button class="btn-action" @click="confirmClear">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            清空
          </button>
          <button class="btn-action" @click="exportLogs">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            导出
          </button>
        </div>
      </div>

      <div class="stats-row">
        <div class="card stat-card">
          <span class="stat-num">{{ allLogs.length }}</span>
          <span class="stat-label">日志总数</span>
        </div>
        <div class="card stat-card">
          <span class="stat-num">{{ todayLogs.length }}</span>
          <span class="stat-label">今日日志</span>
        </div>
        <div class="card stat-card error-stat">
          <span class="stat-num error-color">{{ todayErrors }}</span>
          <span class="stat-label">今日错误</span>
        </div>
      </div>

      <div class="card filter-card">
        <div class="filter-row">
          <div class="level-filter">
            <button
              v-for="l in levels"
              :key="l.value"
              class="level-btn"
              :class="{ active: activeLevel === l.value }"
              @click="activeLevel = l.value; currentPage = 1"
            >{{ l.label }}</button>
          </div>
          <div class="filter-group">
            <input v-model="logSearch" placeholder="搜索日志关键字..." class="input" @input="currentPage=1" />
          </div>
          <div class="filter-group">
            <input type="date" v-model="logDateFrom" class="input input-date" @change="currentPage=1" />
            <span class="date-sep">至</span>
            <input type="date" v-model="logDateTo" class="input input-date" @change="currentPage=1" />
          </div>
        </div>
      </div>

      <div class="card terminal-card">
        <div class="terminal-header">
          <div class="terminal-dots">
            <span class="dot dot-red"></span>
            <span class="dot dot-yellow"></span>
            <span class="dot dot-green"></span>
          </div>
          <span class="terminal-title">crawlmaster@system:~$ tail -f logs</span>
        </div>
        <div class="terminal-body" ref="terminalBody">
          <div v-if="filteredLogs.length === 0" class="terminal-empty">暂无日志记录</div>
          <div
            v-for="log in paginatedLogs"
            :key="log.id"
            class="log-line"
            :class="'level-' + log.level"
          >
            <span class="log-time">{{ log.time }}</span>
            <span class="log-level-tag" :class="'tag-' + log.level">{{ levelLabel(log.level) }}</span>
            <span class="log-source">{{ log.source }}</span>
            <span class="log-msg">{{ log.message }}</span>
          </div>
        </div>
      </div>

      <div v-if="filteredLogs.length > 0" class="pagination-wrap">
        <button class="page-btn" :disabled="currentPage <= 1" @click="currentPage--">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
        </button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <button class="page-btn" :disabled="currentPage >= totalPages" @click="currentPage++">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { systemAPI } from '../api/system'
import NavBar from '../components/NavBar.vue'

const activeLevel = ref('ALL')
const logSearch = ref('')
const logDateFrom = ref('')
const logDateTo = ref('')
const currentPage = ref(1)
const pageSize = 15
const terminalBody = ref(null)

const levels = [
  { label: 'ALL', value: 'ALL' },
  { label: 'INFO', value: 'INFO' },
  { label: 'WARNING', value: 'WARNING' },
  { label: 'ERROR', value: 'ERROR' }
]

const allLogs = ref([])

function levelLabel(level) {
  const map = { INFO: '信息', WARNING: '警告', ERROR: '错误' }
  return map[level] || level
}

const filteredLogs = computed(() => {
  let result = [...allLogs.value]
  if (activeLevel.value !== 'ALL') {
    result = result.filter(l => l.level === activeLevel.value)
  }
  if (logSearch.value) {
    const kw = logSearch.value.toLowerCase()
    result = result.filter(l => (l.message || '').toLowerCase().includes(kw) || (l.source || '').toLowerCase().includes(kw))
  }
  if (logDateFrom.value) {
    result = result.filter(l => l.time && l.time.startsWith(logDateFrom.value))
  }
  if (logDateTo.value) {
    result = result.filter(l => l.time && (l.time.startsWith(logDateTo.value) || l.time < logDateTo.value + ' 23:59:59'))
  }
  return result
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredLogs.value.length / pageSize)))

const paginatedLogs = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredLogs.value.slice(start, start + pageSize)
})

const todayLogs = computed(() => {
  const today = new Date().toISOString().slice(0, 10)
  return allLogs.value.filter(l => l.time && l.time.startsWith(today))
})

const todayErrors = computed(() => {
  const today = new Date().toISOString().slice(0, 10)
  return allLogs.value.filter(l => l.level === 'ERROR' && l.time && l.time.startsWith(today)).length
})

function confirmClear() {
  ElMessageBox.confirm('确定要清空所有日志吗？此操作不可恢复。', '确认操作', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await systemAPI.clearLogs(0)
      allLogs.value = []
      ElMessage.success('日志已清空')
    } catch (error) {
      ElMessage.error('清空日志失败')
    }
  }).catch(() => {})
}

async function refreshLogs() {
  await fetchLogs()
  ElMessage.success('日志已刷新')
}

async function exportLogs() {
  try {
    const { downloadFile } = await import('../api/index')
    await downloadFile('/system/logs/export', 'system_logs.csv', 'csv')
    ElMessage.success('日志导出成功')
  } catch (error) {
    ElMessage.error('日志导出失败')
  }
}

async function fetchLogs() {
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize
    }
    if (activeLevel.value !== 'ALL') params.level = activeLevel.value
    if (logSearch.value) params.keyword = logSearch.value
    const res = await systemAPI.getLogs(params)
    if (res.data.success) {
      allLogs.value = (res.data.data.list || res.data.data || []).map((l, i) => ({ ...l, id: l.id || i + 1 }))
    }
  } catch (error) {
    ElMessage.error('获取日志失败')
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (terminalBody.value) {
      terminalBody.value.scrollTop = terminalBody.value.scrollHeight
    }
  })
}

watch(currentPage, () => {
  nextTick(() => {
    if (terminalBody.value) terminalBody.value.scrollTop = 0
  })
})

onMounted(() => {
  fetchLogs().then(() => scrollToBottom())
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background-color: var(--bg-primary);
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.018) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.018) 1px, transparent 1px);
  background-size: 40px 40px;
}
.page::before {
  content: '';
  position: fixed; top: 0; left: 0;
  width: 100%; height: 100%;
  background:
    radial-gradient(ellipse 80% 60% at 50% -20%, rgba(var(--accent-rgb), 0.06), transparent),
    radial-gradient(ellipse 60% 40% at 80% 80%, var(--glow-color), transparent);
  pointer-events: none; z-index: 0;
}
.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px 80px;
  position: relative; z-index: 1;
}
.page-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 28px;
}
.page-title {
  font-size: 26px; font-weight: 700;
  color: var(--text-primary); letter-spacing: -0.5px;
}
.header-actions { display: flex; gap: 8px; }
.btn-action {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 8px 14px; font-size: 12px; font-weight: 500;
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border-color);
  border-radius: 8px; color: var(--text-secondary);
  cursor: pointer; transition: all 0.2s ease;
}
.btn-action:hover { background: rgba(255,255,255,0.08); color: var(--text-primary); }
.btn-action svg { width: 14px; height: 14px; }
.stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px; }
.card {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
}
.stat-card { padding: 20px; text-align: center; }
.stat-num { display: block; font-size: 28px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
.stat-label { font-size: 12px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.3px; }
.error-color { color: #f87171; }
.filter-card { padding: 16px 20px; margin-bottom: 20px; }
.filter-row { display: flex; gap: 14px; align-items: center; flex-wrap: wrap; }
.level-filter { display: flex; gap: 4px; background: rgba(0,0,0,0.2); border-radius: 8px; padding: 3px; }
.level-btn {
  padding: 6px 13px; font-size: 11px; font-weight: 600;
  color: rgba(255,255,255,0.35); background: transparent; border: none;
  border-radius: 6px; cursor: pointer; transition: all 0.15s ease;
}
.level-btn:hover { color: rgba(255,255,255,0.65); }
.level-btn.active { background: rgba(76,110,245,0.15); color: #7c8aff; }
.filter-group { display: flex; align-items: center; gap: 6px; }
.input {
  padding: 7px 12px; font-size: 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-color);
  border-radius: 7px; color: var(--text-primary);
  outline: none; transition: all 0.2s ease;
}
.input:focus { border-color: rgba(var(--accent-rgb), 0.4); }
.input-date { color-scheme: dark; width: 130px; }
.date-sep { font-size: 11px; color: var(--text-muted); }
.terminal-card { overflow: hidden; margin-bottom: 20px; }
.terminal-header {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 16px; background: rgba(0,0,0,0.3);
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.terminal-dots { display: flex; gap: 6px; }
.dot { width: 10px; height: 10px; border-radius: 50%; }
.dot-red { background: #f87171; }
.dot-yellow { background: #fbbf24; }
.dot-green { background: #34d399; }
.terminal-title { font-size: 11px; color: var(--text-muted); font-family: monospace; }
.terminal-body {
  padding: 16px; max-height: 520px; overflow-y: auto;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 12px; line-height: 1.8;
}
.terminal-body::-webkit-scrollbar { width: 6px; }
.terminal-body::-webkit-scrollbar-track { background: transparent; }
.terminal-body::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 3px; }
.terminal-empty { color: rgba(255,255,255,0.15); padding: 40px; text-align: center; }
.log-line { display: flex; gap: 12px; align-items: baseline; padding: 3px 0; }
.log-time { color: rgba(255,255,255,0.2); white-space: nowrap; min-width: 130px; }
.log-level-tag {
  display: inline-block; padding: 0 6px; border-radius: 3px;
  font-size: 10px; font-weight: 700; min-width: 48px; text-align: center;
}
.tag-INFO { background: rgba(76,110,245,0.15); color: #7c8aff; }
.tag-WARNING { background: rgba(251,191,36,0.15); color: #fbbf24; }
.tag-ERROR { background: rgba(248,113,113,0.15); color: #f87171; }
.log-source { color: rgba(255,255,255,0.3); min-width: 110px; }
.log-msg { color: rgba(255,255,255,0.55); word-break: break-all; }
.level-ERROR .log-msg { color: #fca5a5; }
.level-WARNING .log-msg { color: #fde68a; }
.level-INFO .log-msg { color: rgba(255,255,255,0.55); }
.pagination-wrap {
  display: flex; justify-content: center; align-items: center; gap: 16px;
}
.page-btn {
  width: 38px; height: 38px; display: flex; align-items: center; justify-content: center;
  background: var(--bg-card); border: 1px solid var(--border-color);
  border-radius: 10px; color: var(--text-secondary); cursor: pointer; transition: all 0.25s ease;
}
.page-btn:hover:not(:disabled) { color: var(--text-primary); border-color: rgba(255,255,255,0.15); }
.page-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.page-btn svg { width: 18px; height: 18px; }
.page-info { font-size: 13px; font-weight: 600; color: var(--text-muted); }

@media (max-width: 768px) {
  .content { padding: 24px 16px 64px; }
  .page-title { font-size: 22px; }
  .stats-row { grid-template-columns: repeat(3, 1fr); gap: 8px; }
  .log-line { flex-wrap: wrap; gap: 4px; padding: 6px 0; }
}
@media (max-width: 560px) {
  .stats-row { grid-template-columns: 1fr; }
  .filter-row { flex-direction: column; align-items: flex-start; }
}
</style>