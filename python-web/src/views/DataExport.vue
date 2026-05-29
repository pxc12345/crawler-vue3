<template>
  <div class="page">
    <NavBar />
    <div class="content">
      <div class="page-header">
        <h1 class="page-title">数据导出</h1>
      </div>

      <div class="card">
        <h3 class="section-title">导出格式</h3>
        <div class="format-cards">
          <div class="format-card" :class="{ active: exportFormat === 'csv' }" @click="exportFormat = 'csv'">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
            <span class="format-label">CSV</span>
            <span class="format-desc">通用表格格式</span>
          </div>
          <div class="format-card" :class="{ active: exportFormat === 'excel' }" @click="exportFormat = 'excel'">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
            <span class="format-label">Excel</span>
            <span class="format-desc">Microsoft Excel</span>
          </div>
          <div class="format-card" :class="{ active: exportFormat === 'json' }" @click="exportFormat = 'json'">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><path d="M10 12a2 2 0 0 1 4 0v4a2 2 0 0 1-4 0z"/></svg>
            <span class="format-label">JSON</span>
            <span class="format-desc">结构化数据</span>
          </div>
        </div>
      </div>

      <div class="card">
        <h3 class="section-title">选择导出字段</h3>
        <div class="field-checks">
          <label v-for="field in availFields" :key="field.key" class="field-check">
            <input type="checkbox" v-model="field.selected" />
            <span>{{ field.label }}</span>
          </label>
        </div>
      </div>

      <div class="card">
        <h3 class="section-title">筛选条件（可选）</h3>
        <div class="filter-row">
          <div class="filter-group">
            <label class="filter-label">日期范围</label>
            <div class="date-row">
              <input type="date" v-model="dateFrom" class="input" />
              <span class="sep">至</span>
              <input type="date" v-model="dateTo" class="input" />
            </div>
          </div>
          <div class="filter-group">
            <label class="filter-label">关联任务</label>
            <select v-model="taskFilter" class="input input-select">
              <option value="">全部任务</option>
              <option v-for="t in taskOptions" :key="t.id" :value="t.id">{{ t.name }}</option>
            </select>
          </div>
        </div>
      </div>

      <div class="card">
        <h3 class="section-title">预览 (前5条)</h3>
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th v-for="f in selectedFields" :key="f">{{ f }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in previewRows" :key="idx">
                <td v-for="f in selectedFields" :key="f">{{ row[f] }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card collapsible">
        <div class="collapse-header" @click="autoWriteOpen = !autoWriteOpen">
          <div class="collapse-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
            自动入库配置
          </div>
          <svg class="collapse-arrow" :class="{ rotated: autoWriteOpen }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
        </div>
        <div v-if="autoWriteOpen" class="collapse-body">
          <div class="db-config">
            <div class="config-row">
              <div class="config-group">
                <label class="filter-label">数据库类型</label>
                <select v-model="dbType" class="input input-select">
                  <option value="mysql">MySQL</option>
                  <option value="postgresql">PostgreSQL</option>
                </select>
              </div>
              <div class="config-group">
                <label class="filter-label">主机地址</label>
                <input v-model="dbHost" class="input" placeholder="localhost" />
              </div>
              <div class="config-group">
                <label class="filter-label">端口</label>
                <input v-model="dbPort" class="input" placeholder="3306" />
              </div>
            </div>
            <div class="config-row">
              <div class="config-group">
                <label class="filter-label">用户名</label>
                <input v-model="dbUser" class="input" placeholder="root" />
              </div>
              <div class="config-group">
                <label class="filter-label">密码</label>
                <input v-model="dbPass" type="password" class="input" placeholder="••••••" />
              </div>
              <div class="config-group">
                <label class="filter-label">数据库名</label>
                <input v-model="dbName" class="input" placeholder="crawler_data" />
              </div>
            </div>
            <div class="config-row">
              <div class="config-group">
                <label class="filter-label">目标表名</label>
                <input v-model="dbTable" class="input" placeholder="collected_data" />
              </div>
              <div class="config-group" style="align-self: flex-end;">
                <button class="btn-test" @click="testConnection">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                  测试连接
                </button>
              </div>
            </div>
            <label class="toggle-row">
              <input type="checkbox" v-model="autoWriteEnabled" />
              <span>启用自动入库</span>
            </label>
            <button type="button" class="btn-test" style="margin-top:12px" @click="saveAutoWrite">保存自动入库配置</button>
          </div>
        </div>
      </div>

      <div class="card collapsible">
        <div class="collapse-header" @click="pushOpen = !pushOpen">
          <div class="collapse-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
            推送配置
          </div>
          <svg class="collapse-arrow" :class="{ rotated: pushOpen }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
        </div>
        <div v-if="pushOpen" class="collapse-body">
          <h4 class="push-subtitle">推送方式</h4>
          <div class="field-checks">
            <label class="field-check">
              <input type="checkbox" v-model="pushEmail" />
              <span>邮件推送</span>
            </label>
            <label class="field-check">
              <input type="checkbox" v-model="pushWechat" />
              <span>企业微信</span>
            </label>
          </div>
          <div v-if="pushEmail" class="push-config">
            <h4 class="push-subtitle">邮件配置</h4>
            <div class="config-group">
              <label class="filter-label">接收邮箱</label>
              <input v-model="emailRecipient" class="input" placeholder="admin@example.com" />
            </div>
            <div class="config-group">
              <label class="filter-label">邮件模板预览</label>
              <div class="email-preview">
                <div class="email-preview-header">主题: {{ emailSubject }}</div>
                <div class="email-preview-body">
                  <p>您好，</p>
                  <p>本次数据导出已完成，共导出 <strong>{{ previewRows.length }}</strong> 条记录。</p>
                  <p>导出格式: <strong>{{ exportFormat.toUpperCase() }}</strong></p>
                  <p>导出时间: {{ new Date().toLocaleString('zh-CN') }}</p>
                  <p style="margin-top:12px">此邮件由系统自动发送，请勿回复。</p>
                </div>
              </div>
            </div>
          </div>
          <div v-if="pushWechat" class="push-config">
            <h4 class="push-subtitle">企业微信配置</h4>
            <div class="config-group">
              <label class="filter-label">Webhook URL</label>
              <input v-model="wechatWebhook" class="input" placeholder="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=..." />
            </div>
          </div>
          <div v-if="pushEmail || pushWechat" class="push-config">
            <h4 class="push-subtitle">推送触发条件</h4>
            <div class="field-checks">
              <label class="field-check">
                <input type="checkbox" v-model="pushAfterCrawl" />
                <span>每次爬取完成后推送</span>
              </label>
              <label class="field-check">
                <input type="checkbox" v-model="pushDaily" />
                <span>每日汇总推送</span>
              </label>
            </div>
          </div>
          <button type="button" class="btn-test" style="margin-top:12px" @click="savePush">保存推送配置</button>
        </div>
      </div>

      <div class="export-action">
        <button class="btn-export-main" @click="doExport" :disabled="exporting">
          <svg v-if="!exporting" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          <svg v-else class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
          {{ exporting ? '导出中...' : `导出 ${exportFormat.toUpperCase()}` }}
        </button>
      </div>

      <div v-if="exportSuccess" class="card success-card">
        <div class="success-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        </div>
        <p class="success-text">导出成功！</p>
        <p class="success-desc">文件已准备就绪，点击下方链接下载</p>
        <a href="#" class="download-link" @click.prevent="triggerDownload">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          下载 exported_data.{{ exportFormat }}
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { dataAPI } from '../api/data'
import { taskAPI } from '../api/task'
import NavBar from '../components/NavBar.vue'

const exportFormat = ref('csv')
const exporting = ref(false)
const exportSuccess = ref(false)

const dateFrom = ref('')
const dateTo = ref('')
const taskFilter = ref('')

const autoWriteOpen = ref(false)
const pushOpen = ref(false)

const dbType = ref('mysql')
const dbHost = ref('localhost')
const dbPort = ref('3306')
const dbUser = ref('')
const dbPass = ref('')
const dbName = ref('')
const dbTable = ref('collected_data')
const autoWriteEnabled = ref(false)

const pushEmail = ref(false)
const pushWechat = ref(false)
const emailRecipient = ref('')
const wechatWebhook = ref('')
const pushAfterCrawl = ref(false)
const pushDaily = ref(false)

const availFields = ref([
  { key: 'title', label: '标题', selected: true },
  { key: 'link', label: '链接', selected: true },
  { key: 'content', label: '内容', selected: true },
  { key: 'source_url', label: '来源URL', selected: false },
  { key: 'type', label: '类型', selected: false },
  { key: 'page_number', label: '页码', selected: false },
  { key: 'collected_at', label: '采集时间', selected: true }
])

const taskOptions = ref([])

const previewData = ref([])

const selectedFields = computed(() => availFields.value.filter(f => f.selected).map(f => f.key))

const previewRows = computed(() => {
  return previewData.value.slice(0, 5).map(row => {
    const r = {}
    selectedFields.value.forEach(k => { r[k] = row[k] || '-' })
    return r
  })
})

const emailSubject = computed(() => `[CrawlMaster] 数据导出报告 - ${new Date().toLocaleDateString('zh-CN')}`)

function autoWritePayload(testOnly = false) {
  return {
    test_only: testOnly,
    db_type: dbType.value,
    target_type: dbType.value,
    host: dbHost.value,
    port: dbPort.value,
    user: dbUser.value,
    password: dbPass.value,
    database: dbName.value,
    table: dbTable.value,
    auto_write: autoWriteEnabled.value
  }
}

async function testConnection() {
  try {
    const res = await dataAPI.autoWriteConfig(autoWritePayload(true))
    if (res.data.success) {
      ElMessage.success('数据库连接测试成功')
    } else {
      ElMessage.error(res.data.message || '数据库连接测试失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '数据库连接测试失败')
  }
}

async function saveAutoWrite() {
  try {
    const res = await dataAPI.autoWriteConfig(autoWritePayload(false))
    if (res.data.success) {
      ElMessage.success('自动入库配置已保存')
    } else {
      ElMessage.error(res.data.message || '保存失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '保存失败')
  }
}

async function savePush() {
  try {
    const res = await dataAPI.pushConfig({
      push_email: pushEmail.value,
      push_wechat: pushWechat.value,
      email_recipient: emailRecipient.value,
      wechat_webhook: wechatWebhook.value,
      push_after_crawl: pushAfterCrawl.value,
      push_daily: pushDaily.value
    })
    if (res.data.success) {
      ElMessage.success('推送配置已保存')
    } else {
      ElMessage.error(res.data.message || '保存失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '保存失败')
  }
}

async function doExport() {
  exporting.value = true
  exportSuccess.value = false
  try {
    const { downloadFile } = await import('../api/index')
    const fields = selectedFields.value.join(',')
    const params = new URLSearchParams({ fields, format: exportFormat.value })
    if (dateFrom.value) params.set('date_from', dateFrom.value)
    if (dateTo.value) params.set('date_to', dateTo.value)
    if (taskFilter.value) params.set('task_id', String(taskFilter.value))
    await downloadFile('/data/export?' + params.toString(), `exported_data.${exportFormat.value}`, exportFormat.value)
    exporting.value = false
    exportSuccess.value = true
    ElMessage.success('数据导出成功')
  } catch (error) {
    exporting.value = false
    ElMessage.error('导出失败，请重试')
  }
}

function triggerDownload() {
  if (exportSuccess.value) {
    doExport()
  }
}

onMounted(async () => {
  try {
    const res = await dataAPI.getDataList({ page_size: 5 })
    if (res.data.success) {
      previewData.value = res.data.data?.list || res.data.data || []
    }
  } catch (error) {
    previewData.value = []
  }
  try {
    const tRes = await taskAPI.getTasks({ page_size: 100 })
    if (tRes.data.success) {
      const list = tRes.data.data?.list || tRes.data.data || []
      taskOptions.value = list.map(t => ({ id: t.id, name: t.name || `任务 ${t.id}` }))
    }
  } catch (error) {
    taskOptions.value = []
  }
  try {
    const cfg = await dataAPI.getAutoWriteConfig()
    if (cfg.data.success && cfg.data.data?.target_config) {
      const c = cfg.data.data.target_config
      dbType.value = c.db_type || cfg.data.data.target_type || 'mysql'
      dbHost.value = c.host || 'localhost'
      dbPort.value = String(c.port || '3306')
      dbUser.value = c.user || ''
      dbPass.value = c.password || ''
      dbName.value = c.database || ''
      dbTable.value = c.table || 'collected_data'
      autoWriteEnabled.value = !!cfg.data.data.enabled
    }
  } catch (error) {
    /* ignore */
  }
  try {
    const pCfg = await dataAPI.getPushConfig()
    if (pCfg.data.success && pCfg.data.data?.push_config) {
      const c = pCfg.data.data.push_config
      pushEmail.value = !!c.push_email
      pushWechat.value = !!c.push_wechat
      emailRecipient.value = c.email || ''
      wechatWebhook.value = c.wechat_webhook || ''
      pushAfterCrawl.value = !!c.push_after_crawl
      pushDaily.value = !!c.push_daily
    }
  } catch (error) {
    /* ignore */
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
  max-width: 960px;
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
.card {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px; margin-bottom: 20px;
}
.section-title {
  font-size: 15px; font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 16px;
}
.format-cards { display: flex; gap: 16px; }
.format-card {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 8px;
  padding: 20px 16px; background: rgba(255,255,255,0.03);
  border: 1px solid var(--border-color); border-radius: 14px;
  cursor: pointer; transition: all 0.25s ease; color: var(--text-muted);
}
.format-card:hover { border-color: rgba(var(--accent-rgb), 0.2); color: var(--text-secondary); }
.format-card.active {
  background: rgba(var(--accent-rgb), 0.1); border-color: rgba(var(--accent-rgb), 0.3); color: var(--accent-primary);
  box-shadow: 0 0 20px rgba(var(--accent-rgb), 0.1);
}
.format-card svg { width: 28px; height: 28px; }
.format-label { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.format-desc { font-size: 11px; color: inherit; opacity: 0.6; }
.field-checks { display: flex; flex-wrap: wrap; gap: 12px; }
.field-check {
  display: flex; align-items: center; gap: 6px;
  padding: 7px 14px; background: rgba(255,255,255,0.03);
  border: 1px solid var(--border-color); border-radius: 8px;
  font-size: 13px; color: var(--text-secondary); cursor: pointer;
  transition: all 0.2s ease;
}
.field-check:hover { border-color: rgba(var(--accent-rgb), 0.2); color: var(--text-primary); }
.field-check input { accent-color: var(--accent-primary); }
.filter-row { display: flex; gap: 24px; flex-wrap: wrap; }
.filter-group { flex: 1; min-width: 200px; }
.filter-label {
  display: block; font-size: 12px; font-weight: 500;
  color: var(--text-muted); margin-bottom: 6px;
}
.date-row { display: flex; align-items: center; gap: 8px; }
.sep { font-size: 12px; color: var(--text-muted); }
.input {
  width: 100%; padding: 9px 14px; font-size: 13px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-color);
  border-radius: 8px; color: var(--text-primary);
  outline: none; transition: all 0.2s ease; box-sizing: border-box;
}
.input:focus { border-color: rgba(var(--accent-rgb), 0.4); background: rgba(255, 255, 255, 0.06); }
.input-select { cursor: pointer; color-scheme: dark; }
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.data-table th {
  padding: 10px 12px; text-align: left; font-weight: 600;
  color: var(--text-muted); font-size: 10px; text-transform: uppercase;
  letter-spacing: 0.4px; border-bottom: 1px solid var(--border-color);
  white-space: nowrap; background: var(--border-color);
}
.data-table td {
  padding: 10px 12px; color: var(--text-secondary);
  border-bottom: 1px solid var(--border-color);
  max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.data-table tbody tr:hover { background: rgba(var(--accent-rgb), 0.04); }
.collapse-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 18px 24px; cursor: pointer; user-select: none;
  transition: background 0.2s ease;
}
.collapse-header:hover { background: var(--card-hover-bg); }
.collapse-title {
  display: flex; align-items: center; gap: 10px;
  font-size: 14px; font-weight: 600; color: var(--text-secondary);
}
.collapse-title svg { width: 18px; height: 18px; color: var(--accent-primary); }
.collapse-arrow {
  width: 18px; height: 18px; color: var(--text-muted);
  transition: transform 0.25s ease;
}
.collapse-arrow.rotated { transform: rotate(180deg); }
.collapse-body { padding: 0 24px 24px; border-top: 1px solid var(--border-color); }
.db-config { padding-top: 16px; }
.config-row { display: flex; gap: 14px; margin-bottom: 12px; flex-wrap: wrap; }
.config-group { flex: 1; min-width: 140px; }
.btn-test {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 9px 16px; font-size: 12px; font-weight: 600;
  background: rgba(var(--accent-rgb), 0.1); border: 1px solid rgba(var(--accent-rgb), 0.2);
  border-radius: 8px; color: var(--accent-primary); cursor: pointer;
  transition: all 0.2s ease; white-space: nowrap;
}
.btn-test:hover { background: rgba(var(--accent-rgb), 0.2); }
.btn-test svg { width: 14px; height: 14px; }
.toggle-row {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; color: var(--text-secondary); cursor: pointer;
  padding-top: 8px;
}
.toggle-row input { accent-color: var(--accent-primary); }
.push-subtitle {
  font-size: 13px; font-weight: 600; color: var(--text-secondary);
  margin-bottom: 10px;
}
.push-config { margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border-color); }
.email-preview {
  margin-top: 8px; padding: 16px;
  background: var(--border-color); border: 1px solid var(--border-color);
  border-radius: 10px; font-size: 13px; color: var(--text-secondary);
  line-height: 1.6;
}
.email-preview-header {
  padding-bottom: 10px; margin-bottom: 10px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-secondary); font-weight: 500;
}
.email-preview-body { font-size: 12px; color: var(--text-secondary); }
.email-preview-body p { margin: 6px 0; }
.export-action { text-align: center; margin-top: 28px; }
.btn-export-main {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 14px 40px; font-size: 15px; font-weight: 700;
  background: var(--gradient-primary);
  border: none; border-radius: 12px; color: #fff; cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(var(--accent-rgb), 0.35);
}
.btn-export-main:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(var(--accent-rgb), 0.5); }
.btn-export-main:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-export-main svg { width: 20px; height: 20px; }
.spinner { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.success-card { text-align: center; padding: 32px; }
.success-icon {
  width: 64px; height: 64px; margin: 0 auto 16px;
  border-radius: 50%; background: rgba(16,185,129,0.12);
  display: flex; align-items: center; justify-content: center;
  color: #34d399;
}
.success-icon svg { width: 32px; height: 32px; }
.success-text { font-size: 18px; font-weight: 700; color: #34d399; margin-bottom: 6px; }
.success-desc { font-size: 13px; color: var(--text-muted); margin-bottom: 16px; }
.download-link {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 10px 22px; font-size: 13px; font-weight: 600;
  background: rgba(var(--accent-rgb), 0.12); border: 1px solid rgba(var(--accent-rgb), 0.2);
  border-radius: 10px; color: var(--accent-primary); text-decoration: none;
  transition: all 0.2s ease;
}
.download-link:hover { background: rgba(var(--accent-rgb), 0.2); }
.download-link svg { width: 16px; height: 16px; }

@media (max-width: 768px) {
  .content { padding: 24px 16px 64px; }
  .page-title { font-size: 22px; }
  .format-cards { flex-direction: column; }
  .config-row { flex-direction: column; gap: 8px; }
}
@media (max-width: 560px) {
  .filter-row { flex-direction: column; }
  .field-checks { gap: 8px; }
}
</style>