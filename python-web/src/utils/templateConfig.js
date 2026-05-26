/** 任务模板配置：构建与回填 */

export const TEMPLATE_CATEGORIES = [
  { value: 'all', label: '全部' },
  { value: 'general', label: '通用' },
  { value: 'ecommerce', label: '电商' },
  { value: 'news', label: '资讯' },
  { value: 'monitor', label: '监控' }
]

export function categoryLabel(value) {
  const item = TEMPLATE_CATEGORIES.find(c => c.value === value)
  return item ? item.label : value || '通用'
}

export function minutesToCron(minutes) {
  if (!minutes || minutes < 1) return '*/30 * * * *'
  return `*/${minutes} * * * *`
}

export function cronToMinutes(cron) {
  if (!cron) return 30
  const match = cron.match(/^\*\/(\d+)\s+\*\s+\*\s+\*\s+\*$/)
  if (match) return parseInt(match[1], 10) || 30
  return 30
}

export function parseTemplateConfig(raw) {
  if (!raw) return {}
  if (typeof raw === 'object') return raw
  if (typeof raw === 'string' && raw.trim()) {
    try {
      return JSON.parse(raw)
    } catch (e) {
      return {}
    }
  }
  return {}
}

/** 从表单构建完整模板 config（与任务创建一致） */
export function buildTemplateConfig(form) {
  let headers = form.headers
  if (typeof headers === 'string' && headers.trim()) {
    try {
      headers = JSON.parse(headers)
    } catch (e) {
      headers = {}
    }
  } else if (!headers) {
    headers = {}
  }

  let intervalSeconds = form.intervalSeconds
  if (intervalSeconds == null && form.interval != null) {
    intervalSeconds = form.interval > 60 ? Math.round(form.interval / 1000) : form.interval
  }

  return {
    target_url: (form.targetUrl || form.target_url || '').trim(),
    cron_expr: minutesToCron(form.intervalMinutes),
    interval_seconds: Number(intervalSeconds) || 3,
    concurrency: Number(form.concurrency) || 1,
    max_retries: Number(form.maxRetries ?? form.max_retries) || 0,
    maxRetries: Number(form.maxRetries ?? form.max_retries) || 0,
    retry_interval: Number(form.retryInterval ?? form.retry_interval) || 60,
    crawl_mode: form.crawlMode || form.crawl_mode || 'link',
    total_pages: Number(form.totalPages ?? form.total_pages) || 1,
    headers,
    proxy_group: (form.proxyGroup || form.proxy_group || '').trim(),
    task_type: form.taskType || form.task_type || 'crawler'
  }
}

/** 将模板 config 回填到新建任务表单 */
export function applyTemplateToTaskForm(form, config, templateMeta = {}) {
  const cfg = parseTemplateConfig(config)
  if (templateMeta.name && !form.name) {
    form.name = `${templateMeta.name} - 任务`
  }
  if (templateMeta.description) {
    form.description = templateMeta.description
  }
  form.targetUrl = cfg.target_url || ''
  form.taskType = cfg.task_type || 'crawler'
  form.intervalMinutes = cronToMinutes(cfg.cron_expr)
  form.concurrency = cfg.concurrency ?? 1
  const sec = cfg.interval_seconds ?? cfg.interval
  form.intervalSeconds = sec != null && sec > 60 ? Math.round(sec / 1000) : (Number(sec) || 3)
  form.maxRetries = cfg.max_retries ?? cfg.maxRetries ?? 3
  form.retryInterval = cfg.retry_interval ?? 60
  form.crawlMode = cfg.crawl_mode || 'link'
  form.totalPages = cfg.total_pages ?? 1
  form.proxyGroup = cfg.proxy_group || ''
  if (typeof cfg.headers === 'object') {
    form.headers = JSON.stringify(cfg.headers, null, 2)
  } else {
    form.headers = cfg.headers || ''
  }
  return cfg
}

/** 将模板 config 回填到模板编辑弹窗表单 */
export function applyTemplateToModalForm(modalForm, config) {
  const cfg = parseTemplateConfig(config)
  modalForm.targetUrl = cfg.target_url || ''
  modalForm.intervalMinutes = cronToMinutes(cfg.cron_expr)
  modalForm.concurrency = cfg.concurrency ?? 1
  const sec = cfg.interval_seconds ?? cfg.interval
  modalForm.intervalSeconds = sec != null && sec > 60 ? Math.round(sec / 1000) : (Number(sec) || 3)
  modalForm.maxRetries = cfg.max_retries ?? cfg.maxRetries ?? 3
  modalForm.retryInterval = cfg.retry_interval ?? 60
  modalForm.crawlMode = cfg.crawl_mode || 'link'
  modalForm.totalPages = cfg.total_pages ?? 1
  modalForm.proxyGroup = cfg.proxy_group || ''
  modalForm.taskType = cfg.task_type || 'crawler'
  if (typeof cfg.headers === 'object') {
    modalForm.headers = JSON.stringify(cfg.headers, null, 2)
  } else {
    modalForm.headers = cfg.headers || ''
  }
}

export function getTemplatePreviewLines(config) {
  const cfg = parseTemplateConfig(config)
  const lines = [
    { label: '目标 URL', value: cfg.target_url || '—' },
    { label: '执行周期', value: `每 ${cronToMinutes(cfg.cron_expr)} 分钟` },
    { label: '爬取模式', value: cfg.crawl_mode === 'image' ? '图片' : cfg.crawl_mode === 'mixed' ? '混合' : '链接' },
    { label: '爬取页数', value: String(cfg.total_pages ?? 1) },
    { label: '并发数', value: String(cfg.concurrency ?? 1) },
    { label: '请求间隔', value: `${cfg.interval_seconds ?? 3} 秒` },
    { label: '最大重试', value: String(cfg.max_retries ?? cfg.maxRetries ?? 0) },
    { label: '重试间隔', value: `${cfg.retry_interval ?? 60} 秒` },
    { label: '代理组', value: cfg.proxy_group || '未配置' },
    { label: '任务类型', value: cfg.task_type || 'crawler' }
  ]
  return lines
}

export function getDefaultModalForm() {
  return {
    name: '',
    description: '',
    category: 'general',
    isFavorite: false,
    targetUrl: '',
    intervalMinutes: 30,
    concurrency: 1,
    intervalSeconds: 3,
    maxRetries: 3,
    retryInterval: 60,
    crawlMode: 'link',
    totalPages: 1,
    headers: '',
    proxyGroup: '',
    taskType: 'crawler'
  }
}
