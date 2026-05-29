<template>
  <div class="page">
    <NavBar />
    <div class="content">
      <div class="page-header">
        <h1 class="page-title">数据清洗</h1>
        <span class="data-count">{{ rawData.length }} 条数据</span>
      </div>

      <div class="two-panel">
        <div class="card left-panel">
          <h3 class="panel-title">清洗操作</h3>

          <div class="op-section">
            <div class="op-header">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3"/>
              </svg>
              <span>一键去重</span>
            </div>
            <p class="op-desc">自动检测并移除重复数据行</p>
            <p v-if="dedupResult" class="op-result success">{{ dedupResult }}</p>
            <button class="btn-op" @click="runDedup" :disabled="processing">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
              {{ processing && activeOp === 'dedup' ? '处理中...' : '一键去重' }}
            </button>
          </div>

          <div class="op-section">
            <div class="op-header">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
              </svg>
              <span>空值过滤</span>
            </div>
            <p class="op-desc">选择字段，过滤空值行</p>
            <select v-model="nullFilterField" class="input input-select">
              <option value="">选择字段...</option>
              <option value="title">标题</option>
              <option value="link">链接</option>
              <option value="content">内容</option>
              <option value="source_url">来源URL</option>
            </select>
            <p v-if="nullFilterResult" class="op-result success">{{ nullFilterResult }}</p>
            <button class="btn-op" @click="runNullFilter" :disabled="processing || !nullFilterField">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
              {{ processing && activeOp === 'nullFilter' ? '处理中...' : '过滤空值' }}
            </button>
          </div>

          <div class="op-section">
            <div class="op-header">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="10" y1="6" x2="18" y2="6"/>
              </svg>
              <span>字段格式转换</span>
            </div>
            <p class="op-desc">对指定字段进行格式转换</p>
            <select v-model="formatField" class="input input-select">
              <option value="">选择字段...</option>
              <option value="title">标题</option>
              <option value="content">内容</option>
              <option value="collected_at">采集时间</option>
            </select>
            <select v-model="formatType" class="input input-select" style="margin-top:8px">
              <option value="">选择格式...</option>
              <option value="trim">去除首尾空格</option>
              <option value="lowercase">转为小写</option>
              <option value="uppercase">转为大写</option>
              <option value="timestamp">时间戳转日期</option>
            </select>
            <p v-if="formatResult" class="op-result success">{{ formatResult }}</p>
            <button class="btn-op" @click="runFormat" :disabled="processing || !formatField || !formatType">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
              {{ processing && activeOp === 'format' ? '处理中...' : '执行转换' }}
            </button>
          </div>

          <div v-if="hasChanges" class="action-row">
            <button class="btn-apply" @click="applyChanges">应用更改</button>
            <button class="btn-cancel" @click="resetData">取消</button>
          </div>

          <div v-if="processing" class="progress-bar-wrap">
            <div class="progress-bar" :style="{ width: progressPercent + '%' }"></div>
          </div>
        </div>

        <div class="card right-panel">
          <h3 class="panel-title">
            数据预览
            <span class="preview-count">{{ displayData.length }} 条</span>
          </h3>
          <div class="filter-card">
            <div class="filter-row">
              <div class="filter-input">
                <svg class="filter-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                <input v-model="tableKeyword" placeholder="搜索标题、内容、链接..." class="input" />
              </div>
              <div class="column-toggle-wrapper">
                <button type="button" class="btn-column" @click="showColumnMenu = !showColumnMenu">列显示</button>
                <div v-if="showColumnMenu" class="column-menu">
                  <label v-for="col in columns" :key="col.key" class="column-option">
                    <input type="checkbox" v-model="col.visible" />
                    <span>{{ col.label }}</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
          <div class="table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th v-if="columnVisible('title')" class="sortable" @click="toggleSort('title')">标题 {{ sortIndicator('title') }}</th>
                  <th v-if="columnVisible('link')" class="sortable" @click="toggleSort('link')">链接 {{ sortIndicator('link') }}</th>
                  <th v-if="columnVisible('content')" class="sortable" @click="toggleSort('content')">内容 {{ sortIndicator('content') }}</th>
                  <th v-if="columnVisible('source_url')" class="sortable" @click="toggleSort('source_url')">来源 {{ sortIndicator('source_url') }}</th>
                  <th v-if="columnVisible('collected_at')" class="sortable" @click="toggleSort('collected_at')">采集时间 {{ sortIndicator('collected_at') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, idx) in displayData" :key="row.id || idx">
                  <td class="td-idx">{{ idx + 1 }}</td>
                  <td v-if="columnVisible('title')" class="td-title">{{ row.title || '-' }}</td>
                  <td v-if="columnVisible('link')" class="td-link">{{ row.link || '-' }}</td>
                  <td v-if="columnVisible('content')" class="td-content">{{ (row.content || '-').slice(0, 30) }}{{ row.content && row.content.length > 30 ? '...' : '' }}</td>
                  <td v-if="columnVisible('source_url')" class="td-source">{{ row.source_url || '-' }}</td>
                  <td v-if="columnVisible('collected_at')" class="td-time">{{ row.collected_at || '-' }}</td>
                </tr>
                <tr v-if="displayData.length === 0">
                  <td colspan="6" class="td-empty">暂无数据</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { dataAPI } from '../api/data'
import NavBar from '../components/NavBar.vue'

const route = useRoute()

const processing = ref(false)
const activeOp = ref('')
const progressPercent = ref(0)
const hasChanges = ref(false)

const nullFilterField = ref('')
const formatField = ref('')
const formatType = ref('')

const dedupResult = ref('')
const nullFilterResult = ref('')
const formatResult = ref('')

const rawData = ref([])
const previewData = ref([])

const tableKeyword = ref('')
const showColumnMenu = ref(false)
const sortKey = ref('collected_at')
const sortDir = ref('desc')

const columns = ref([
  { key: 'title', label: '标题', visible: true },
  { key: 'link', label: '链接', visible: true },
  { key: 'content', label: '内容', visible: true },
  { key: 'source_url', label: '来源', visible: true },
  { key: 'collected_at', label: '采集时间', visible: true }
])

function columnVisible(key) {
  const col = columns.value.find(c => c.key === key)
  return col ? col.visible : true
}

function sortIndicator(key) {
  if (sortKey.value !== key) return '↕'
  return sortDir.value === 'asc' ? '↑' : '↓'
}

function toggleSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}

const displayData = computed(() => {
  let rows = [...previewData.value]
  const kw = tableKeyword.value.trim().toLowerCase()
  if (kw) {
    rows = rows.filter(r =>
      ['title', 'content', 'link', 'source_url'].some(f =>
        String(r[f] || '').toLowerCase().includes(kw)
      )
    )
  }
  const key = sortKey.value
  const dir = sortDir.value === 'asc' ? 1 : -1
  rows.sort((a, b) => {
    const va = a[key] ?? ''
    const vb = b[key] ?? ''
    if (va < vb) return -1 * dir
    if (va > vb) return 1 * dir
    return 0
  })
  return rows
})

function parseCleanItems(res) {
  const d = res.data?.data
  return d?.items || d?.list || (Array.isArray(d) ? d : [])
}

async function runDedup() {
  activeOp.value = 'dedup'
  processing.value = true
  progressPercent.value = 0
  const interval = setInterval(() => {
    progressPercent.value = Math.min(100, progressPercent.value + 25)
    if (progressPercent.value >= 100) clearInterval(interval)
  }, 150)
  try {
    const res = await dataAPI.cleanData({
      operations: ['deduplicate'],
      data: previewData.value
    })
    if (res.data.success) {
      const before = previewData.value.length
      previewData.value = parseCleanItems(res)
      const removed = before - previewData.value.length
      dedupResult.value = `已去除 ${removed} 条重复数据`
      hasChanges.value = removed > 0
    }
  } catch (error) {
    ElMessage.error('去重操作失败')
  } finally {
    processing.value = false
    progressPercent.value = 0
  }
}

async function runNullFilter() {
  activeOp.value = 'nullFilter'
  processing.value = true
  progressPercent.value = 0
  const interval = setInterval(() => {
    progressPercent.value = Math.min(100, progressPercent.value + 30)
    if (progressPercent.value >= 100) clearInterval(interval)
  }, 120)
  try {
    const res = await dataAPI.cleanData({
      operations: ['filter_empty'],
      data: previewData.value,
      fields: [nullFilterField.value]
    })
    if (res.data.success) {
      const before = previewData.value.length
      previewData.value = parseCleanItems(res)
      const removed = before - previewData.value.length
      nullFilterResult.value = `已过滤 ${removed} 条空值数据`
      hasChanges.value = removed > 0
    }
  } catch (error) {
    ElMessage.error('空值过滤失败')
  } finally {
    processing.value = false
    progressPercent.value = 0
  }
}

async function runFormat() {
  activeOp.value = 'format'
  processing.value = true
  progressPercent.value = 0
  const interval = setInterval(() => {
    progressPercent.value = Math.min(100, progressPercent.value + 20)
    if (progressPercent.value >= 100) clearInterval(interval)
  }, 100)
  try {
    const res = await dataAPI.cleanData({
      operations: ['format_convert'],
      data: previewData.value,
      field: formatField.value,
      format: formatType.value === 'timestamp' ? 'timestamp_to_date' : formatType.value
    })
    if (res.data.success) {
      const resultData = parseCleanItems(res)
      let count = 0
      previewData.value.forEach((row, idx) => {
        if (JSON.stringify(row) !== JSON.stringify(resultData[idx])) count++
      })
      previewData.value = resultData
      formatResult.value = `已转换 ${count} 条数据的字段格式`
      hasChanges.value = count > 0
    }
  } catch (error) {
    ElMessage.error('格式转换失败')
  } finally {
    processing.value = false
    progressPercent.value = 0
  }
}

async function applyChanges() {
  processing.value = true
  try {
    const res = await dataAPI.cleanData({
      operations: [],
      data: previewData.value,
      save_to_db: true
    })
    if (res.data.success) {
      rawData.value = previewData.value.map(r => ({ ...r }))
      ElMessage.success('数据清洗结果已保存到数据库')
      hasChanges.value = false
      dedupResult.value = ''
      nullFilterResult.value = ''
      formatResult.value = ''
      nullFilterField.value = ''
      formatField.value = ''
      formatType.value = ''
    } else {
      ElMessage.error(res.data.message || '保存失败')
    }
  } catch (error) {
    ElMessage.error('应用更改失败')
  } finally {
    processing.value = false
  }
}

function resetData() {
  previewData.value = rawData.value.map(r => ({ ...r }))
  hasChanges.value = false
  dedupResult.value = ''
  nullFilterResult.value = ''
  formatResult.value = ''
  ElMessage.info('已恢复原始数据')
}

onMounted(async () => {
  try {
    const params = { page_size: 500 }
    const taskId = route.query.task_id
    if (taskId) params.task_id = taskId
    const res = await dataAPI.getDataList(params)
    if (res.data.success) {
      const list = res.data.data?.list || res.data.data || []
      rawData.value = list.map(r => ({ ...r }))
      previewData.value = rawData.value.map(r => ({ ...r }))
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
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
    radial-gradient(ellipse 80% 60% at 50% -20%, rgba(76, 110, 245, 0.06), transparent),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(124, 58, 237, 0.04), transparent);
  pointer-events: none; z-index: 0;
}
.content {
  max-width: 1280px;
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
.data-count {
  font-size: 13px; font-weight: 500;
  padding: 6px 14px; background: rgba(var(--accent-rgb), 0.1);
  color: var(--accent-color); border-radius: 20px;
}
.two-panel {
  display: grid; grid-template-columns: 380px 1fr;
  gap: 20px; align-items: start;
}
.card {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
}
.left-panel { padding: 24px; }
.right-panel { padding: 24px; }
.panel-title {
  font-size: 15px; font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 20px; display: flex; align-items: center; gap: 10px;
}
.preview-count {
  font-size: 11px; font-weight: 500; color: var(--text-muted);
  padding: 2px 8px; background: rgba(255,255,255,0.04); border-radius: 6px;
}
.filter-card { margin-bottom: 12px; }
.filter-row { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.filter-input { flex: 1; min-width: 160px; position: relative; }
.filter-icon {
  position: absolute; left: 10px; top: 50%; transform: translateY(-50%);
  width: 14px; height: 14px; color: var(--text-muted); pointer-events: none;
}
.filter-input .input { padding-left: 32px; }
.column-toggle-wrapper { position: relative; }
.btn-column {
  padding: 8px 12px; font-size: 12px; font-weight: 500;
  background: rgba(255,255,255,0.04); border: 1px solid var(--border-color);
  border-radius: 8px; color: var(--text-secondary); cursor: pointer;
}
.column-menu {
  position: absolute; right: 0; top: 100%; margin-top: 4px; z-index: 10;
  padding: 8px; background: var(--bg-card); border: 1px solid var(--border-color);
  border-radius: 8px; min-width: 120px;
}
.column-option { display: flex; align-items: center; gap: 6px; font-size: 12px; padding: 4px 0; color: var(--text-secondary); cursor: pointer; }
.data-table th.sortable { cursor: pointer; user-select: none; }
.op-section {
  padding: 16px; margin-bottom: 12px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}
.op-header {
  display: flex; align-items: center; gap: 8px;
  font-size: 14px; font-weight: 600; color: var(--text-secondary);
  margin-bottom: 6px;
}
.op-header svg { width: 18px; height: 18px; color: var(--accent-color); }
.op-desc {
  font-size: 12px; color: var(--text-muted);
  margin-bottom: 10px; line-height: 1.4;
}
.op-result {
  font-size: 12px; font-weight: 500; margin-bottom: 8px; padding: 4px 0;
}
.op-result.success { color: #34d399; }
.input {
  width: 100%; padding: 9px 14px; font-size: 13px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-color);
  border-radius: 8px; color: var(--text-primary);
  outline: none; transition: all 0.2s ease; box-sizing: border-box;
}
.input:focus { border-color: rgba(var(--accent-rgb), 0.4); background: rgba(255, 255, 255, 0.06); }
.input-select { cursor: pointer; color-scheme: dark; margin-bottom: 8px; }
.btn-op {
  display: inline-flex; align-items: center; gap: 5px;
  width: 100%; padding: 10px 16px; margin-top: 8px;
  font-size: 13px; font-weight: 600;
  background: rgba(var(--accent-rgb), 0.1);
  border: 1px solid rgba(var(--accent-rgb), 0.2);
  border-radius: 10px; color: var(--accent-color);
  cursor: pointer; transition: all 0.2s ease;
  justify-content: center;
}
.btn-op:hover:not(:disabled) { background: rgba(var(--accent-rgb), 0.2); }
.btn-op:disabled { opacity: 0.35; cursor: not-allowed; }
.btn-op svg { width: 16px; height: 16px; }
.action-row {
  display: flex; gap: 10px; margin-top: 16px; padding-top: 16px;
  border-top: 1px solid var(--border-color);
}
.btn-apply {
  flex: 1; padding: 11px 16px; font-size: 13px; font-weight: 600;
  background: var(--gradient-primary);
  border: none; border-radius: 10px; color: #fff; cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 2px 12px rgba(var(--accent-rgb), 0.3);
}
.btn-apply:hover { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(var(--accent-rgb), 0.45); }
.btn-cancel {
  padding: 11px 20px; font-size: 13px; font-weight: 500;
  background: rgba(255,255,255,0.04); border: 1px solid var(--border-color);
  border-radius: 10px; color: var(--text-secondary); cursor: pointer; transition: all 0.2s ease;
}
.btn-cancel:hover { background: rgba(255,255,255,0.08); color: var(--text-primary); }
.progress-bar-wrap {
  margin-top: 14px; height: 4px; background: rgba(255,255,255,0.04);
  border-radius: 2px; overflow: hidden;
}
.progress-bar {
  height: 100%; background: var(--gradient-primary);
  border-radius: 2px; transition: width 0.3s ease;
}
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.data-table th {
  padding: 10px 12px; text-align: left; font-weight: 600;
  color: var(--text-muted); font-size: 10px; text-transform: uppercase;
  letter-spacing: 0.4px; border-bottom: 1px solid var(--border-color);
  white-space: nowrap; background: rgba(0,0,0,0.15);
}
.data-table td {
  padding: 10px 12px; color: var(--text-secondary);
  border-bottom: 1px solid var(--border-color);
  vertical-align: top; line-height: 1.4; max-width: 160px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.data-table tbody tr { transition: background 0.15s ease; }
.data-table tbody tr:hover { background: rgba(var(--accent-rgb), 0.04); }
.td-idx { color: var(--text-muted); font-size: 11px; width: 30px; }
.td-title { font-weight: 500; color: var(--text-primary); }
.td-link { color: var(--accent-color); }
.td-content { color: var(--text-muted); }
.td-source { font-family: monospace; font-size: 11px; color: var(--text-muted); }
.td-time { white-space: nowrap; color: var(--text-muted); font-size: 11px; }
.td-empty { text-align: center; color: var(--text-muted); padding: 40px 12px !important; }

@media (max-width: 768px) {
  .content { padding: 24px 16px 64px; }
  .page-title { font-size: 22px; }
  .two-panel { grid-template-columns: 1fr; }
  .left-panel { padding: 20px; }
  .right-panel { padding: 20px; }
}
@media (max-width: 560px) {
  .action-row { flex-direction: column; }
  .data-table th, .data-table td { padding: 6px 8px; font-size: 10px; }
}
</style>
