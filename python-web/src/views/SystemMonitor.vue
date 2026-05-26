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
import { ElMessage } from 'element-plus'
import { systemAPI } from '../api/system'
import { taskAPI } from '../api/task'
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
  { name: 'cpu', label: 'CPU 使用率', value: 0 },
  { name: 'mem', label: '内存使用率', value: 0 },
  { name: 'disk', label: '磁盘使用率', value: 0 },
  { name: 'net', label: '网络带宽', value: 0 }
])

const tasks = ref([])

const sortedTasks = computed(() => {
  return [...tasks.value].sort((a, b) => {
    const cmp = (a[taskSortKey.value] || 0) - (b[taskSortKey.value] || 0)
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

async function refreshGauges() {
  isRefreshing.value = true
  try {
    const res = await systemAPI.getResources()
    if (res.data.success) {
      const data = res.data.data
      gauges.value[0].value = data.cpu_percent ?? 0
      gauges.value[1].value = data.memory_percent ?? 0
      gauges.value[2].value = data.disk_percent ?? 0
      gauges.value[3].value = data.network_io ?? 0
    }
  } catch (error) {
    // 静默处理轮询异常
  }
  cpuHistory.value.push(gauges.value[0].value)
  memHistory.value.push(gauges.value[1].value)
  if (cpuHistory.value.length > 24) cpuHistory.value.shift()
  if (memHistory.value.length > 24) memHistory.value.shift()
  setTimeout(() => { isRefreshing.value = false }, 300)
}

async function saveThresholds() {
  try {
    await systemAPI.updateSetting('threshold_cpu', { value: thresholdCpu.value })
    await systemAPI.updateSetting('threshold_mem', { value: thresholdMem.value })
    await systemAPI.updateSetting('threshold_disk', { value: thresholdDisk.value })
    ElMessage.success('告警阈值已保存')
  } catch (error) {
    ElMessage.error('保存阈值失败')
  }
}

let timer = null

onMounted(async () => {
  await refreshGauges()
  timer = setInterval(refreshGauges, 5000)

  try {
    const res = await taskAPI.getTasks({ page_size: 10 })
    if (res.data.success) {
      const taskList = res.data.data.list || res.data.data || []
      tasks.value = taskList.map(t => ({
        name: t.name || t.id,
        // TODO: Replace with real resource-per-task data from backend when available
        cpu: Math.round(Math.random() * 30),
        mem: Math.round(Math.random() * 40),
        status: t.status || 'idle'
      }))
    }
  } catch (error) {
    // TODO: Replace with real resource-per-task data from backend when available
  }
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
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
  color: rgba(255, 255, 255, 0.9); letter-spacing: -0.5px;
}
.header-right { display: flex; align-items: center; }
.refresh-tag {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 12px; font-weight: 500;
  color: rgba(255,255,255,0.3); transition: color 0.3s ease;
}
.refresh-tag svg { width: 14px; height: 14px; }
.refresh-tag.refreshing { color: var(--active-color); }
.refresh-tag.refreshing svg { animation: spin 0.8s linear; }
@keyframes spin { to { transform: rotate(360deg); } }
.gauges-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 20px; }
.card {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
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
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-muted); }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; }
.cpu-dot { background: var(--accent-color); }
.mem-dot { background: var(--accent-color); }
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th {
  padding: 12px 16px; text-align: left; font-weight: 600;
  color: var(--text-muted); font-size: 11px; text-transform: uppercase;
  letter-spacing: 0.4px; border-bottom: 1px solid var(--border-color);
  white-space: nowrap; background: rgba(0,0,0,0.15);
}
.data-table th.sortable { cursor: pointer; user-select: none; }
.data-table th.sortable:hover { color: var(--text-secondary); }
.sort-arrow { font-size: 10px; opacity: 0.5; margin-left: 3px; }
.data-table td {
  padding: 12px 16px; color: var(--text-secondary);
  border-bottom: 1px solid rgba(255,255,255,0.03);
}
.data-table tbody tr:hover { background: rgba(var(--accent-rgb), 0.04); }
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
  background: rgba(var(--accent-rgb), 0.1); border: 1px solid rgba(var(--accent-rgb), 0.15);
  border-radius: 6px; color: var(--accent-color); cursor: pointer; transition: all 0.2s ease;
}
.btn-sm:hover { background: rgba(var(--accent-rgb), 0.2); }
.thresholds { display: flex; gap: 24px; align-items: flex-end; flex-wrap: wrap; }
.threshold-group { flex: 1; min-width: 160px; }
.filter-label {
  display: block; font-size: 12px; font-weight: 500;
  color: rgba(255,255,255,0.35); margin-bottom: 6px;
}
.slider {
  width: 100%; accent-color: var(--accent-primary); cursor: pointer;
}
.threshold-val {
  display: inline-block; margin-top: 4px;
  font-size: 13px; font-weight: 600; color: var(--active-color);
}
.btn-save-threshold {
  padding: 10px 24px; font-size: 13px; font-weight: 600;
  background: var(--gradient-primary);
  border: none; border-radius: 10px; color: var(--btn-text-color, #fff); cursor: pointer;
  transition: all 0.25s ease; box-shadow: 0 2px 12px rgba(var(--accent-rgb), 0.3);
}
.btn-save-threshold:hover { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(var(--accent-rgb), 0.45); }

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