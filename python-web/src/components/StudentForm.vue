<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h2>{{ isEdit ? '✏️ 编辑学生' : '➕ 添加学生' }}</h2>
        <button class="modal-close" @click="$emit('close')">×</button>
      </div>

      <div class="modal-body">
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
        <button class="btn" @click="$emit('close')">取消</button>
        <button class="btn btn-success" @click="handleSubmit">
          {{ isEdit ? '💾 保存' : '✅ 添加' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

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
  grade: ''
})

const errors = ref({
  name: '',
  age: '',
  grade: ''
})

watch(() => props.student, (newVal) => {
  if (newVal) {
    formData.value = { ...newVal }
  } else {
    formData.value = { name: '', age: '', grade: '' }
  }
  errors.value = { name: '', age: '', grade: '' }
}, { immediate: true })

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
    await emit('submit', { ...formData.value })
  } catch (e) {
    console.error('提交失败:', e)
  }
}
</script>
