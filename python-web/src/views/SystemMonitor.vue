<template>
  <div class="page">
    <NavBar />
    <div class="content">
      <div class="page-header">
        <h1 class="page-title">资源看板</h1>
        <div class="header-right">
          <span class="refresh-tag" :class="{ refreshing: isRefreshing }">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
            </svg>
            每3秒刷新
          </span>
        </div>
      </div>

      <div class="gauges-row">
        <div v-for="g in gauges" :key="g.name" class="card gauge-card">
          <div class="gauge-info">
            <span class="gauge-label">{{ g.label }}</span>
            <span class="gauge-value">{{ Math.round(g.value) }}%</span>
          </div>
          <div class="gauge-ring">
            <svg viewBox="0 0 120 120">
              <circle cx="60" cy="60" r="48" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="8" />
              <circle
                cx="60" cy="60" r="48" fill="none"
                :stroke="gaugeColor(g.value)" stroke-width="8"
                stroke-linecap="round"
                :stroke-dasharray="2 * Math.PI * 48"
                :stroke-dashoffset="2 * Math.PI * 48 * (1 - g.value / 100)"
                transform="rotate(-90 60 60)"
                class="gauge-arc"
              />
            </svg>
            <span class="gauge-status" :class="'status-' + gaugeStatus(g.value)">{{ gaugeStatusText(g.value) }}</span>
          </div>
        </div>
      </div>

      <div class="card chart-card">
        <h3 class="section-title">CPU / 内存 使用历史</h3>
        <div class="chart-wrap">
          <svg viewBox="0 0 720 200" class="line-chart">
            <line v-for="i in 4" :key="'g'+i" :x1="0" :y1="i*50" :x2="720" :y2="i*50" stroke="rgba(255,255,255,0.04)" stroke-width="1" />
            <polyline :points="cpuLinePoints" fill="none" stroke="#4c6ef5" stroke-width="2" stroke-linejoin="round" />
            <polyline :points="memLinePoints" fill="none" stroke="#7c3aed" stroke-width="2" stroke-linejoin="round" />
          </svg>
          <div class="chart-legend">
            <span class="legend-item"><span class="legend-dot cpu-dot"></span>CPU</span>
            <span class="legend-item"><span class="legend-dot mem-dot"></span>内存</span>
          </div>
        </div>
      </div>

      <div class="card">
        <h3 class="section-title">任务资源排名</h3>
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>任务名称</th>
                <th class="sortable" @click="taskSortKey='cpu'; taskSortDir=taskSortKey==='cpu'&&taskSortDir==='asc'?'desc':'asc'">CPU% <span class="sort-arrow">{{ taskSortKey==='cpu'? taskSortDir==='asc'?'↑':'↓':'↕' }}</span></th>
                <th class="sortable" @click="taskSortKey='mem'; taskSortDir=taskSortKey==='mem'&&taskSortDir==='asc'?'desc':'asc'">内存% <span class="sort-arrow">{{ taskSortKey==='mem'? taskSortDir==='asc'?'↑':'↓':'↕' }}</span></th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="t in sortedTasks" :key="t.name">
                <td class="task-name">{{ t.name }}</td>
                <td>
                  <div class="usage-bar">
                    <div class="usage-fill cpu-fill" :style="{ width: t.cpu + '%' }"></div>
                    <span class="usage-text">{{ t.cpu }}%</span>
                  </div>
                </td>
                <td>
                  <div class="usage-bar">
                    <div class="usage-fill mem-fill" :style="{ width: t.mem + '%' }"></div>
                    <span class="usage-text">{{ t.mem }}%</span>
                  </div>
                </td>
                <td><span class="status-tag" :class="'s-' + t.status">{{ t.status === 'running' ? '运行中' : t.status === 'idle' ? '空闲' : '已停止' }}</span></td>
                <td>
                  <button class="btn-sm" @click="ElMessage.info('查看详情: ' + t.name)">详情</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <h3 class="section-title">告警阈值设置</h3>
        <div class="thresholds">
          <div class="threshold-group">
            <label class="filter-label">CPU 阈值 (%)</label>
            <input type="range" v-model.number="thresholdCpu" min="50" max="99" class="slider" />
            <span class="threshold-val">{{ thresholdCpu }}%</span>
          </div>
          <div class="threshold-group">
            <label class="filter-label">内存阈值 (%)</label>
            <input type="range" v-model.number="thresholdMem" min="50" max="99" class="slider" />
            <span class="threshold-val">{{ thresholdMem }}%</span>
          </div>
          <div class="threshold-group">
            <label class="filter-label">磁盘阈值 (%)</label>
            <input type="range" v-model.number="thresholdDisk" min="50" max="99" class="slider" />
            <span class="threshold-val">{{ thresholdDisk }}%</span>
          </div>
          <button class="btn-save-threshold" @click="saveThresholds">保存阈值</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import NavBar from '../components/NavBar.vue'

const isRefreshing = ref(false)
const cpuHistory = ref([])
const memHistory = ref([])

const thresholdCpu = ref(80)
const thresholdMem = ref(80)
const thresholdDisk = ref(85)

const taskSortKey = ref('cpu')
const taskSortDir = ref('desc')

const gauges = ref([
  { name: 'cpu', label: 'CPU 使用率', value: 45 },
  { name: 'mem', label: '内存使用率', value: 62 },
  { name: 'disk', label: '磁盘使用率', value: 38 },
  { name: 'net', label: '网络带宽', value: 28 }
])

const tasks = ref([
  { name: '电商商品数据采集', cpu: 32, mem: 45, status: 'running' },
  { name: '新闻资讯爬取', cpu: 18, mem: 28, status: 'running' },
  { name: '竞品价格追踪', cpu: 12, mem: 15, status: 'running' },
  { name: '社交媒体采集', cpu: 8, mem: 22, status: 'idle' },
  { name: '地图POI数据', cpu: 5, mem: 12, status: 'idle' },
  { name: '视频元数据采集', cpu: 0, mem: 0, status: 'stopped' }
])

const sortedTasks = computed(() => {
  return [...tasks.value].sort((a, b) => {
    const cmp = a[taskSortKey.value] - b[taskSortKey.value]
    return taskSortDir.value === 'asc' ? cmp : -cmp
  })
})

const cpuLinePoints = computed(() => {
  if (cpuHistory.value.length < 2) return ''
  const maxVal = 100
  const w = 720; const h = 200
  return cpuHistory.value.map((v, i) => {
    const x = (i / (cpuHistory.value.length - 1)) * w
    const y = h - (v / maxVal) * h
    return `${x},${y}`
  }).join(' ')
})

const memLinePoints = computed(() => {
  if (memHistory.value.length < 2) return ''
  const maxVal = 100
  const w = 720; const h = 200
  return memHistory.value.map((v, i) => {
    const x = (i / (memHistory.value.length - 1)) * w
    const y = h - (v / maxVal) * h
    return `${x},${y}`
  }).join(' ')
})

function gaugeColor(val) {
  if (val < 60) return '#34d399'
  if (val < 80) return '#fbbf24'
  return '#f87171'
}

function gaugeStatus(val) {
  if (val < 60) return 'normal'
  if (val < 80) return 'warn'
  return 'danger'
}

function gaugeStatusText(val) {
  if (val < 60) return '正常'
  if (val < 80) return '警告'
  return '危险'
}

function fluctuate(base) {
  return Math.max(0, Math.min(100, base + (Math.random() - 0.5) * 16))
}

function refreshGauges() {
  isRefreshing.value = true
  gauges.value.forEach(g => {
    g.value = fluctuate(g.value)
  })
  tasks.value.forEach(t => {
    if (t.status !== 'stopped') {
      t.cpu = Math.max(0, Math.min(100, t.cpu + (Math.random() - 0.5) * 6))
      t.mem = Math.max(0, Math.min(100, t.mem + (Math.random() - 0.5) * 4))
    }
  })
  cpuHistory.value.push(gauges.value[0].value)
  memHistory.value.push(gauges.value[1].value)
  if (cpuHistory.value.length > 24) cpuHistory.value.shift()
  if (memHistory.value.length > 24) memHistory.value.shift()
  setTimeout(() => { isRefreshing.value = false }, 300)
}

function saveThresholds() {
  ElMessage.success('告警阈值已保存')
}

let timer = null

onMounted(() => {
  for (let i = 24; i >= 1; i--) {
    cpuHistory.value.push(Math.round(35 + Math.random() * 25))
    memHistory.value.push(Math.round(50 + Math.random() * 25))
  }
  refreshGauges()
  timer = setInterval(refreshGauges, 3000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<script>
import { ElMessage } from 'element-plus'
export default { name: 'SystemMonitor' }
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
  color: rgba(255, 255, 255, 0.9); letter-spacing: -0.5px;
}
.header-right { display: flex; align-items: center; }
.refresh-tag {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 12px; font-weight: 500;
  color: rgba(255,255,255,0.3); transition: color 0.3s ease;
}
.refresh-tag svg { width: 14px; height: 14px; }
.refresh-tag.refreshing { color: #7c8aff; }
.refresh-tag.refreshing svg { animation: spin 0.8s linear; }
@keyframes spin { to { transform: rotate(360deg); } }
.gauges-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 20px; }
.card {
  background: rgba(22, 27, 34, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 24px; margin-bottom: 20px;
}
.gauge-card {
  text-align: center; padding: 20px 12px;
}
.gauge-info { margin-bottom: 8px; }
.gauge-label { font-size: 11px; color: rgba(255,255,255,0.35); text-transform: uppercase; letter-spacing: 0.5px; display: block; margin-bottom: 4px; }
.gauge-value { font-size: 32px; font-weight: 700; color: rgba(255,255,255,0.85); }
.gauge-ring { position: relative; display: inline-block; }
.gauge-ring svg { width: 120px; height: 120px; }
.gauge-arc { transition: stroke-dashoffset 0.8s ease, stroke 0.8s ease; }
.gauge-status { position: absolute; bottom: 12px; left: 50%; transform: translateX(-50%); font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 4px; }
.status-normal { background: rgba(52,211,153,0.12); color: #34d399; }
.status-warn { background: rgba(251,191,36,0.12); color: #fbbf24; }
.status-danger { background: rgba(248,113,113,0.12); color: #f87171; }
.section-title {
  font-size: 15px; font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 16px;
}
.chart-wrap { }
.line-chart { width: 100%; height: auto; }
.chart-legend { display: flex; gap: 20px; margin-top: 12px; }
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px; color: rgba(255,255,255,0.4); }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; }
.cpu-dot { background: #4c6ef5; }
.mem-dot { background: #7c3aed; }
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th {
  padding: 12px 16px; text-align: left; font-weight: 600;
  color: rgba(255,255,255,0.35); font-size: 11px; text-transform: uppercase;
  letter-spacing: 0.4px; border-bottom: 1px solid rgba(255,255,255,0.06);
  white-space: nowrap; background: rgba(0,0,0,0.15);
}
.data-table th.sortable { cursor: pointer; user-select: none; }
.data-table th.sortable:hover { color: rgba(255,255,255,0.6); }
.sort-arrow { font-size: 10px; opacity: 0.5; margin-left: 3px; }
.data-table td {
  padding: 12px 16px; color: rgba(255,255,255,0.6);
  border-bottom: 1px solid rgba(255,255,255,0.03);
}
.data-table tbody tr:hover { background: rgba(76,110,245,0.04); }
.task-name { font-weight: 500; color: rgba(255,255,255,0.75); }
.usage-bar {
  display: flex; align-items: center; gap: 8px;
  position: relative; height: 22px; background: rgba(255,255,255,0.04);
  border-radius: 6px; overflow: hidden; min-width: 100px;
}
.usage-fill {
  height: 100%; border-radius: 6px; transition: width 0.8s ease;
}
.cpu-fill { background: rgba(76,110,245,0.4); }
.mem-fill { background: rgba(124,58,237,0.4); }
.usage-text { position: absolute; right: 8px; font-size: 11px; font-weight: 600; color: rgba(255,255,255,0.5); }
.status-tag {
  font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 6px;
}
.s-running { background: rgba(52,211,153,0.12); color: #34d399; }
.s-idle { background: rgba(251,191,36,0.12); color: #fbbf24; }
.s-stopped { background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.3); }
.btn-sm {
  padding: 5px 12px; font-size: 11px; font-weight: 500;
  background: rgba(76,110,245,0.1); border: 1px solid rgba(76,110,245,0.15);
  border-radius: 6px; color: #7c8aff; cursor: pointer; transition: all 0.2s ease;
}
.btn-sm:hover { background: rgba(76,110,245,0.2); }
.thresholds { display: flex; gap: 24px; align-items: flex-end; flex-wrap: wrap; }
.threshold-group { flex: 1; min-width: 160px; }
.filter-label {
  display: block; font-size: 12px; font-weight: 500;
  color: rgba(255,255,255,0.35); margin-bottom: 6px;
}
.slider {
  width: 100%; accent-color: #4c6ef5; cursor: pointer;
}
.threshold-val {
  display: inline-block; margin-top: 4px;
  font-size: 13px; font-weight: 600; color: #7c8aff;
}
.btn-save-threshold {
  padding: 10px 24px; font-size: 13px; font-weight: 600;
  background: linear-gradient(135deg, #4c6ef5, #7c3aed);
  border: none; border-radius: 10px; color: #fff; cursor: pointer;
  transition: all 0.25s ease; box-shadow: 0 2px 12px rgba(76,110,245,0.3);
}
.btn-save-threshold:hover { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(76,110,245,0.45); }

@media (max-width: 768px) {
  .content { padding: 24px 16px 64px; }
  .page-title { font-size: 22px; }
  .gauges-row { grid-template-columns: repeat(2, 1fr); }
  .thresholds { flex-direction: column; }
}
@media (max-width: 560px) {
  .gauges-row { grid-template-columns: 1fr; }
}
</style>