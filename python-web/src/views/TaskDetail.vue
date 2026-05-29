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
                <input v-model="form.targetUrl" type="text" class="form-input" :disabled="!editing" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">执行周期（分钟）</label>
                <input v-model.number="form.intervalMinutes" type="number" class="form-input" :disabled="!editing" placeholder="例如：30" min="1" />
              </div>
              <div class="form-group">
                <label class="form-label">爬取页数</label>
                <input v-model.number="form.totalPages" type="number" class="form-input" :disabled="!editing" min="1" max="100" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">并发数</label>
                <input v-model.number="form.concurrency" type="number" class="form-input" :disabled="!editing" min="1" />
              </div>
              <div class="form-group">
                <label class="form-label">请求间隔 (秒)</label>
                <input v-model.number="form.intervalSeconds" type="number" class="form-input" :disabled="!editing" min="1" max="60" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">最大重试次数</label>
                <input v-model.number="form.maxRetries" type="number" class="form-input" :disabled="!editing" min="0" />
              </div>
              <div class="form-group">
                <label class="form-label">重试间隔 (秒)</label>
                <input v-model.number="form.retryInterval" type="number" class="form-input" :disabled="!editing" min="1" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group full">
                <label class="form-label">任务类型</label>
                <select v-model="form.taskType" class="form-input" :disabled="!editing">
                  <option value="crawler">爬虫任务</option>
                  <option value="data_collection">数据采集</option>
                  <option value="monitor">监控任务</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group full">
                <label class="form-label">爬取模式</label>
                <select v-model="form.crawlMode" class="form-input" :disabled="!editing">
                  <option value="link">链接模式</option>
                  <option value="image">图片模式</option>
                  <option value="mixed">混合模式</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group full">
                <label class="form-label">代理组</label>
                <select v-model="form.proxyGroup" class="form-input" :disabled="!editing">
                  <option value="">不使用代理组</option>
                  <option v-for="g in proxyGroups" :key="g.id" :value="g.name">{{ g.name }}</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group full">
                <label class="form-label">请求头 (JSON，可选)</label>
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
          <p class="records-hint">仅展示任务「启动运行」产生的执行记录；保存配置不会产生新记录。</p>
          <div v-if="executionRecords.length === 0" class="records-empty">
            <p>暂无执行记录</p>
            <p class="records-empty-desc">点击「启动」运行任务后，每次结束会在此生成一条记录</p>
          </div>
          <div v-else class="timeline">
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
                <p v-if="record.summary" class="timeline-card-summary">{{ record.summary }}</p>
                <div class="timeline-card-time">{{ record.time }}</div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'preview'" class="tab-panel preview-panel">
          <div v-if="dataSummaryLoading && previewTableLoading" class="loading-state">
            <div class="spinner"></div>
            <span>加载中...</span>
          </div>
          <div v-else class="preview-layout">
            <aside class="preview-sidebar">
              <div class="side-stat-card">
                <p class="side-label">本次执行</p>
                <span class="side-status" :class="'status-' + (task.status || 'pending')">
                  <span class="status-dot"></span>
                  {{ statusLabel(task.status) }}
                </span>
                <div class="side-metrics">
                  <div class="side-metric">
                    <span class="side-metric-value">{{ previewTotalCount }}</span>
                    <span class="side-metric-label">采集条数</span>
                  </div>
                  <div class="side-metric">
                    <span class="side-metric-value">{{ Math.round(dataSummary?.success_rate || 0) }}%</span>
                    <span class="side-metric-label">成功率</span>
                  </div>
                  <div class="side-metric">
                    <span class="side-metric-value side-metric-sm">{{ formatDuration(dataSummary?.execution_time) }}</span>
                    <span class="side-metric-label">耗时</span>
                  </div>
                </div>
                <p v-if="dataSummary?.last_run_started_at" class="side-hint">
                  执行始于 {{ dataSummary.last_run_started_at }}
                </p>
                <p v-if="dataSummary?.last_collected_at" class="side-hint muted">
                  最近入库 {{ dataSummary.last_collected_at }}
                </p>
                <p v-if="dataSummary?.latest_only" class="side-scope">
                  仅展示本次执行采集的数据
                </p>
                <p v-if="task.error_message || dataSummary?.error_message" class="side-error" :title="task.error_message || dataSummary?.error_message">
                  {{ (task.error_message || dataSummary?.error_message || '').slice(0, 120) }}
                </p>
              </div>
              <button type="button" class="btn-refresh-preview" :disabled="previewTableLoading" @click="refreshPreview">
                {{ previewTableLoading ? '刷新中…' : '刷新数据' }}
              </button>
            </aside>

            <div class="preview-main">
              <div class="preview-table-header">
                <h3 class="preview-table-title">采集明细</h3>
                <span class="preview-table-meta">共 {{ previewTotal }} 条 · 第 {{ previewPage }} / {{ previewTotalPages }} 页</span>
              </div>
              <div class="preview-table-card" :class="{ 'is-refreshing': previewTableLoading }">
                <el-table
                  v-loading="previewTableLoading"
                  element-loading-custom-class="app-theme-loading"
                  :data="previewTableData"
                  :tooltip-options="tableTooltipOptions"
                  border
                  class="data-el-table task-preview-table"
                  style="width: 100%"
                  max-height="520"
                  empty-text="本次执行暂无采集数据，请先启动任务"
                >
                  <el-table-column prop="title" label="标题" min-width="140" show-overflow-tooltip />
                  <el-table-column prop="link" label="链接" min-width="160">
                    <template #default="{ row }">
                      <el-tooltip
                        v-if="row.link"
                        :content="row.link"
                        placement="top"
                        :show-after="400"
                        teleported
                        effect="dark"
                        popper-class="data-table-tooltip"
                      >
                        <a
                          :href="row.link"
                          target="_blank"
                          rel="noopener"
                          class="data-link data-link-ellipsis"
                          @click.stop
                        >{{ row.link }}</a>
                      </el-tooltip>
                      <span v-else class="text-muted">—</span>
                    </template>
                  </el-table-column>
                  <el-table-column label="图片" width="88" align="center">
                    <template #default="{ row }">
                      <div v-if="getPreviewImageUrl(row)" class="thumb-cell">
                        <el-image
                          :src="getPreviewImageUrl(row)"
                          :preview-src-list="[getPreviewImageUrl(row)]"
                          :preview-teleported="true"
                          fit="cover"
                          lazy
                          class="thumb-image"
                        >
                          <template #error><span class="img-error">—</span></template>
                        </el-image>
                      </div>
                      <span v-else class="text-muted">—</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="content" label="内容摘要" min-width="160" show-overflow-tooltip />
                  <el-table-column prop="type" label="类型" width="80" align="center">
                    <template #default="{ row }">
                      <span class="type-tag" :class="'tag-' + (row.type || 'link')">{{ previewTypeLabel(row.type) }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="collected_at" label="采集时间" width="168" />
                </el-table>
                <div v-if="previewTotal > 0" class="preview-pagination">
                  <el-pagination
                    v-model:current-page="previewPage"
                    v-model:page-size="previewPageSize"
                    :page-sizes="[10, 20, 50]"
                    :total="previewTotal"
                    layout="total, sizes, prev, pager, next"
                    background
                    @size-change="onPreviewSizeChange"
                    @current-change="fetchPreviewTable"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import NavBar from '../components/NavBar.vue'
import { taskAPI } from '../api/task'
import { proxyAPI } from '../api/proxy'
import { systemAPI } from '../api/system'
import { dataAPI } from '../api/data'
import {
  applyConfigToTaskDetailForm,
  buildTaskDetailConfig,
  parseTemplateConfig
} from '../utils/templateConfig'

const route = useRoute()
const activeTab = ref('info')
const editing = ref(false)
const autoScroll = ref(true)
const logViewerRef = ref(null)
const proxyGroups = ref([])

const task = ref({})

const tabs = [
  { key: 'info', label: '基础信息' },
  { key: 'logs', label: '运行日志' },
  { key: 'records', label: '执行记录' },
  { key: 'preview', label: '数据预览' }
]

const statusLabelMap = { running: '运行中', pending: '待执行', completed: '已完成', failed: '失败' }
function statusLabel(status) { return statusLabelMap[status] || status }

function formatDuration(seconds) {
  if (!seconds) return '0s'
  if (seconds >= 3600) return `${Math.floor(seconds/3600)}h ${Math.floor((seconds%3600)/60)}m`
  if (seconds >= 60) return `${Math.floor(seconds/60)}m ${seconds%60}s`
  return `${seconds}s`
}

const form = reactive({
  name: '',
  targetUrl: '',
  taskType: 'crawler',
  intervalMinutes: 30,
  concurrency: 1,
  intervalSeconds: 3,
  maxRetries: 3,
  retryInterval: 60,
  crawlMode: 'link',
  totalPages: 1,
  proxyGroup: '',
  headers: ''
})

const formBackup = ref(null)

function loadForm() {
  const config = parseTaskConfig(task.value.config)
  applyConfigToTaskDetailForm(form, task.value, config)
  formBackup.value = JSON.parse(JSON.stringify(form))
}

function cancelEdit() {
  if (formBackup.value) {
    Object.assign(form, formBackup.value)
  }
  editing.value = false
}

async function saveConfig() {
  if (!form.name.trim()) {
    ElMessage.warning('请输入任务名称')
    return
  }
  if (!form.targetUrl.trim()) {
    ElMessage.warning('请输入目标 URL')
    return
  }
  try {
    const config = buildTaskDetailConfig(form)
    const res = await taskAPI.updateTask(task.value.id, {
      name: form.name.trim(),
      config
    })
    if (res.data.success) {
      task.value.name = form.name.trim()
      task.value.target_url = config.target_url
      task.value.proxy_group = config.proxy_group
      task.value.config = config
      formBackup.value = JSON.parse(JSON.stringify(form))
      editing.value = false
      ElMessage.success('保存成功')
    } else {
      ElMessage.error(res.data.message || '保存失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '保存失败')
  }
}

const executionRecords = ref([])
const logs = ref([])
const logsLoading = ref(false)
const dataSummary = ref(null)
const dataSummaryLoading = ref(false)
const previewTableData = ref([])
const previewTableLoading = ref(false)
const previewPage = ref(1)
const previewPageSize = ref(20)
const previewTotal = ref(0)

const previewTotalPages = computed(() =>
  Math.max(1, Math.ceil(previewTotal.value / previewPageSize.value))
)
const previewTotalCount = computed(() =>
  dataSummary.value?.total_count ?? previewTotal.value ?? 0
)

const previewTypeLabels = { link: '链接', image: '图片', page: '页面', mixed: '混合' }
function previewTypeLabel(type) {
  return previewTypeLabels[type] || type || '—'
}

const tableTooltipOptions = {
  placement: 'top',
  teleported: true,
  effect: 'dark',
  popperClass: 'data-table-tooltip',
  showArrow: true,
}

function getPreviewImageUrl(row) {
  const url = (row.image_url || '').trim()
  if (url) return url
  if (row.type === 'image' && row.link) return row.link.trim()
  return ''
}

function parseTaskConfig(raw) {
  return parseTemplateConfig(raw)
}

async function fetchProxyGroups() {
  try {
    const res = await proxyAPI.getProxyGroups()
    if (res.data.success) {
      proxyGroups.value = res.data.data || []
    }
  } catch (e) {
    proxyGroups.value = []
  }
}

async function fetchTask() {
  const taskId = route.params.id
  if (!taskId || taskId === 'new' || taskId === 'undefined') {
    return
  }
  try {
    const res = await taskAPI.getTask(taskId)
    if (res.data.success) {
      const data = res.data.data
      if (typeof data.config === 'string') {
        data.config = parseTaskConfig(data.config)
      }
      const status = (data.status || 'pending').toLowerCase()
      task.value = {
        ...data,
        status: status === 'error' ? 'failed' : status,
        error_message: data.error_message || '',
      }
      loadForm()
      if (route.query.edit === '1') {
        editing.value = true
      }
    }
  } catch (e) {
    console.error('获取任务详情失败:', e)
    ElMessage.error('获取任务详情失败')
  }
}

function formatExecutionDuration(seconds) {
  const t = Number(seconds)
  if (Number.isNaN(t)) return 'N/A'
  if (t <= 0) return '0s'
  if (t >= 3600) {
    return `${Math.floor(t / 3600)}h ${Math.floor((t % 3600) / 60)}m`
  }
  if (t >= 60) {
    return `${Math.floor(t / 60)}m ${t % 60}s`
  }
  return `${t}s`
}

/** 仅解析真实「任务执行」产生的版本（过滤历史误写入的配置版本） */
function mapVersionToExecutionRecord(v, index, total) {
  const changeLog = v.change_log || ''
  let config = v.config || {}
  if (typeof config === 'string') {
    try {
      config = JSON.parse(config)
    } catch {
      config = {}
    }
  }
  const lastExec = config._last_execution || {}
  if (!/^执行结果:/i.test(changeLog.trim())) {
    return null
  }

  let status = 'completed'
  const rawStatus = (lastExec.status || '').toString().toUpperCase()
  if (rawStatus) {
    status = rawStatus === 'COMPLETED' ? 'completed' : 'failed'
  } else {
    const m = changeLog.match(/执行结果:\s*(\w+)/i)
    if (m) {
      status = m[1].toUpperCase() === 'COMPLETED' ? 'completed' : 'failed'
    }
  }

  let dataCount = Number(lastExec.data_count)
  if (Number.isNaN(dataCount)) dataCount = 0
  const dm = changeLog.match(/数据:\s*(\d+)\s*条/)
  if (dataCount === 0 && dm) {
    dataCount = parseInt(dm[1], 10) || 0
  }

  let duration = 'N/A'
  if (lastExec.execution_time !== undefined && lastExec.execution_time !== null) {
    duration = formatExecutionDuration(lastExec.execution_time)
  }

  const summary = changeLog || (lastExec.error_message ? String(lastExec.error_message).slice(0, 80) : '')

  return {
    id: v.id,
    version: v.version_index || (total - index),
    status,
    duration,
    dataCount,
    time: v.created_at || '',
    changeLog,
    summary,
  }
}

async function fetchExecutionRecords() {
  if (!route.params.id || route.params.id === 'new' || route.params.id === 'undefined') {
    return
  }
  try {
    const res = await taskAPI.getExecutions(route.params.id)
    if (res.data.success) {
      const versions = res.data.data || []
      executionRecords.value = versions
        .map((v, index) => mapVersionToExecutionRecord(v, index, versions.length))
        .filter(Boolean)
    }
  } catch (e) {
    console.error('获取执行记录失败:', e)
    executionRecords.value = []
  }
}

async function refreshLogs() {
  logsLoading.value = true
  try {
    // 传递 task_id 参数过滤任务相关日志
    const res = await systemAPI.getLogs({ task_id: route.params.id, limit: 200, page_size: 200 })
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

async function fetchDataSummary() {
  if (!route.params.id || route.params.id === 'new' || route.params.id === 'undefined') {
    return
  }
  dataSummaryLoading.value = true
  try {
    const res = await taskAPI.getDataSummary(route.params.id, { latest_only: 1 })
    if (res.data.success) {
      dataSummary.value = res.data.data
    }
  } catch (e) {
    console.error('获取数据概览失败:', e)
  } finally {
    dataSummaryLoading.value = false
  }
}

async function fetchPreviewTable() {
  const taskId = route.params.id
  if (!taskId || taskId === 'new' || taskId === 'undefined') return

  previewTableLoading.value = true
  try {
    const params = {
      task_id: taskId,
      page: previewPage.value,
      page_size: previewPageSize.value,
      sort_field: 'collected_at',
      sort_order: 'desc',
    }
    if (dataSummary.value?.since) {
      params.since = dataSummary.value.since
    }
    const res = await dataAPI.getDataList(params)
    if (res.data.success) {
      const data = res.data.data || {}
      previewTableData.value = data.list || []
      previewTotal.value = data.total ?? 0
      if (data.page) previewPage.value = data.page
    } else {
      previewTableData.value = []
      previewTotal.value = 0
    }
  } catch (e) {
    console.error('获取任务采集数据失败:', e)
    previewTableData.value = []
    previewTotal.value = 0
  } finally {
    previewTableLoading.value = false
  }
}

function onPreviewSizeChange() {
  previewPage.value = 1
  fetchPreviewTable()
}

async function refreshPreview() {
  await fetchDataSummary()
  previewPage.value = 1
  await fetchPreviewTable()
}

async function loadPreviewTab() {
  await fetchDataSummary()
  previewPage.value = 1
  await fetchPreviewTable()
}

onMounted(() => {
  fetchProxyGroups()
  fetchTask()
})

watch(() => route.params.id, (id, prevId) => {
  if (id && id !== prevId && id !== 'new' && id !== 'undefined') {
    editing.value = route.query.edit === '1'
    fetchTask()
    if (activeTab.value === 'logs') {
      refreshLogs()
    }
  }
})

watch(activeTab, (val) => {
  if (val === 'records') {
    fetchExecutionRecords()
  }
  if (val === 'logs') {
    refreshLogs()
    if (autoScroll.value) {
      nextTick(() => {
        if (logViewerRef.value) {
          logViewerRef.value.scrollTop = logViewerRef.value.scrollHeight
        }
      })
    }
  }
  if (val === 'preview') {
    loadPreviewTab()
  }
})
</script>

<style scoped>
.task-detail-page {
  min-height: 100vh;
  background-color: var(--bg-primary);
  background-image:
    linear-gradient(var(--border-color) 1px, transparent 1px),
    linear-gradient(90deg, var(--border-color) 1px, transparent 1px);
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
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.25s ease;
  flex-shrink: 0;
}

.btn-back:hover {
  color: var(--text-primary);
  border-color: var(--border-color);
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
  color: var(--text-primary);
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

.status-pending { background: var(--active-bg); color: var(--active-color); }
.status-pending .status-dot { background: var(--active-color); }
.status-completed { background: rgba(255, 255, 255, 0.05); color: var(--text-muted); }
.status-completed .status-dot { background: var(--text-muted); }
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
  background: var(--border-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-version:hover {
  color: var(--text-primary);
  background: var(--card-hover-bg);
  border-color: var(--border-color);
}

.btn-version svg {
  width: 14px;
  height: 14px;
}

.tab-nav {
  display: flex;
  gap: 4px;
  background: var(--bg-card);
  border-radius: 12px;
  padding: 5px;
  margin-bottom: 24px;
  border: 1px solid var(--border-color);
}

.tab-btn {
  flex: 1;
  padding: 11px 20px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-muted);
  background: transparent;
  border: none;
  border-radius: 9px;
  cursor: pointer;
  transition: all 0.25s ease;
}

.tab-btn:hover {
  color: var(--active-color);
  background: var(--active-bg);
}

.tab-btn.active {
  background: rgba(var(--accent-rgb), 0.15);
  color: var(--active-color);
  font-weight: 600;
}

.tab-panel {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
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
  color: var(--text-muted);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-input {
  width: 100%;
  padding: 11px 16px;
  font-size: 14px;
  background: var(--card-hover-bg);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  outline: none;
  transition: all 0.25s ease;
}

.form-input:focus {
  border-color: rgba(var(--accent-rgb), 0.4);
  box-shadow: 0 0 0 3px var(--glow-color);
}

.form-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

select.form-input {
  color-scheme: dark;
  cursor: pointer;
}

select.form-input option {
  background-color: #161b22;
  color: rgba(255, 255, 255, 0.92);
}

.form-textarea {
  width: 100%;
  padding: 11px 16px;
  font-size: 13px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  background: var(--card-hover-bg);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  outline: none;
  resize: vertical;
  transition: all 0.25s ease;
}

.form-textarea:focus {
  border-color: rgba(var(--accent-rgb), 0.4);
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
  border: 1px solid var(--border-color);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.25s ease;
  background: var(--border-color);
  color: var(--text-secondary);
}

.action-btn svg { width: 16px; height: 16px; }

.action-btn.primary {
  background: var(--gradient-primary);
  color: #fff;
  border: none;
  box-shadow: 0 4px 14px rgba(var(--accent-rgb), 0.3);
}

.action-btn.primary:hover { box-shadow: 0 6px 20px rgba(var(--accent-rgb), 0.45); transform: translateY(-1px); }

.action-btn.success {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border-color: rgba(16, 185, 129, 0.2);
}

.action-btn.success:hover { background: rgba(16, 185, 129, 0.22); }

.action-btn.cancel {
  background: var(--border-color);
  color: var(--text-secondary);
}

.action-btn.cancel:hover { background: var(--card-hover-bg); color: var(--text-primary); }

.log-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 14px;
  margin-bottom: 14px;
  border-bottom: 1px solid var(--border-color);
}

.auto-scroll-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-muted);
  cursor: pointer;
}

.auto-scroll-label input {
  accent-color: var(--accent-primary);
}

.btn-clear-log {
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 500;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.15);
  border-radius: 8px;
  color: var(--error-text, #f87171);
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
  background: var(--border-color);
  border-radius: 10px;
  padding: 16px;
}

.log-viewer::-webkit-scrollbar { width: 6px; }
.log-viewer::-webkit-scrollbar-track { background: transparent; }
.log-viewer::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 3px; }

.log-line {
  display: flex;
  gap: 10px;
}

.log-time {
  color: var(--text-muted);
  flex-shrink: 0;
}

.log-level {
  width: 50px;
  flex-shrink: 0;
  font-weight: 600;
}

.log-level.info { color: var(--active-color); }
.log-level.warn { color: var(--warning-text, #fbbf24); }
.log-level.error { color: var(--error-text, #f87171); }

.log-msg { color: var(--text-secondary); }

.log-msg :deep(.kw) { color: var(--active-color); }
.log-msg :deep(.err) { color: var(--error-text, #f87171); }

.log-line.error .log-msg { color: var(--error-text, #f87171); }
.log-line.warn .log-msg { color: var(--warning-text, #fbbf24); }

.log-empty {
  text-align: center;
  color: var(--text-muted);
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
  background: var(--border-color);
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
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
}

.timeline-dot.dot-completed {
  border-color: #34d399;
  background: #34d399;
  box-shadow: 0 0 8px rgba(52, 211, 153, 0.4);
}

.timeline-dot.dot-failed {
  border-color: var(--error-text, #f87171);
  background: var(--error-text, #f87171);
  box-shadow: 0 0 8px rgba(248, 113, 113, 0.4);
}

.timeline-card {
  background: var(--card-hover-bg);
  border: 1px solid var(--border-color);
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
  color: var(--text-primary);
}

.record-status {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 10px;
}

.record-status.status-completed { background: rgba(16, 185, 129, 0.12); color: #34d399; }
.record-status.status-failed { background: rgba(239, 68, 68, 0.12); color: var(--error-text, #f87171); }

.timeline-card-meta {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 6px;
}

.timeline-card-time {
  font-size: 11px;
  color: var(--text-muted);
}

.timeline-card-summary {
  margin-top: 8px;
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.4;
  word-break: break-word;
}

.records-hint {
  margin-bottom: 16px;
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
}

.records-empty {
  text-align: center;
  padding: 48px 20px;
  color: var(--text-muted);
}

.records-empty p {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.records-empty-desc {
  font-size: 13px;
  color: var(--text-muted);
}

.preview-panel {
  padding: 20px 24px 28px;
}

.preview-layout {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  min-height: 480px;
}

.preview-sidebar {
  flex: 0 0 200px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: sticky;
  top: 88px;
}

.side-stat-card {
  padding: 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
}

.side-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 10px;
}

.side-status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 14px;
}

.side-status .status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.side-status.status-running { background: rgba(16, 185, 129, 0.12); color: #34d399; }
.side-status.status-pending { background: rgba(var(--accent-rgb), 0.12); color: var(--accent-primary); }
.side-status.status-completed { background: var(--card-hover-bg); color: var(--text-secondary); }
.side-status.status-failed { background: rgba(239, 68, 68, 0.12); color: var(--error-text, #f87171); }

.side-metrics {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.side-metric {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.side-metric-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.side-metric-value.side-metric-sm {
  font-size: 15px;
  font-weight: 600;
}

.side-metric-label {
  font-size: 11px;
  color: var(--text-muted);
}

.side-hint {
  margin-top: 12px;
  font-size: 11px;
  color: var(--text-secondary);
  line-height: 1.45;
}

.side-hint.muted {
  color: var(--text-muted);
}

.side-scope {
  margin-top: 8px;
  font-size: 10px;
  color: var(--accent-primary);
  line-height: 1.4;
}

.side-error {
  margin-top: 10px;
  padding: 8px;
  font-size: 11px;
  line-height: 1.4;
  color: var(--error-text, #fca5a5);
  background: var(--error-bg, rgba(239, 68, 68, 0.1));
  border: 1px solid rgba(239, 68, 68, 0.25);
  border-radius: 8px;
  word-break: break-word;
}

.btn-refresh-preview {
  width: 100%;
  padding: 9px 12px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--border-color);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-refresh-preview:hover:not(:disabled) {
  color: var(--text-primary);
  border-color: rgba(var(--accent-rgb), 0.35);
}

.btn-refresh-preview:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.preview-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preview-table-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.preview-table-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.preview-table-meta {
  font-size: 12px;
  color: var(--text-muted);
}

.preview-table-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  overflow: visible;
  transition: opacity 0.2s ease;
}

.preview-table-card :deep(.el-table__inner-wrapper) {
  border-radius: 14px;
  overflow: hidden;
}

.preview-table-card.is-refreshing {
  opacity: 0.92;
}

.preview-pagination {
  display: flex;
  justify-content: center;
  padding: 16px;
  border-top: 1px solid var(--border-color);
}

.preview-pagination :deep(.el-pagination) {
  flex-wrap: wrap;
  justify-content: center;
}

/* 与数据预览页一致的表格样式 */
.task-preview-table.data-el-table {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: var(--border-color);
  --el-table-row-hover-bg-color: rgba(var(--accent-rgb), 0.08);
  --el-table-border-color: var(--border-color);
  --el-table-text-color: var(--text-secondary);
  --el-table-header-text-color: var(--text-muted);
  --el-fill-color-lighter: var(--border-color);
  --el-bg-color: transparent;
}

.task-preview-table.data-el-table :deep(.el-table__inner-wrapper),
.task-preview-table.data-el-table :deep(.el-table__body-wrapper),
.task-preview-table.data-el-table :deep(.el-table__header-wrapper) {
  background-color: transparent !important;
}

.task-preview-table.data-el-table :deep(.el-table__header th.el-table__cell) {
  background-color: var(--border-color) !important;
  color: var(--text-muted) !important;
  border-color: var(--border-color) !important;
}

.task-preview-table.data-el-table :deep(.el-table__body tr) {
  background-color: transparent !important;
}

.task-preview-table.data-el-table :deep(.el-table__body td.el-table__cell) {
  background-color: transparent !important;
  color: var(--text-secondary) !important;
  border-color: var(--border-color) !important;
}

.task-preview-table.data-el-table :deep(.el-table__body tr:hover > td.el-table__cell) {
  background-color: rgba(var(--accent-rgb), 0.1) !important;
}

.task-preview-table.data-el-table :deep(.el-table__body tr:hover > td.el-table__cell .cell) {
  color: var(--text-primary) !important;
}

.task-preview-table.data-el-table :deep(.el-table__body .cell) {
  color: var(--text-secondary);
}

.task-preview-table.data-el-table :deep(.el-table__empty-block) {
  background-color: transparent !important;
}

.thumb-cell {
  display: flex;
  justify-content: center;
  align-items: center;
}

.thumb-image {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  cursor: zoom-in;
}

.img-error {
  font-size: 11px;
  color: var(--text-muted);
}

.data-link {
  color: var(--accent-primary);
  text-decoration: none;
}

.data-link:hover {
  text-decoration: underline;
  color: var(--active-color);
}

.data-link-ellipsis {
  display: block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.5;
}

.task-preview-table.data-el-table :deep(.el-tooltip__trigger) {
  display: block;
  max-width: 100%;
  overflow: hidden;
}

.text-muted {
  color: var(--text-muted);
  font-size: 12px;
}

.type-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
}

.tag-link { background: rgba(var(--accent-rgb), 0.15); color: var(--active-color); }
.tag-image { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.tag-page { background: var(--card-hover-bg); color: var(--text-muted); }

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 60px;
  color: var(--text-muted);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 80px 20px;
}

.empty-icon {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  background: var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.empty-icon svg { width: 32px; height: 32px; }

.empty-text {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-secondary);
}

.empty-desc {
  font-size: 13px;
  color: var(--text-muted);
}

@media (max-width: 960px) {
  .preview-layout {
    flex-direction: column;
  }
  .preview-sidebar {
    flex: none;
    width: 100%;
    position: static;
    flex-direction: row;
    flex-wrap: wrap;
    align-items: stretch;
  }
  .side-stat-card {
    flex: 1;
    min-width: 200px;
  }
  .btn-refresh-preview {
    width: auto;
    flex: 0 0 auto;
    align-self: center;
    padding: 9px 20px;
  }
}

@media (max-width: 768px) {
  .detail-content { padding: 24px 16px 64px; }
  .detail-title { font-size: 20px; }
  .form-row { grid-template-columns: 1fr; }
  .tab-nav { overflow-x: auto; }
  .preview-panel { padding: 16px; }
}
</style>