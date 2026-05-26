<template>
  <div class="page">
    <NavBar />
    <div class="content">
      <div class="page-header">
        <h1 class="page-title">数据预览</h1>
        <div class="header-actions">
          <button
            class="btn-batch-delete"
            :disabled="selectedIds.length === 0 || deleting"
            @click="handleBatchDelete"
          >
            批量删除{{ selectedIds.length > 0 ? ` (${selectedIds.length})` : '' }}
          </button>
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
            <input
              v-model="filters.keyword"
              placeholder="搜索标题、内容、链接、图片地址..."
              class="input"
              @input="onKeywordInput"
              @keyup.enter="applyFilters"
            />
          </div>
          <input type="date" v-model="filters.dateFrom" class="input input-date" @change="applyFilters" />
          <span class="date-sep">至</span>
          <input type="date" v-model="filters.dateTo" class="input input-date" @change="applyFilters" />
          <select v-model="filters.type" class="input input-select" @change="applyFilters">
            <option value="all">全部类型</option>
            <option value="link">链接</option>
            <option value="image">图片</option>
            <option value="page">页面</option>
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
                <input type="checkbox" v-model="col.visible" />
                <span>{{ col.label }}</span>
              </label>
            </div>
          </div>
          <button class="btn-reset" type="button" @click="resetFilters">重置</button>
        </div>
        <div class="filter-result">
          共 {{ totalCount }} 条数据，当前第 {{ currentPage }} / {{ totalPages }} 页，每页 {{ pageSize }} 条
          <span v-if="refreshing" class="refresh-hint">· 刷新中</span>
        </div>
      </div>

      <div class="card table-card" :class="{ 'is-refreshing': refreshing }">
        <el-table
          ref="tableRef"
          v-loading="loading"
          element-loading-custom-class="app-theme-loading"
          element-loading-text="加载中..."
          :data="tableData"
          border
          class="data-el-table"
          style="width: 100%"
          max-height="560"
          @sort-change="handleSortChange"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="48" fixed="left" />
          <el-table-column v-if="columnVisible('title')" prop="title" label="标题" min-width="160" sortable="custom" show-overflow-tooltip />
          <el-table-column v-if="columnVisible('link')" prop="link" label="链接" min-width="180" sortable="custom" show-overflow-tooltip>
            <template #default="{ row }">
              <a v-if="row.link" :href="row.link" target="_blank" rel="noopener" class="data-link">{{ row.link }}</a>
              <span v-else class="text-muted">—</span>
            </template>
          </el-table-column>
          <el-table-column v-if="columnVisible('image_url')" label="图片预览" width="100" align="center">
            <template #default="{ row }">
              <div v-if="getImageUrl(row)" class="thumb-cell">
                <el-image
                  :src="getImageUrl(row)"
                  :preview-src-list="[getImageUrl(row)]"
                  :preview-teleported="true"
                  fit="cover"
                  lazy
                  class="thumb-image"
                >
                  <template #error>
                    <span class="img-error">无效</span>
                  </template>
                </el-image>
              </div>
              <span v-else class="text-muted">—</span>
            </template>
          </el-table-column>
          <el-table-column v-if="columnVisible('content')" prop="content" label="内容摘要" min-width="200" sortable="custom" show-overflow-tooltip />
          <el-table-column v-if="columnVisible('type')" prop="type" label="类型" width="90" sortable="custom" align="center">
            <template #default="{ row }">
              <span class="type-tag" :class="'tag-' + (row.type || 'link')">{{ typeLabels[row.type] || row.type }}</span>
            </template>
          </el-table-column>
          <el-table-column v-if="columnVisible('source_url')" prop="source_url" label="来源URL" min-width="160" sortable="custom" show-overflow-tooltip />
          <el-table-column v-if="columnVisible('collected_at')" prop="collected_at" label="采集时间" width="170" sortable="custom" />
          <el-table-column label="操作" width="88" fixed="right" align="center">
            <template #default="{ row }">
              <button class="btn-row-delete" type="button" :disabled="deleting" @click="handleDeleteOne(row)">删除</button>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="!loading && !refreshing && tableData.length === 0" class="table-empty">
          <div class="empty-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
              <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
              <polyline points="13 2 13 9 20 9"/>
            </svg>
          </div>
          <p class="empty-text">{{ hasActiveFilters ? '未找到匹配的数据' : '暂无数据' }}</p>
          <p class="empty-desc">{{ hasActiveFilters ? '请调整搜索关键词或筛选条件后重试' : '尝试调整筛选条件或等待新的采集数据入库' }}</p>
        </div>

        <div v-if="totalCount > 0" class="pagination-bar">
          <button class="page-edge-btn" :disabled="currentPage <= 1" @click="goFirstPage">首页</button>
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="totalCount"
            layout="total, sizes, prev, pager, next, jumper"
            background
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
          <button class="page-edge-btn" :disabled="currentPage >= totalPages" @click="goLastPage">末页</button>
        </div>
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
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { dataAPI } from '../api/data'
import NavBar from '../components/NavBar.vue'

const loading = ref(false)
const refreshing = ref(false)
const deleting = ref(false)
const showExportOptions = ref(false)
const showColumnMenu = ref(false)
const tableRef = ref(null)

const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)
const tableData = ref([])
const selectedIds = ref([])

const filters = ref({
  keyword: '',
  dateFrom: '',
  dateTo: '',
  type: 'all'
})

const sortKey = ref('collected_at')
const sortDir = ref('desc')

let searchDebounceTimer = null

const typeLabels = { link: '链接', image: '图片', page: '页面', mixed: '混合' }

const columns = ref([
  { key: 'title', label: '标题', visible: true },
  { key: 'link', label: '链接', visible: true },
  { key: 'image_url', label: '图片预览', visible: true },
  { key: 'content', label: '内容摘要', visible: true },
  { key: 'type', label: '类型', visible: true },
  { key: 'source_url', label: '来源URL', visible: true },
  { key: 'collected_at', label: '采集时间', visible: true }
])

const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize.value)))

const hasActiveFilters = computed(() => {
  const f = filters.value
  return !!(f.keyword?.trim() || f.dateFrom || f.dateTo || (f.type && f.type !== 'all'))
})

function columnVisible(key) {
  return columns.value.find(c => c.key === key)?.visible ?? true
}

function getImageUrl(row) {
  const url = (row.image_url || '').trim()
  if (url) return url
  if (row.type === 'image' && row.link) return row.link.trim()
  return ''
}

function buildQueryParams() {
  const params = {
    page: currentPage.value,
    page_size: pageSize.value,
    sort_field: sortKey.value,
    sort_order: sortDir.value
  }
  const kw = filters.value.keyword?.trim()
  if (kw) params.keyword = kw
  if (filters.value.type && filters.value.type !== 'all') params.type = filters.value.type
  if (filters.value.dateFrom) params.date_from = filters.value.dateFrom
  if (filters.value.dateTo) params.date_to = filters.value.dateTo
  return params
}

async function loadData({ silent = false } = {}) {
  if (silent) {
    refreshing.value = true
  } else {
    loading.value = true
  }
  try {
    const res = await dataAPI.getDataList(buildQueryParams())
    if (res.data.success) {
      const data = res.data.data || {}
      tableData.value = data.list || []
      totalCount.value = data.total ?? 0
      if (data.page) currentPage.value = data.page
      if (data.page_size) pageSize.value = data.page_size
      selectedIds.value = []
      tableRef.value?.clearSelection()
    } else {
      tableData.value = []
      totalCount.value = 0
      ElMessage.error(res.data.message || '加载数据失败')
    }
  } catch (e) {
    tableData.value = []
    totalCount.value = 0
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

function onKeywordInput() {
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
  searchDebounceTimer = setTimeout(() => {
    currentPage.value = 1
    loadData({ silent: true })
  }, 300)
}

function applyFilters() {
  currentPage.value = 1
  loadData({ silent: true })
}

function resetFilters() {
  filters.value = { keyword: '', dateFrom: '', dateTo: '', type: 'all' }
  sortKey.value = 'collected_at'
  sortDir.value = 'desc'
  currentPage.value = 1
  loadData({ silent: true })
}

function handleSortChange({ prop, order }) {
  if (!prop || !order) {
    sortKey.value = 'collected_at'
    sortDir.value = 'desc'
  } else {
    sortKey.value = prop
    sortDir.value = order === 'ascending' ? 'asc' : 'desc'
  }
  currentPage.value = 1
  loadData({ silent: true })
}

function handleSelectionChange(rows) {
  selectedIds.value = rows.map(r => r.id)
}

function handlePageChange(page) {
  currentPage.value = page
  loadData({ silent: true })
}

function handleSizeChange(size) {
  pageSize.value = size
  currentPage.value = 1
  loadData({ silent: true })
}

function goFirstPage() {
  if (currentPage.value <= 1) return
  currentPage.value = 1
  loadData({ silent: true })
}

function goLastPage() {
  if (currentPage.value >= totalPages.value) return
  currentPage.value = totalPages.value
  loadData({ silent: true })
}

async function deleteRecords(ids) {
  if (!ids.length) return { success: false, message: '未选择数据' }
  if (ids.length === 1) {
    try {
      const res = await dataAPI.deleteData(ids[0])
      if (res.data.success) return res.data
    } catch (e) {
      if (e.response?.status !== 404) throw e
    }
  }
  const res = await dataAPI.batchDeleteData(ids)
  return res.data
}

async function handleDeleteOne(row) {
  try {
    await ElMessageBox.confirm(
      `确定删除「${(row.title || '该条数据').slice(0, 40)}」吗？此操作不可恢复。`,
      '确认删除',
      { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }
    )
    deleting.value = true
    const result = await deleteRecords([row.id])
    if (result.success) {
      ElMessage.success(result.message || '删除成功')
      if (tableData.value.length === 1 && currentPage.value > 1) {
        currentPage.value -= 1
      }
      await loadData({ silent: true })
    } else {
      ElMessage.error(result.message || '删除失败')
    }
  } catch (e) {
    if (e !== 'cancel' && e !== 'close') {
      const msg = e.response?.status === 404
        ? '删除接口不可用，请重启后端服务 (python app.py)'
        : '删除失败'
      ElMessage.error(msg)
    }
  } finally {
    deleting.value = false
  }
}

async function handleBatchDelete() {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先选择要删除的数据')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确定删除选中的 ${selectedIds.value.length} 条数据吗？此操作不可恢复。`,
      '批量删除确认',
      { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }
    )
    deleting.value = true
    const result = await deleteRecords(selectedIds.value)
    if (result.success) {
      ElMessage.success(result.message || '批量删除成功')
      currentPage.value = 1
      await loadData({ silent: true })
    } else {
      ElMessage.error(result.message || '批量删除失败')
    }
  } catch (e) {
    if (e !== 'cancel' && e !== 'close') {
      const msg = e.response?.status === 404
        ? '删除接口不可用，请重启后端服务 (python app.py)'
        : '批量删除失败'
      ElMessage.error(msg)
    }
  } finally {
    deleting.value = false
  }
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

onMounted(() => {
  loadData()
})

onBeforeUnmount(() => {
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
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
  flex-wrap: wrap;
  gap: 12px;
}
.page-title {
  font-size: 26px; font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}
.header-actions { display: flex; gap: 10px; flex-wrap: wrap; }
.btn-export, .btn-batch-delete {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 10px 20px; font-size: 13px; font-weight: 600;
  border-radius: 10px; cursor: pointer;
  transition: all 0.25s ease;
}
.btn-export {
  background: var(--gradient-primary);
  border: none; color: var(--btn-text-color);
  box-shadow: var(--btn-shadow);
}
.btn-export:hover { transform: translateY(-1px); box-shadow: var(--btn-hover-shadow); }
.btn-export svg { width: 16px; height: 16px; }
.btn-batch-delete {
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.35);
  color: #f87171;
}
.btn-batch-delete:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.2);
}
.btn-batch-delete:disabled { opacity: 0.45; cursor: not-allowed; }
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
  position: relative; display: flex; align-items: center; flex: 1; min-width: 220px;
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
.btn-reset {
  padding: 9px 16px; font-size: 12px; font-weight: 600;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-color);
  border-radius: 8px; color: var(--text-secondary);
  cursor: pointer;
}
.btn-reset:hover { color: var(--text-primary); background: rgba(255, 255, 255, 0.08); }
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
.refresh-hint { margin-left: 6px; color: var(--accent-primary); font-weight: 500; }
.table-card { overflow: hidden; padding: 0; }
.table-card.is-refreshing { opacity: 0.92; transition: opacity 0.2s ease; }
.data-el-table {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: rgba(0, 0, 0, 0.25);
  --el-table-row-hover-bg-color: rgba(var(--accent-rgb), 0.08);
  --el-table-border-color: var(--border-color);
  --el-table-text-color: var(--text-secondary);
  --el-table-header-text-color: var(--text-muted);
  --el-fill-color-lighter: rgba(255, 255, 255, 0.03);
  --el-bg-color: transparent;
}
.data-el-table :deep(.el-table__inner-wrapper),
.data-el-table :deep(.el-table__body-wrapper),
.data-el-table :deep(.el-table__header-wrapper) {
  background-color: transparent !important;
}
.data-el-table :deep(.el-table__header th.el-table__cell) {
  background-color: rgba(0, 0, 0, 0.25) !important;
  color: var(--text-muted) !important;
  border-color: var(--border-color) !important;
}
.data-el-table :deep(.el-table__body tr),
.data-el-table :deep(.el-table__body tr.el-table__row--striped) {
  background-color: rgba(255, 255, 255, 0.02) !important;
}
.data-el-table :deep(.el-table__body td.el-table__cell) {
  background-color: transparent !important;
  color: var(--text-secondary) !important;
  border-color: var(--border-color) !important;
}
.data-el-table :deep(.el-table__body tr:hover > td.el-table__cell) {
  background-color: rgba(var(--accent-rgb), 0.08) !important;
}
.data-el-table :deep(.el-table__body .cell) {
  color: var(--text-secondary);
}
.data-el-table :deep(.el-table__empty-block) {
  background-color: transparent !important;
}
.data-el-table :deep(.el-checkbox__inner) {
  background-color: rgba(255, 255, 255, 0.06);
  border-color: var(--border-color);
}
.thumb-cell {
  display: flex; justify-content: center; align-items: center;
}
.thumb-image {
  width: 56px; height: 56px; border-radius: 8px;
  border: 1px solid var(--border-color);
  cursor: zoom-in;
}
.img-error {
  font-size: 11px; color: var(--text-muted);
}
.data-link {
  color: var(--accent-color);
  text-decoration: none;
}
.data-link:hover { text-decoration: underline; }
.text-muted { color: var(--text-muted); font-size: 12px; }
.type-tag {
  display: inline-block; padding: 3px 10px; border-radius: 6px;
  font-size: 11px; font-weight: 600;
}
.tag-link { background: rgba(var(--accent-rgb), 0.15); color: var(--active-color); }
.tag-image { background: rgba(16,185,129,0.15); color: #34d399; }
.tag-page { background: rgba(255,255,255,0.08); color: var(--text-muted); }
.btn-row-delete {
  padding: 4px 10px; font-size: 12px; font-weight: 600;
  color: #f87171; background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.25);
  border-radius: 6px; cursor: pointer;
}
.btn-row-delete:hover:not(:disabled) { background: rgba(239, 68, 68, 0.18); }
.btn-row-delete:disabled { opacity: 0.5; cursor: not-allowed; }
.table-empty {
  text-align: center; padding: 48px 20px 32px;
}
.table-empty .empty-icon {
  width: 64px; height: 64px; margin: 0 auto 16px;
  border-radius: 16px; background: rgba(255,255,255,0.03);
  display: flex; align-items: center; justify-content: center;
  color: rgba(255,255,255,0.1);
}
.table-empty .empty-icon svg { width: 28px; height: 28px; }
.table-empty .empty-text { font-size: 16px; font-weight: 600; color: var(--text-muted); margin-bottom: 6px; }
.table-empty .empty-desc { font-size: 13px; color: var(--text-muted); }
.pagination-bar {
  display: flex; align-items: center; justify-content: center;
  flex-wrap: wrap; gap: 12px;
  padding: 20px 16px;
  border-top: 1px solid var(--border-color);
}
.page-edge-btn {
  padding: 8px 14px; font-size: 12px; font-weight: 600;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px; color: var(--text-secondary);
  cursor: pointer;
}
.page-edge-btn:hover:not(:disabled) { color: var(--text-primary); border-color: rgba(255,255,255,0.15); }
.page-edge-btn:disabled { opacity: 0.35; cursor: not-allowed; }
.pagination-bar :deep(.el-pagination) {
  flex-wrap: wrap;
  justify-content: center;
}
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

@media (max-width: 768px) {
  .content { padding: 24px 16px 64px; }
  .page-title { font-size: 22px; }
  .filter-row { gap: 8px; }
  .filter-input { min-width: 100%; flex: none; }
  .pagination-bar { flex-direction: column; }
  .modal-card { min-width: auto; width: 90%; padding: 24px; }
}
@media (max-width: 560px) {
  .export-options { flex-direction: column; }
}
</style>
