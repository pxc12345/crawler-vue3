<template>
  <div class="page">
    <NavBar />
    <div class="content">
      <div class="page-header">
        <h1 class="page-title">数据预览</h1>
        <div class="header-actions">
          <button class="btn-export" @click="showExportOptions = true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            导出数据
          </button>
        </div>
      </div>

      <div class="card filter-card">
        <div class="filter-row">
          <div class="filter-input">
            <svg class="filter-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input v-model="filters.keyword" placeholder="搜索标题、内容..." class="input" @input="handleFilter" />
          </div>
          <input type="date" v-model="filters.dateFrom" class="input input-date" @change="handleFilter" />
          <span class="date-sep">至</span>
          <input type="date" v-model="filters.dateTo" class="input input-date" @change="handleFilter" />
          <select v-model="filters.type" class="input input-select" @change="handleFilter">
            <option value="all">全部类型</option>
            <option value="link">链接</option>
            <option value="image">图片</option>
          </select>
          <div class="column-toggle-wrapper">
            <button class="btn-column" @click="showColumnMenu = !showColumnMenu">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/>
              </svg>
              列显示
            </button>
            <div v-if="showColumnMenu" class="column-menu">
              <label v-for="col in columns" :key="col.key" class="column-option">
                <input type="checkbox" v-model="col.visible" @change="handleFilter" />
                <span>{{ col.label }}</span>
              </label>
            </div>
          </div>
        </div>
        <div class="filter-result">共 {{ totalFiltered }} 条数据，当前第 {{ currentPage }} 页</div>
      </div>

      <div v-if="loading" class="card skeleton-wrap">
        <div v-for="n in 6" :key="n" class="skeleton-row">
          <div class="skeleton-line w-15"></div>
          <div class="skeleton-line w-25"></div>
          <div class="skeleton-line w-35"></div>
          <div class="skeleton-line w-10"></div>
          <div class="skeleton-line w-10"></div>
        </div>
      </div>

      <div v-else-if="filteredData.length === 0" class="card empty-state">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
            <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
            <polyline points="13 2 13 9 20 9"/>
          </svg>
        </div>
        <p class="empty-text">暂无数据</p>
        <p class="empty-desc">尝试调整筛选条件或等待新的采集数据入库</p>
      </div>

      <div v-else class="card table-card">
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th v-if="columnVisible('title')" class="sortable" @click="toggleSort('title')">
                  标题 <span class="sort-icon">{{ sortIcon('title') }}</span>
                </th>
                <th v-if="columnVisible('link')" class="sortable" @click="toggleSort('link')">
                  链接 <span class="sort-icon">{{ sortIcon('link') }}</span>
                </th>
                <th v-if="columnVisible('content')" class="sortable" @click="toggleSort('content')">
                  内容摘要 <span class="sort-icon">{{ sortIcon('content') }}</span>
                </th>
                <th v-if="columnVisible('type')" class="sortable" @click="toggleSort('type')">
                  类型 <span class="sort-icon">{{ sortIcon('type') }}</span>
                </th>
                <th v-if="columnVisible('source_url')" class="sortable" @click="toggleSort('source_url')">
                  来源URL <span class="sort-icon">{{ sortIcon('source_url') }}</span>
                </th>
                <th v-if="columnVisible('collected_at')" class="sortable" @click="toggleSort('collected_at')">
                  采集时间 <span class="sort-icon">{{ sortIcon('collected_at') }}</span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in paginatedData" :key="row.id">
                <td v-if="columnVisible('title')" class="td-title">{{ row.title }}</td>
                <td v-if="columnVisible('link')">
                  <a :href="row.link" target="_blank" class="data-link">{{ row.link }}</a>
                </td>
                <td v-if="columnVisible('content')" class="td-content">{{ row.content }}</td>
                <td v-if="columnVisible('type')">
                  <span class="type-tag" :class="'tag-' + row.type">{{ typeLabels[row.type] }}</span>
                </td>
                <td v-if="columnVisible('source_url')" class="td-source">{{ row.source_url }}</td>
                <td v-if="columnVisible('collected_at')" class="td-time">{{ row.collected_at }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="totalFiltered > 0 && !loading" class="pagination-wrap">
        <button class="page-btn" :disabled="currentPage <= 1" @click="currentPage--">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
        </button>
        <div class="page-numbers">
          <button
            v-for="p in pageNumbers"
            :key="p"
            class="page-num"
            :class="{ active: p === currentPage }"
            @click="currentPage = p"
          >{{ p }}</button>
        </div>
        <button class="page-btn" :disabled="currentPage >= totalPages" @click="currentPage++">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
        </button>
      </div>

      <div v-if="showExportOptions" class="modal-overlay" @click.self="showExportOptions = false">
        <div class="modal-card">
          <h3 class="modal-title">导出选项</h3>
          <div class="export-options">
            <div class="export-option" @click="handleExport('csv')">
              <div class="export-icon-wrap"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg></div>
              <span>CSV</span>
            </div>
            <div class="export-option" @click="handleExport('excel')">
              <div class="export-icon-wrap"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><path d="M8 13h2"/><path d="M8 17h2"/><path d="M14 13h2"/><path d="M14 17h2"/></svg></div>
              <span>Excel</span>
            </div>
            <div class="export-option" @click="handleExport('json')">
              <div class="export-icon-wrap"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><path d="M10 12a2 2 0 0 1 4 0v4a2 2 0 0 1-4 0z"/></svg></div>
              <span>JSON</span>
            </div>
          </div>
          <button class="btn-close-modal" @click="showExportOptions = false">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { dataAPI } from '../api/data'
import NavBar from '../components/NavBar.vue'

const loading = ref(true)
const showExportOptions = ref(false)
const showColumnMenu = ref(false)
const currentPage = ref(1)
const pageSize = 10

const filters = ref({
  keyword: '',
  dateFrom: '',
  dateTo: '',
  type: 'all'
})

const sortKey = ref('')
const sortDir = ref('asc')

const typeLabels = { link: '链接', image: '图片' }

const columns = ref([
  { key: 'title', label: '标题', visible: true },
  { key: 'link', label: '链接', visible: true },
  { key: 'content', label: '内容摘要', visible: true },
  { key: 'type', label: '类型', visible: true },
  { key: 'source_url', label: '来源URL', visible: true },
  { key: 'collected_at', label: '采集时间', visible: true }
])

const rawData = ref([])

function columnVisible(key) {
  return columns.value.find(c => c.key === key)?.visible ?? true
}

function toggleSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}

function sortIcon(key) {
  if (sortKey.value !== key) return '↕'
  return sortDir.value === 'asc' ? '↑' : '↓'
}

const filteredData = computed(() => {
  let result = [...rawData.value]
  if (filters.value.keyword) {
    const kw = filters.value.keyword.toLowerCase()
    result = result.filter(r => (r.title || '').toLowerCase().includes(kw) || (r.content || '').toLowerCase().includes(kw))
  }
  if (filters.value.dateFrom) {
    result = result.filter(r => r.collected_at >= filters.value.dateFrom)
  }
  if (filters.value.dateTo) {
    result = result.filter(r => r.collected_at <= filters.value.dateTo)
  }
  if (filters.value.type !== 'all') {
    result = result.filter(r => r.type === filters.value.type)
  }
  if (sortKey.value) {
    result.sort((a, b) => {
      const va = a[sortKey.value] || ''
      const vb = b[sortKey.value] || ''
      const cmp = String(va).localeCompare(String(vb))
      return sortDir.value === 'asc' ? cmp : -cmp
    })
  }
  return result
})

const totalFiltered = computed(() => filteredData.value.length)

const totalPages = computed(() => Math.max(1, Math.ceil(totalFiltered.value / pageSize)))

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredData.value.slice(start, start + pageSize)
})

const pageNumbers = computed(() => {
  const pages = []
  const total = totalPages.value
  const curr = currentPage.value
  let start = Math.max(1, curr - 2)
  let end = Math.min(total, curr + 2)
  if (end - start < 4) {
    if (start === 1) end = Math.min(total, start + 4)
    else start = Math.max(1, end - 4)
  }
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

function handleFilter() {
  currentPage.value = 1
}

async function handleExport(format) {
  showExportOptions.value = false
  try {
    const { downloadFile } = await import('../api/index')
    const fields = columns.value.filter(c => c.visible).map(c => c.key).join(',')
    await downloadFile('/data/export?fields=' + fields, `data_export.${format}`, format)
    ElMessage.success(`导出 ${format.toUpperCase()} 成功`)
  } catch (error) {
    ElMessage.error('导出失败，请重试')
  }
}

async function loadData() {
  loading.value = true
  try {
    const res = await dataAPI.getDataList({
      page: currentPage.value,
      page_size: pageSize,
      keyword: filters.value.keyword || undefined,
      type: filters.value.type !== 'all' ? filters.value.type : undefined,
      sort_field: sortKey.value || undefined,
      sort_order: sortDir.value || undefined
    })
    if (res.data.success) {
      rawData.value = res.data.data.list || res.data.data || []
    } else {
      rawData.value = []
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
    rawData.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
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
  position: fixed;
  top: 0; left: 0;
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
  position: relative;
  z-index: 1;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}
.page-title {
  font-size: 26px; font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}
.btn-export {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 10px 20px; font-size: 13px; font-weight: 600;
  background: var(--gradient-primary);
  border: none; border-radius: 10px; color: var(--btn-text-color); cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: var(--btn-shadow);
}
.btn-export:hover { transform: translateY(-1px); box-shadow: var(--btn-hover-shadow); }
.btn-export svg { width: 16px; height: 16px; }
.card {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  margin-bottom: 20px;
}
.filter-card { padding: 20px 24px; }
.filter-row {
  display: flex; gap: 12px; align-items: center;
  flex-wrap: wrap;
}
.filter-input {
  position: relative; display: flex; align-items: center; flex: 1; min-width: 180px;
}
.filter-icon {
  position: absolute; left: 12px; width: 16px; height: 16px;
  color: var(--text-muted); pointer-events: none;
}
.input {
  padding: 9px 14px; font-size: 13px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-color);
  border-radius: 8px; color: var(--text-primary);
  outline: none; transition: all 0.2s ease;
}
.filter-input .input { padding-left: 36px; width: 100%; }
.input:focus { border-color: rgba(var(--accent-rgb), 0.4); background: rgba(255, 255, 255, 0.06); }
.date-sep { font-size: 12px; color: var(--text-muted); }
.input-select { min-width: 120px; cursor: pointer; color-scheme: dark; }
.column-toggle-wrapper { position: relative; }
.btn-column {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 9px 14px; font-size: 12px; font-weight: 500;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px; color: rgba(255, 255, 255, 0.45);
  cursor: pointer; transition: all 0.2s ease;
}
.btn-column:hover { color: rgba(255, 255, 255, 0.75); border-color: rgba(255, 255, 255, 0.15); }
.btn-column svg { width: 15px; height: 15px; }
.column-menu {
  position: absolute; top: calc(100% + 6px); right: 0; min-width: 170px;
  background: var(--bg-card);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px; padding: 8px;
  z-index: 50; box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.column-option {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 12px; font-size: 12px; color: rgba(255, 255, 255, 0.55);
  cursor: pointer; border-radius: 8px; transition: all 0.15s ease;
}
.column-option:hover { background: rgba(255, 255, 255, 0.04); color: rgba(255, 255, 255, 0.75); }
.column-option input { accent-color: var(--accent-primary); }
.filter-result { margin-top: 12px; font-size: 12px; color: var(--text-muted); }
.skeleton-wrap { padding: 16px 24px; }
.skeleton-row { display: flex; gap: 24px; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.02); }
.skeleton-line {
  height: 14px; background: rgba(255,255,255,0.04); border-radius: 7px;
  animation: shimmer 1.5s ease-in-out infinite;
}
.skeleton-line.w-15 { width: 15%; } .skeleton-line.w-10 { width: 10%; }
.skeleton-line.w-25 { width: 25%; } .skeleton-line.w-35 { width: 35%; }
@keyframes shimmer { 0%,100% { opacity: 0.4; } 50% { opacity: 0.8; } }
.empty-state { text-align: center; padding: 80px 20px; }
.empty-icon {
  width: 80px; height: 80px; margin: 0 auto 24px;
  border-radius: 20px; background: rgba(255,255,255,0.03);
  display: flex; align-items: center; justify-content: center;
  color: rgba(255,255,255,0.1);
}
.empty-icon svg { width: 36px; height: 36px; }
.empty-text { font-size: 18px; font-weight: 600; color: var(--text-muted); margin-bottom: 8px; }
.empty-desc { font-size: 13px; color: var(--text-muted); }
.table-card { overflow: hidden; }
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th {
  padding: 14px 16px; text-align: left; font-weight: 600;
  color: var(--text-muted); font-size: 11px; text-transform: uppercase;
  letter-spacing: 0.5px; border-bottom: 1px solid var(--border-color);
  white-space: nowrap; background: rgba(0,0,0,0.15);
}
.data-table th.sortable { cursor: pointer; user-select: none; }
.data-table th.sortable:hover { color: var(--text-secondary); }
.sort-icon { font-size: 10px; margin-left: 4px; opacity: 0.5; }
.data-table td {
  padding: 12px 16px; color: var(--text-secondary);
  border-bottom: 1px solid var(--border-color);
  vertical-align: top; line-height: 1.5;
}
.data-table tbody tr { transition: background 0.15s ease; }
.data-table tbody tr:hover { background: rgba(var(--accent-rgb), 0.04); }
.td-title { font-weight: 500; color: var(--text-primary); max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.data-link { color: var(--accent-color); text-decoration: none; max-width: 180px; display: inline-block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.data-link:hover { text-decoration: underline; }
.td-content { max-width: 280px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--text-muted); }
.td-source { max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-family: monospace; font-size: 12px; }
.td-time { white-space: nowrap; font-family: monospace; font-size: 12px; color: var(--text-muted); }
.type-tag {
  display: inline-block; padding: 3px 10px; border-radius: 6px;
  font-size: 11px; font-weight: 600;
}
.tag-link { background: rgba(var(--accent-rgb), 0.15); color: var(--active-color); }
.tag-image { background: rgba(16,185,129,0.15); color: #34d399; }
.pagination-wrap {
  display: flex; justify-content: center; align-items: center;
  gap: 8px; margin-top: 24px;
}
.page-btn {
  width: 38px; height: 38px; display: flex; align-items: center; justify-content: center;
  background: var(--bg-card); border: 1px solid var(--border-color);
  border-radius: 10px; color: var(--text-secondary); cursor: pointer; transition: all 0.25s ease;
}
.page-btn:hover:not(:disabled) { color: var(--text-primary); border-color: var(--border-color); }
.page-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.page-btn svg { width: 18px; height: 18px; }
.page-numbers { display: flex; gap: 4px; }
.page-num {
  width: 34px; height: 34px; display: flex; align-items: center; justify-content: center;
  background: transparent; border: 1px solid transparent; border-radius: 8px;
  font-size: 13px; font-weight: 500; color: var(--text-muted); cursor: pointer; transition: all 0.2s ease;
}
.page-num:hover { color: var(--text-primary); background: rgba(255,255,255,0.04); }
.page-num.active { background: rgba(var(--accent-rgb), 0.15); color: var(--accent-color); border-color: rgba(var(--accent-rgb), 0.2); font-weight: 600; }
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center; z-index: 200;
}
.modal-card {
  background: var(--bg-card);
  backdrop-filter: blur(24px);
  border: 1px solid var(--border-color);
  border-radius: 20px; padding: 32px;
  min-width: 400px; box-shadow: 0 16px 64px rgba(0,0,0,0.5);
}
.modal-title { font-size: 18px; font-weight: 700; color: var(--text-primary); margin-bottom: 24px; text-align: center; }
.export-options { display: flex; gap: 16px; margin-bottom: 24px; }
.export-option {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 10px;
  padding: 24px 16px; background: rgba(255,255,255,0.03);
  border: 1px solid var(--border-color); border-radius: 14px;
  cursor: pointer; transition: all 0.25s ease; color: var(--text-secondary);
}
.export-option:hover { background: rgba(var(--accent-rgb), 0.1); border-color: rgba(var(--accent-rgb), 0.25); color: var(--accent-color); }
.export-icon-wrap { width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; }
.export-icon-wrap svg { width: 28px; height: 28px; }
.btn-close-modal {
  width: 100%; padding: 10px; font-size: 13px; font-weight: 600;
  background: rgba(255,255,255,0.04); border: 1px solid var(--border-color);
  border-radius: 10px; color: var(--text-secondary); cursor: pointer; transition: all 0.2s ease;
}
.btn-close-modal:hover { background: rgba(255,255,255,0.08); color: var(--text-primary); }
.header-actions { display: flex; gap: 10px; }

@media (max-width: 768px) {
  .content { padding: 24px 16px 64px; }
  .page-title { font-size: 22px; }
  .filter-row { gap: 8px; }
  .filter-input { min-width: 100%; flex: none; }
  .modal-card { min-width: auto; width: 90%; padding: 24px; }
}
@media (max-width: 560px) {
  .data-table th, .data-table td { padding: 8px 10px; font-size: 11px; }
  .export-options { flex-direction: column; }
}
</style>