/**
 * 从已有任务构建「全新运行实例」的创建参数（不含原任务执行痕迹）
 */

const CONFIG_KEYS = [
  'target_url',
  'cron_expr',
  'interval_seconds',
  'interval',
  'concurrency',
  'max_retries',
  'maxRetries',
  'retry_interval',
  'crawl_mode',
  'total_pages',
  'headers',
  'proxy_group',
  'task_type',
  'timeout',
  'validate_images'
]

const STRIP_KEYS = new Set([
  'last_run_started_at',
  'source_task_id',
  '_last_execution'
])

function formatLocalRunLabel() {
  const now = new Date()
  const y = now.getFullYear()
  const m = String(now.getMonth() + 1).padStart(2, '0')
  const d = String(now.getDate()).padStart(2, '0')
  const h = String(now.getHours()).padStart(2, '0')
  const min = String(now.getMinutes()).padStart(2, '0')
  const s = String(now.getSeconds()).padStart(2, '0')
  return `${y}-${m}-${d} ${h}:${min}:${s}`
}

function baseTaskName(name) {
  const text = (name || '任务').trim()
  const idx = text.indexOf(' · ')
  return idx >= 0 ? text.slice(0, idx) : text
}

/**
 * 提取干净的爬虫配置，剔除原任务运行元数据
 */
export function buildCleanTaskConfig(rawConfig = {}, targetUrl = '') {
  const source = rawConfig && typeof rawConfig === 'object' ? rawConfig : {}
  const config = {}

  CONFIG_KEYS.forEach((key) => {
    if (source[key] !== undefined && source[key] !== null && !STRIP_KEYS.has(key)) {
      config[key] = source[key]
    }
  })

  if (!config.target_url && targetUrl) {
    config.target_url = targetUrl
  }

  if (!config.task_type) {
    config.task_type = 'crawler'
  }

  return config
}

/**
 * 是否需要在启动前先复制出新任务。
 * - 从未运行过的新任务：直接启动，不复制
 * - 已运行过 / 已有执行痕迹：再次启动时复制出新实例
 */
export function shouldCloneTaskBeforeStart(task) {
  const config = task?.config && typeof task.config === 'object' ? task.config : {}
  if (config.last_run_started_at) {
    return true
  }
  const status = (task?.status || '').toLowerCase()
  if (status === 'completed' || status === 'failed') {
    return true
  }
  const dataCount = Number(task?.data_count ?? task?.dataCount ?? 0)
  if (dataCount > 0) {
    return true
  }
  if (config._last_execution && typeof config._last_execution === 'object') {
    return true
  }
  return false
}

/**
 * 构建创建新任务的请求体
 */
export function buildTaskRunCreatePayload(task) {
  const rawConfig = task?.config && typeof task.config === 'object' ? task.config : {}
  const config = buildCleanTaskConfig(rawConfig, task?.target_url || task?.url || '')
  const taskType = config.task_type || 'crawler'
  const label = formatLocalRunLabel()

  return {
    name: `${baseTaskName(task?.name)} · ${label}`,
    task_type: taskType,
    config,
    description: ''
  }
}
