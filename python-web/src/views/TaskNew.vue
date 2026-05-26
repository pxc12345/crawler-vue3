<template>
  <div class="task-new-page">
    <NavBar />
    <div class="new-content">
      <div class="new-header">
        <button class="btn-back" @click="$router.back()">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
        </button>
        <h1 class="new-title">新建任务</h1>
      </div>

      <div class="template-bar">
        <label class="form-label">从模板创建</label>
        <div class="template-bar-row">
          <select v-model="selectedTemplateId" class="form-input template-select" @change="onTemplateSelect">
            <option value="">不使用模板（手动填写）</option>
            <option v-for="t in templateList" :key="t.id" :value="String(t.id)">
              {{ t.isFavorite ? '★ ' : '' }}{{ t.name }}（{{ t.categoryLabel }}）
            </option>
          </select>
          <button
            type="button"
            class="btn-apply-template"
            :disabled="!selectedTemplateId || applyingTemplate"
            @click="applySelectedTemplate"
          >
            {{ applyingTemplate ? '加载中...' : '应用模板' }}
          </button>
        </div>
        <p v-if="appliedTemplateName" class="template-applied-hint">
          已应用模板：{{ appliedTemplateName }}
        </p>
      </div>

      <div class="config-form">
        <div class="form-row">
          <div class="form-group full">
            <label class="form-label">任务名称</label>
            <input v-model="form.name" type="text" class="form-input" placeholder="输入任务名称" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group full">
            <label class="form-label">目标 URL</label>
            <input v-model="form.targetUrl" type="text" class="form-input" placeholder="https://example.com" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">执行周期（分钟）</label>
            <input v-model.number="form.intervalMinutes" type="number" class="form-input" placeholder="例如：30" min="1" />
          </div>
          <div class="form-group">
            <label class="form-label">爬取页数</label>
            <input v-model.number="form.totalPages" type="number" class="form-input" min="1" max="100" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">并发数</label>
            <input v-model.number="form.concurrency" type="number" class="form-input" placeholder="1" min="1" />
          </div>
          <div class="form-group">
            <label class="form-label">请求间隔 (秒)</label>
            <input v-model.number="form.intervalSeconds" type="number" class="form-input" placeholder="3" min="1" max="60" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">最大重试次数</label>
            <input v-model.number="form.maxRetries" type="number" class="form-input" placeholder="3" min="0" />
          </div>
          <div class="form-group">
            <label class="form-label">重试间隔 (秒)</label>
            <input v-model.number="form.retryInterval" type="number" class="form-input" min="1" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group full">
            <label class="form-label">任务类型</label>
            <select v-model="form.taskType" class="form-input">
              <option value="crawler">爬虫任务</option>
              <option value="data_collection">数据采集</option>
              <option value="monitor">监控任务</option>
            </select>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group full">
            <label class="form-label">爬取模式</label>
            <select v-model="form.crawlMode" class="form-input">
              <option value="link">链接模式</option>
              <option value="image">图片模式</option>
              <option value="mixed">混合模式</option>
            </select>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group full">
            <label class="form-label">代理组</label>
            <input v-model="form.proxyGroup" type="text" class="form-input" placeholder="留空则不使用代理组" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group full">
            <label class="form-label">请求头 (JSON，可选)</label>
            <textarea v-model="form.headers" class="form-textarea" rows="3" placeholder='{"User-Agent": "..."}'></textarea>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group full">
            <label class="form-label">描述（可选）</label>
            <input v-model="form.description" type="text" class="form-input" placeholder="任务描述" />
          </div>
        </div>
      </div>

      <div class="form-actions">
        <button class="action-btn cancel" @click="$router.back()">取消</button>
        <button class="action-btn primary" @click="createTask" :disabled="creating">
          {{ creating ? '创建中...' : '创建任务' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import NavBar from '../components/NavBar.vue'
import { taskAPI } from '../api/task'
import {
  categoryLabel,
  buildTemplateConfig,
  applyTemplateToTaskForm
} from '../utils/templateConfig'

const router = useRouter()
const route = useRoute()
const creating = ref(false)
const applyingTemplate = ref(false)
const templateList = ref([])
const selectedTemplateId = ref('')
const appliedTemplateName = ref('')

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
  headers: '',
  description: ''
})

async function loadTemplateList() {
  try {
    const res = await taskAPI.getTemplates()
    if (res.data.success) {
      templateList.value = (res.data.data || []).map(item => ({
        id: item.id,
        name: item.name,
        isFavorite: item.is_favorite === 1 || item.is_favorite === true,
        categoryLabel: categoryLabel(item.category || 'general'),
        config: item.config
      }))
    }
  } catch (e) {
    console.error('加载模板列表失败', e)
  }
}

async function loadAndApplyTemplate(templateId, showMessage = true) {
  if (!templateId) return
  applyingTemplate.value = true
  try {
    const res = await taskAPI.getTemplateById(templateId)
    if (res.data.success) {
      const tmpl = res.data.data
      applyTemplateToTaskForm(form, tmpl.config, {
        name: tmpl.name,
        description: tmpl.description
      })
      appliedTemplateName.value = tmpl.name
      selectedTemplateId.value = String(templateId)
      if (showMessage) {
        ElMessage.success(`已应用模板「${tmpl.name}」的配置`)
      }
      await taskAPI.useTemplate(templateId).catch(() => {})
    } else {
      ElMessage.error(res.data.message || '加载模板失败')
    }
  } catch (e) {
    ElMessage.error('加载模板失败')
  } finally {
    applyingTemplate.value = false
  }
}

function onTemplateSelect() {
  if (!selectedTemplateId.value) {
    appliedTemplateName.value = ''
    return
  }
}

async function applySelectedTemplate() {
  if (!selectedTemplateId.value) {
    ElMessage.warning('请先选择模板')
    return
  }
  await loadAndApplyTemplate(selectedTemplateId.value, true)
}

async function createTask() {
  if (!form.name.trim()) {
    ElMessage.warning('请输入任务名称')
    return
  }
  if (!form.targetUrl.trim()) {
    ElMessage.warning('请输入目标 URL')
    return
  }

  creating.value = true
  try {
    const config = buildTemplateConfig(form)

    const res = await taskAPI.createTask({
      name: form.name,
      task_type: form.taskType,
      config: config,
      description: form.description,
      template_id: selectedTemplateId.value ? Number(selectedTemplateId.value) : undefined
    })

    if (res.data.success) {
      ElMessage.success('任务创建成功')
      router.push('/tasks')
    } else {
      ElMessage.error(res.data.message || '创建失败')
    }
  } catch (e) {
    ElMessage.error('创建任务失败')
    console.error(e)
  } finally {
    creating.value = false
  }
}

onMounted(async () => {
  await loadTemplateList()
  const qid = route.query.templateId
  if (qid) {
    selectedTemplateId.value = String(qid)
    await loadAndApplyTemplate(qid, true)
  }
})
</script>

<style scoped>
.task-new-page {
  min-height: 100vh;
  background-color: var(--bg-primary);
  background-image:
    linear-gradient(var(--border-color) 1px, transparent 1px),
    linear-gradient(90deg, var(--border-color) 1px, transparent 1px);
  background-size: 40px 40px;
}

.new-content {
  max-width: 640px;
  margin: 0 auto;
  padding: 40px 24px 80px;
}

.new-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
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
}

.btn-back:hover {
  color: var(--text-primary);
  border-color: rgba(255, 255, 255, 0.15);
}

.btn-back svg {
  width: 20px;
  height: 20px;
}

.new-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.template-bar {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 16px;
}

.template-bar .form-label {
  margin-bottom: 8px;
}

.template-bar-row {
  display: flex;
  gap: 10px;
}

.template-select {
  flex: 1;
}

.btn-apply-template {
  flex-shrink: 0;
  padding: 10px 16px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 10px;
  border: 1px solid rgba(var(--accent-rgb), 0.3);
  background: var(--active-bg);
  color: var(--active-color);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-apply-template:hover:not(:disabled) {
  background: rgba(var(--accent-rgb), 0.2);
}

.btn-apply-template:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.template-applied-hint {
  margin-top: 10px;
  font-size: 12px;
  color: #34d399;
}

.config-form {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 28px;
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
  background: rgba(255, 255, 255, 0.03);
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

.form-input::placeholder {
  color: var(--text-muted);
}

.form-textarea {
  width: 100%;
  padding: 11px 16px;
  font-size: 13px;
  font-family: inherit;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  outline: none;
  resize: vertical;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
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

.action-btn.primary {
  background: var(--gradient-primary);
  color: #fff;
  border: none;
  box-shadow: 0 4px 14px rgba(var(--accent-rgb), 0.3);
}

.action-btn.primary:hover:not(:disabled) {
  box-shadow: 0 6px 20px rgba(var(--accent-rgb), 0.45);
  transform: translateY(-1px);
}

.action-btn.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.action-btn.cancel:hover {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-primary);
}

@media (max-width: 768px) {
  .new-content { padding: 24px 16px 64px; }
  .form-row { grid-template-columns: 1fr; }
  .template-bar-row { flex-direction: column; }
}
</style>
