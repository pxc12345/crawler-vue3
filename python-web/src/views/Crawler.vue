<template>
  <div>
    <NavBar />

    <div class="home-container">
      <el-card class="control-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span class="card-header-title">爬虫任务控制台</span>
            <el-tag
              :type="statusTagType"
              size="large"
              effect="dark"
              round
            >
              {{ statusLabel }}
            </el-tag>
          </div>
        </template>

        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="目标网址">
              <el-input
                v-model="targetUrl"
                placeholder="请输入网址，如 https://example.com"
                :disabled="isRunning"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :xs="12" :sm="6" :md="4">
            <el-form-item label="爬取页数">
              <el-input-number
                v-model="totalPages"
                :min="1"
                :max="100"
                :disabled="isRunning"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="12" :sm="6" :md="4">
            <el-form-item label="请求间隔(秒)">
              <el-input-number
                v-model="intervalSeconds"
                :min="1"
                :max="60"
                :disabled="isRunning"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="12" :sm="6" :md="4">
            <el-form-item label="爬取模式">
              <el-select
                v-model="crawlMode"
                :disabled="isRunning"
                style="width: 100%"
              >
                <el-option label="只爬链接" value="link" />
                <el-option label="只爬图片" value="image" />
                <el-option label="链接+图片" value="mixed" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="操作">
              <div class="button-group">
                <el-button
                  type="primary"
                  :icon="VideoPlay"
                  :loading="startingLoading"
                  :disabled="isRunning"
                  @click="handleStart"
                >
                  开始爬取
                </el-button>
                <el-button
                  type="danger"
                  :icon="VideoPause"
                  :disabled="!isRunning"
                  @click="handleStop"
                >
                  停止爬取
                </el-button>
                <el-button
                  type="warning"
                  :icon="Delete"
                  :disabled="isRunning"
                  @click="handleClear"
                >
                  清空数据
                </el-button>
                <el-button
                  type="success"
                  :icon="Download"
                  :disabled="isRunning"
                  @click="handleExport"
                >
                  导出数据
                </el-button>
              </div>
            </el-form-item>
          </el-col>
        </el-row>
      </el-card>

      <el-card class="status-card" shadow="never">
        <template #header>
          <span>运行状态</span>
        </template>
        <el-row :gutter="24">
          <el-col :xs="12" :sm="6">
            <el-statistic title="运行状态" :value="statusLabel" />
          </el-col>
          <el-col :xs="12" :sm="6">
            <el-statistic title="已采集条数" :value="crawlerStatus.collected_count" />
          </el-col>
          <el-col :xs="12" :sm="6">
            <el-statistic title="当前/总页数" :value="`${crawlerStatus.current_page} / ${crawlerStatus.total_pages}`" />
          </el-col>
          <el-col :xs="12" :sm="6">
            <el-statistic title="运行耗时(秒)" :value="crawlerStatus.elapsed_seconds" />
          </el-col>
        </el-row>
        <el-progress
          v-if="isRunning"
          :percentage="progressPercent"
          :status="progressStatus"
          :stroke-width="18"
          style="margin-top: 20px"
        />
        <el-alert
          v-if="crawlerStatus.error_message"
          :title="crawlerStatus.error_message"
          type="error"
          show-icon
          :closable="false"
          style="margin-top: 16px"
        />
      </el-card>

      <el-card class="data-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>爬取数据列表</span>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索标题或内容"
              clearable
              style="width: 260px"
              @keyup.enter="loadData"
              @clear="loadData"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
        </template>

        <el-table
          v-loading="tableLoading"
          :data="tableData"
          stripe
          border
          style="width: 100%"
          max-height="500"
        >
          <el-table-column type="index" label="序号" width="60" fixed />
          <el-table-column prop="title" label="标题" min-width="150" show-overflow-tooltip />
          <el-table-column label="图片预览" width="120" align="center">
            <template #default="{ row }">
              <div v-if="row.image_url" class="image-preview">
                <el-image
                  :src="row.image_url"
                  :preview-src-list="[row.image_url]"
                  fit="contain"
                  class="preview-image"
                />
              </div>
              <span v-else class="no-image">暂无图片</span>
            </template>
          </el-table-column>
          <el-table-column prop="link" label="链接/图片地址" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">
              <a :href="row.link" target="_blank" class="data-link">{{ row.link }}</a>
            </template>
          </el-table-column>
          <el-table-column prop="content" label="内容摘要" min-width="200" show-overflow-tooltip />
          <el-table-column prop="source_url" label="来源网址" min-width="150" show-overflow-tooltip />
          <el-table-column prop="type" label="类型" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="getTypeTagType(row.type)" size="small">
                {{ getTypeLabel(row.type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="page_number" label="页码" width="60" align="center" />
          <el-table-column prop="collected_at" label="采集时间" width="160" />
        </el-table>

        <div class="pagination-wrapper">
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
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VideoPlay, VideoPause, Delete, Download, Search } from '@element-plus/icons-vue'
import { crawlerAPI } from '../api/crawler'
import NavBar from '../components/NavBar.vue'

const targetUrl = ref('')
const totalPages = ref(1)
const intervalSeconds = ref(3)
const crawlMode = ref('image')  // 默认混合模式（同时爬取链接和图片）
const startingLoading = ref(false)
const isRunning = ref(false)
const searchKeyword = ref('')
const tableData = ref([])
const tableLoading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)
let statusTimer = null

const crawlerStatus = reactive({
  status: 'idle',
  collected_count: 0,
  current_page: 0,
  total_pages: 0,
  elapsed_seconds: 0,
  error_message: ''
})

const statusLabel = computed(() => {
  const map = {
    idle: '空闲',
    running: '运行中',
    stopping: '停止中',
    stopped: '已停止',
    completed: '已完成',
    error: '异常'
  }
  return map[crawlerStatus.status] || crawlerStatus.status
})

const statusTagType = computed(() => {
  const map = {
    idle: 'info',
    running: 'success',
    stopping: 'warning',
    stopped: 'warning',
    completed: 'success',
    error: 'danger'
  }
  return map[crawlerStatus.status] || 'info'
})

const progressPercent = computed(() => {
  if (crawlerStatus.total_pages === 0) return 0
  return Math.round((crawlerStatus.current_page / crawlerStatus.total_pages) * 100)
})

const progressStatus = computed(() => {
  if (crawlerStatus.status === 'error') return 'exception'
  if (crawlerStatus.status === 'completed') return 'success'
  return ''
})

function getTypeLabel(type) {
  const map = {
    link: '链接',
    image: '图片',
    page: '页面',
    mixed: '混合'
  }
  return map[type] || type
}

function getTypeTagType(type) {
  const map = {
    link: 'primary',
    image: 'success',
    page: 'info',
    mixed: 'warning'
  }
  return map[type] || 'info'
}

async function fetchStatus() {
  try {
    const res = await crawlerAPI.getStatus()
    if (res.data.success) {
      Object.assign(crawlerStatus, res.data.data)
      const running = res.data.data.status === 'running' || res.data.data.status === 'stopping'
      if (isRunning.value && !running) {
        ElMessage.success(res.data.data.status === 'completed' ? '爬取任务已完成' : '爬取任务已停止')
      }
      isRunning.value = running
    }
  } catch {
    // 静默处理状态轮询异常
  }
}

function startStatusPolling() {
  stopStatusPolling()
  statusTimer = setInterval(fetchStatus, 1500)
}

function stopStatusPolling() {
  if (statusTimer) {
    clearInterval(statusTimer)
    statusTimer = null
  }
}

async function handleStart() {
  if (!targetUrl.value.trim()) {
    ElMessage.warning('请输入目标网址')
    return
  }
  if (!targetUrl.value.startsWith('http://') && !targetUrl.value.startsWith('https://')) {
    ElMessage.warning('请输入有效的网址（以 http:// 或 https:// 开头）')
    return
  }

  startingLoading.value = true
  try {
    const res = await crawlerAPI.start({
      target_url: targetUrl.value.trim(),
      total_pages: totalPages.value,
      interval_seconds: intervalSeconds.value,
      crawl_mode: crawlMode.value
    })
    if (res.data.success) {
      ElMessage.success(res.data.message)
      isRunning.value = true
      crawlerStatus.status = 'running'
      crawlerStatus.error_message = ''
      startStatusPolling()
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '启动爬虫失败，请检查网络连接')
  } finally {
    startingLoading.value = false
  }
}

async function handleStop() {
  try {
    const res = await crawlerAPI.stop()
    if (res.data.success) {
      ElMessage.info(res.data.message)
    } else {
      ElMessage.warning(res.data.message)
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '停止爬虫失败')
  }
}

async function handleClear() {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有爬取数据吗？此操作不可恢复！',
      '确认清空',
      {
        confirmButtonText: '确定清空',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    const res = await crawlerAPI.clearData()
    if (res.data.success) {
      ElMessage.success(res.data.message)
      tableData.value = []
      totalCount.value = 0
      currentPage.value = 1
      crawlerStatus.collected_count = 0
    } else {
      ElMessage.error(res.data.message)
    }
  } catch {
    // 用户取消操作
  }
}

function handleExport() {
  const exportUrl = crawlerAPI.getExportUrl()
  const a = document.createElement('a')
  a.href = exportUrl
  a.download = 'crawler_data_export.csv'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  ElMessage.success('数据导出请求已发送')
}

async function loadData() {
  tableLoading.value = true
  try {
    const res = await crawlerAPI.getDataList({
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: searchKeyword.value
    })
    if (res.data.success) {
      tableData.value = res.data.data.list
      totalCount.value = res.data.data.total
    } else {
      ElMessage.error(res.data.message)
      tableData.value = []
      totalCount.value = 0
    }
  } catch {
    ElMessage.error('加载数据失败，请检查网络连接')
    tableData.value = []
    totalCount.value = 0
  } finally {
    tableLoading.value = false
  }
}

function handlePageChange() {
  loadData()
}

function handleSizeChange() {
  currentPage.value = 1
  loadData()
}

onMounted(async () => {
  await fetchStatus()
  if (crawlerStatus.status === 'running' || crawlerStatus.status === 'stopping') {
    startStatusPolling()
  }
  loadData()
})

onUnmounted(() => {
  stopStatusPolling()
})
</script>

<style scoped>
.home-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px 20px 40px;
}

.control-card {
  margin-bottom: 20px;
}

.status-card {
  margin-bottom: 20px;
}

.data-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--gray-800);
}

.button-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--gray-200);
}

.data-link {
  color: var(--primary-600);
  text-decoration: none;
  font-size: 13px;
}

.data-link:hover {
  text-decoration: underline;
}

.image-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 80px;
}

.preview-image {
  max-width: 100px;
  max-height: 80px;
  object-fit: contain;
  border-radius: 4px;
  cursor: pointer;
}

.preview-image:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.no-image {
  color: var(--gray-400);
  font-size: 12px;
}
</style>