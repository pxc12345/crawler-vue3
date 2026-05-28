<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h2>{{ isEdit ? '编辑学生' : '添加学生' }}</h2>
        <button class="modal-close" @click="$emit('close')">×</button>
      </div>

      <div class="modal-body">
        <div class="avatar-upload">
          <div class="avatar-preview" @click="triggerFileInput">
            <img v-if="avatarPreview" :src="avatarPreview" alt="avatar" />
            <span v-else-if="formData.avatar_url">{{ formData.name.charAt(0) }}</span>
            <span v-else class="placeholder">+</span>
          </div>
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            style="display: none"
            @change="handleFileChange"
          />
          <div class="avatar-hint">点击上传头像</div>
        </div>

        <div class="form-group">
          <label>姓名 *</label>
          <input
            v-model="formData.name"
            type="text"
            placeholder="请输入姓名"
            :class="{ error: errors.name }"
          />
          <div v-if="errors.name" class="error-text">{{ errors.name }}</div>
        </div>

        <div class="form-group">
          <label>年龄 *</label>
          <input
            v-model.number="formData.age"
            type="number"
            placeholder="请输入年龄 (1-150)"
            :class="{ error: errors.age }"
          />
          <div v-if="errors.age" class="error-text">{{ errors.age }}</div>
        </div>

        <div class="form-group">
          <label>成绩 *</label>
          <input
            v-model.number="formData.grade"
            type="number"
            placeholder="请输入成绩 (0-100)"
            :class="{ error: errors.grade }"
          />
          <div v-if="errors.grade" class="error-text">{{ errors.grade }}</div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn btn-cancel" @click="$emit('close')">取消</button>
        <button class="btn btn-primary" :disabled="uploading" @click="handleSubmit">
          {{ uploading ? '上传中...' : (isEdit ? '保存' : '添加') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { studentApi } from '../api/student.js'
import { API_ORIGIN } from '../config/api'

const props = defineProps({
  student: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'submit'])

const isEdit = computed(() => !!props.student)

const formData = ref({
  name: '',
  age: '',
  grade: '',
  avatar_url: ''
})

const errors = ref({
  name: '',
  age: '',
  grade: ''
})

const avatarPreview = ref('')
const uploading = ref(false)
const fileInput = ref(null)

watch(() => props.student, (newVal) => {
  if (newVal) {
    formData.value = {
      name: newVal.name || '',
      age: newVal.age || '',
      grade: newVal.grade || '',
      avatar_url: newVal.avatar_url || ''
    }
    avatarPreview.value = newVal.avatar_url ? getFullUrl(newVal.avatar_url) : ''
  } else {
    formData.value = { name: '', age: '', grade: '', avatar_url: '' }
    avatarPreview.value = ''
  }
  errors.value = { name: '', age: '', grade: '' }
}, { immediate: true })

function getFullUrl(url) {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `${API_ORIGIN}${url}`
}

function triggerFileInput() {
  fileInput.value.click()
}

async function handleFileChange(event) {
  const file = event.target.files[0]
  if (!file) return

  if (!file.type.startsWith('image/')) {
    alert('请选择图片文件')
    return
  }

  if (file.size > 5 * 1024 * 1024) {
    alert('图片大小不能超过 5MB')
    return
  }

  avatarPreview.value = URL.createObjectURL(file)
  uploading.value = true

  try {
    const res = await studentApi.uploadFile(file)
    if (res.code === 200) {
      formData.value.avatar_url = res.data.url
    } else {
      alert(res.message)
      avatarPreview.value = formData.value.avatar_url ? getFullUrl(formData.value.avatar_url) : ''
    }
  } catch (e) {
    alert('上传失败: ' + e.message)
    avatarPreview.value = formData.value.avatar_url ? getFullUrl(formData.value.avatar_url) : ''
  } finally {
    uploading.value = false
  }

  event.target.value = ''
}

function validate() {
  let isValid = true
  errors.value = { name: '', age: '', grade: '' }

  if (!formData.value.name || !formData.value.name.trim()) {
    errors.value.name = '姓名不能为空'
    isValid = false
  }

  const age = formData.value.age
  if (!age || age < 1 || age > 150) {
    errors.value.age = '年龄必须在 1-150 之间'
    isValid = false
  }

  const grade = formData.value.grade
  if (grade === '' || grade < 0 || grade > 100) {
    errors.value.grade = '成绩必须在 0-100 之间'
    isValid = false
  }

  return isValid
}

async function handleSubmit() {
  if (!validate()) return

  try {
    await emit('submit', {
      name: formData.value.name.trim(),
      age: Number(formData.value.age),
      grade: Number(formData.value.grade),
      avatar_url: formData.value.avatar_url || null
    })
  } catch (e) {
    console.error('提交失败:', e)
  }
}
</script>