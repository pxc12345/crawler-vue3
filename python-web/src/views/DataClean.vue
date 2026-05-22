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
            <span class="preview-count">{{ previewData.length }} 条</span>
          </h3>
          <div class="table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>标题</th>
                  <th>链接</th>
                  <th>内容</th>
                  <th>来源</th>
                  <th>采集时间</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, idx) in previewData" :key="idx">
                  <td class="td-idx">{{ idx + 1 }}</td>
                  <td class="td-title">{{ row.title || '-' }}</td>
                  <td class="td-link">{{ row.link || '-' }}</td>
                  <td class="td-content">{{ (row.content || '-').slice(0, 30) }}{{ row.content && row.content.length > 30 ? '...' : '' }}</td>
                  <td class="td-source">{{ row.source_url || '-' }}</td>
                  <td class="td-time">{{ row.collected_at || '-' }}</td>
                </tr>
                <tr v-if="previewData.length === 0">
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
import { ref, reactive, onMounted } from 'vue'
import NavBar from '../components/NavBar.vue'

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

const mockData = [
  { title: '智能手机市场分析报告', link: 'https://example.com/report/phones', content: '2024年全球智能手机出货量同比增长6.5%', source_url: 'https://research.example.com', collected_at: '2024-06-15 14:30:22' },
  { title: '智能手机市场分析报告', link: 'https://example.com/report/phones', content: '2024年全球智能手机出货量同比增长6.5%', source_url: 'https://research.example.com', collected_at: '2024-06-15 14:30:22' },
  { title: '新能源汽车政策解读', link: 'https://example.com/news/ev', content: '财政部发布最新新能源汽车补贴方案', source_url: 'https://gov.example.com', collected_at: '2024-06-15 13:22:10' },
  { title: '', link: 'https://cdn.example.com/img/logo.png', content: '', source_url: 'https://brands.example.com', collected_at: '2024-06-15 12:08:45' },
  { title: 'PyTorch 2.4正式发布', link: 'https://example.com/tech/pytorch', content: 'PyTorch 2.4版本带来全新优化', source_url: 'https://dev.example.com', collected_at: '2024-06-15 11:44:33' },
  { title: '长三角房价走势', link: 'https://example.com/data/housing', content: '四城新建商品住宅价格指数环比上涨', source_url: 'https://stats.example.com', collected_at: '2024-06-15 10:15:00' },
  { title: '', link: '', content: '数据缺失的行', source_url: 'https://unknown.example.com', collected_at: '2024-06-15 09:30:12' },
  { title: 'AI大模型实践白皮书', link: 'https://example.com/reports/ai', content: '  调研了200+企业AI落地案例  ', source_url: 'https://ai.example.com', collected_at: '1718340164' },
  { title: '汽车产业报告', link: 'https://example.com/report/cars', content: '新能源汽车渗透率达到40%', source_url: 'https://auto.example.com', collected_at: '2024-06-14 18:22:44' },
  { title: '新能源汽车政策解读', link: 'https://example.com/news/ev', content: '财政部发布最新新能源汽车补贴方案', source_url: 'https://gov.example.com', collected_at: '2024-06-15 13:22:10' },
  { title: '跨境支付指南', link: 'https://example.com/guides/payment', content: '跨境电商企业支付合规手册', source_url: 'https://fintech.example.com', collected_at: '2024-06-14 16:05:21' },
  { title: 'K8S集群优化方案', link: 'https://example.com/tech/k8s', content: '  KUBERNETES PERFORMANCE TUNING  ', source_url: 'https://cloud.example.com', collected_at: '2024-06-14 15:00:00' },
  { title: '竞品监测截图包', link: 'https://cdn.example.com/comp.zip', content: '15家竞品平台价格监测截图', source_url: 'https://monitor.example.com', collected_at: '2024-06-14 14:22:18' },
  { title: '', link: 'https://example.com/no-title', content: '缺少标题字段的数据', source_url: 'https://orphan.example.com', collected_at: '2024-06-14 13:11:05' },
  { title: '电商大促分析', link: 'https://example.com/insights/sale', content: '双十一促销策略分析预测', source_url: 'https://ecommerce.example.com', collected_at: '2024-06-14 12:00:00' },
]

function runDedup() {
  activeOp.value = 'dedup'
  processing.value = true
  progressPercent.value = 0
  const interval = setInterval(() => {
    progressPercent.value = Math.min(100, progressPercent.value + 25)
    if (progressPercent.value >= 100) clearInterval(interval)
  }, 150)
  setTimeout(() => {
    const before = previewData.value.length
    const seen = new Set()
    previewData.value = previewData.value.filter(row => {
      const key = row.title + '|' + row.link + '|' + row.content
      if (seen.has(key)) return false
      seen.add(key)
      return true
    })
    const removed = before - previewData.value.length
    dedupResult.value = `已去除 ${removed} 条重复数据`
    hasChanges.value = removed > 0
    processing.value = false
    progressPercent.value = 0
  }, 800)
}

function runNullFilter() {
  activeOp.value = 'nullFilter'
  processing.value = true
  progressPercent.value = 0
  const interval = setInterval(() => {
    progressPercent.value = Math.min(100, progressPercent.value + 30)
    if (progressPercent.value >= 100) clearInterval(interval)
  }, 120)
  setTimeout(() => {
    const before = previewData.value.length
    previewData.value = previewData.value.filter(row => {
      return row[nullFilterField.value] && row[nullFilterField.value].trim() !== ''
    })
    const removed = before - previewData.value.length
    nullFilterResult.value = `已过滤 ${removed} 条空值数据`
    hasChanges.value = removed > 0
    processing.value = false
    progressPercent.value = 0
  }, 500)
}

function runFormat() {
  activeOp.value = 'format'
  processing.value = true
  progressPercent.value = 0
  const interval = setInterval(() => {
    progressPercent.value = Math.min(100, progressPercent.value + 20)
    if (progressPercent.value >= 100) clearInterval(interval)
  }, 100)
  setTimeout(() => {
    let count = 0
    previewData.value = previewData.value.map(row => {
      const val = row[formatField.value]
      if (!val) return row
      let newVal = val
      if (formatType.value === 'trim') { newVal = val.trim() }
      else if (formatType.value === 'lowercase') { newVal = val.toLowerCase() }
      else if (formatType.value === 'uppercase') { newVal = val.toUpperCase() }
      else if (formatType.value === 'timestamp') { newVal = new Date(parseInt(val) * 1000).toLocaleString('zh-CN') }
      if (newVal !== val) {
        count++
        return { ...row, [formatField.value]: newVal }
      }
      return row
    })
    formatResult.value = `已转换 ${count} 条数据的字段格式`
    hasChanges.value = count > 0
    processing.value = false
    progressPercent.value = 0
  }, 700)
}

function applyChanges() {
  ElMessage.success('数据清洗结果已应用')
  hasChanges.value = false
  dedupResult.value = ''
  nullFilterResult.value = ''
  formatResult.value = ''
  nullFilterField.value = ''
  formatField.value = ''
  formatType.value = ''
}

function resetData() {
  previewData.value = rawData.value.map(r => ({ ...r }))
  hasChanges.value = false
  dedupResult.value = ''
  nullFilterResult.value = ''
  formatResult.value = ''
  ElMessage.info('已恢复原始数据')
}

onMounted(() => {
  rawData.value = mockData.map(r => ({ ...r }))
  previewData.value = rawData.value.map(r => ({ ...r }))
  dedupResult.value = `检测到 ${countDuplicates()} 条疑似重复数据`
})

function countDuplicates() {
  const seen = new Set()
  let dupes = 0
  rawData.value.forEach(row => {
    const key = row.title + '|' + row.link + '|' + row.content
    if (seen.has(key)) dupes++
    else seen.add(key)
  })
  return dupes
}
</script>

<script>
import { ElMessage } from 'element-plus'
export default { name: 'DataClean' }
</script>

<style scoped>
.page {
  min-height: 100vh;
  background-color: #0d1117;
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
  color: rgba(255, 255, 255, 0.9); letter-spacing: -0.5px;
}
.data-count {
  font-size: 13px; font-weight: 500;
  padding: 6px 14px; background: rgba(76, 110, 245, 0.1);
  color: #7c8aff; border-radius: 20px;
}
.two-panel {
  display: grid; grid-template-columns: 380px 1fr;
  gap: 20px; align-items: start;
}
.card {
  background: rgba(22, 27, 34, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
}
.left-panel { padding: 24px; }
.right-panel { padding: 24px; }
.panel-title {
  font-size: 15px; font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 20px; display: flex; align-items: center; gap: 10px;
}
.preview-count {
  font-size: 11px; font-weight: 500; color: rgba(255, 255, 255, 0.3);
  padding: 2px 8px; background: rgba(255,255,255,0.04); border-radius: 6px;
}
.op-section {
  padding: 16px; margin-bottom: 12px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: 12px;
}
.op-header {
  display: flex; align-items: center; gap: 8px;
  font-size: 14px; font-weight: 600; color: rgba(255,255,255,0.65);
  margin-bottom: 6px;
}
.op-header svg { width: 18px; height: 18px; color: #7c8aff; }
.op-desc {
  font-size: 12px; color: rgba(255,255,255,0.3);
  margin-bottom: 10px; line-height: 1.4;
}
.op-result {
  font-size: 12px; font-weight: 500; margin-bottom: 8px; padding: 4px 0;
}
.op-result.success { color: #34d399; }
.input {
  width: 100%; padding: 9px 14px; font-size: 13px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px; color: rgba(255, 255, 255, 0.75);
  outline: none; transition: all 0.2s ease; box-sizing: border-box;
}
.input:focus { border-color: rgba(76, 110, 245, 0.4); background: rgba(255, 255, 255, 0.06); }
.input-select { cursor: pointer; color-scheme: dark; margin-bottom: 8px; }
.btn-op {
  display: inline-flex; align-items: center; gap: 5px;
  width: 100%; padding: 10px 16px; margin-top: 8px;
  font-size: 13px; font-weight: 600;
  background: rgba(76, 110, 245, 0.1);
  border: 1px solid rgba(76, 110, 245, 0.2);
  border-radius: 10px; color: #7c8aff;
  cursor: pointer; transition: all 0.2s ease;
  justify-content: center;
}
.btn-op:hover:not(:disabled) { background: rgba(76, 110, 245, 0.2); }
.btn-op:disabled { opacity: 0.35; cursor: not-allowed; }
.btn-op svg { width: 16px; height: 16px; }
.action-row {
  display: flex; gap: 10px; margin-top: 16px; padding-top: 16px;
  border-top: 1px solid rgba(255,255,255,0.06);
}
.btn-apply {
  flex: 1; padding: 11px 16px; font-size: 13px; font-weight: 600;
  background: linear-gradient(135deg, #4c6ef5, #7c3aed);
  border: none; border-radius: 10px; color: #fff; cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 2px 12px rgba(76, 110, 245, 0.3);
}
.btn-apply:hover { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(76, 110, 245, 0.45); }
.btn-cancel {
  padding: 11px 20px; font-size: 13px; font-weight: 500;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
  border-radius: 10px; color: rgba(255,255,255,0.45); cursor: pointer; transition: all 0.2s ease;
}
.btn-cancel:hover { background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.7); }
.progress-bar-wrap {
  margin-top: 14px; height: 4px; background: rgba(255,255,255,0.04);
  border-radius: 2px; overflow: hidden;
}
.progress-bar {
  height: 100%; background: linear-gradient(90deg, #4c6ef5, #7c3aed);
  border-radius: 2px; transition: width 0.3s ease;
}
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.data-table th {
  padding: 10px 12px; text-align: left; font-weight: 600;
  color: rgba(255,255,255,0.35); font-size: 10px; text-transform: uppercase;
  letter-spacing: 0.4px; border-bottom: 1px solid rgba(255,255,255,0.06);
  white-space: nowrap; background: rgba(0,0,0,0.15);
}
.data-table td {
  padding: 10px 12px; color: rgba(255,255,255,0.55);
  border-bottom: 1px solid rgba(255,255,255,0.03);
  vertical-align: top; line-height: 1.4; max-width: 160px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.data-table tbody tr { transition: background 0.15s ease; }
.data-table tbody tr:hover { background: rgba(76,110,245,0.04); }
.td-idx { color: rgba(255,255,255,0.2); font-size: 11px; width: 30px; }
.td-title { font-weight: 500; color: rgba(255,255,255,0.7); }
.td-link { color: #7c8aff; }
.td-content { color: rgba(255,255,255,0.4); }
.td-source { font-family: monospace; font-size: 11px; color: rgba(255,255,255,0.3); }
.td-time { white-space: nowrap; color: rgba(255,255,255,0.35); font-size: 11px; }
.td-empty { text-align: center; color: rgba(255,255,255,0.2); padding: 40px 12px !important; }

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