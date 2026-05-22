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
            <label class="form-label">并发数</label>
            <input v-model.number="form.concurrency" type="number" class="form-input" placeholder="1" min="1" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">请求间隔 (秒)</label>
            <input v-model.number="form.intervalSeconds" type="number" class="form-input" placeholder="3" min="1" />
          </div>
          <div class="form-group">
            <label class="form-label">最大重试次数</label>
            <input v-model.number="form.maxRetries" type="number" class="form-input" placeholder="3" min="0" />
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
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import NavBar from '../components/NavBar.vue'
import { taskAPI } from '../api/task'

const router = useRouter()
const creating = ref(false)

const form = reactive({
  name: '',
  targetUrl: '',
  taskType: 'crawler',
  intervalMinutes: 30,
  concurrency: 1,
  intervalSeconds: 3,
  maxRetries: 3,
  crawlMode: 'link',
  description: ''
})

function minutesToCron(minutes) {
  if (!minutes || minutes < 1) return '*/30 * * * *'
  return `*/${minutes} * * * *`
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
    const config = {
      target_url: form.targetUrl,
      cron_expr: minutesToCron(form.intervalMinutes),
      concurrency: form.concurrency,
      interval_seconds: form.intervalSeconds,
      max_retries: form.maxRetries,
      crawl_mode: form.crawlMode
    }

    const res = await taskAPI.createTask({
      name: form.name,
      task_type: form.taskType,
      config: config,
      description: form.description
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
</script>

<style scoped>
.task-new-page {
  min-height: 100vh;
  background-color: #0d1117;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.018) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.018) 1px, transparent 1px);
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
  margin-bottom: 32px;
}

.btn-back {
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(22, 27, 34, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.25s ease;
}

.btn-back:hover {
  color: rgba(255, 255, 255, 0.85);
  border-color: rgba(255, 255, 255, 0.15);
}

.btn-back svg {
  width: 20px;
  height: 20px;
}

.new-title {
  font-size: 24px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
}

.config-form {
  background: rgba(22, 27, 34, 0.55);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.06);
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
  color: rgba(255, 255, 255, 0.4);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-input {
  width: 100%;
  padding: 11px 16px;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.85);
  outline: none;
  transition: all 0.25s ease;
}

.form-input:focus {
  border-color: rgba(76, 110, 245, 0.4);
  box-shadow: 0 0 0 3px rgba(76, 110, 245, 0.08);
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.2);
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
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.25s ease;
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.6);
}

.action-btn.primary {
  background: linear-gradient(135deg, #4c6ef5, #7c3aed);
  color: #fff;
  border: none;
  box-shadow: 0 4px 14px rgba(76, 110, 245, 0.3);
}

.action-btn.primary:hover {
  box-shadow: 0 6px 20px rgba(76, 110, 245, 0.45);
  transform: translateY(-1px);
}

.action-btn.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.action-btn.cancel:hover {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.75);
}

@media (max-width: 768px) {
  .new-content { padding: 24px 16px 64px; }
  .form-row { grid-template-columns: 1fr; }
}
</style>
