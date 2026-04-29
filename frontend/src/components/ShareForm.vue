<script setup>
import { ref } from 'vue'
import { Link2Icon, SendIcon, Loader2Icon } from 'lucide-vue-next'

const emit = defineEmits(['submit'])
const urlInput = ref('')
const isSubmitting = ref(false)

const handleSubmit = async () => {
  if (!urlInput.value) return;
  // Basic validation
  if (!urlInput.value.startsWith('http')) {
    alert("请提供完整的 URL。")
    return
  }
  
  isSubmitting.value = true;
  emit('submit', urlInput.value, () => {
    isSubmitting.value = false;
    urlInput.value = ''; // clear on success
  })
}
</script>

<template>
  <div class="glass-panel form-container">
    <div class="form-header">
      <Link2Icon class="icon" />
      <h2>提交新分享</h2>
    </div>
    <p>支持 B站视频、微信公众号文章或通用网页链接。我们会自动解析核心内容并生成摘要分析。</p>
    
    <div class="input-group">
      <input 
        v-model="urlInput"
        type="url" 
        class="input-field" 
        placeholder="https://www.bilibili.com/video/BV..."
        @keyup.enter="handleSubmit"
        :disabled="isSubmitting"
      />
      <button 
        class="btn-primary submit-btn" 
        @click="handleSubmit"
        :disabled="isSubmitting || !urlInput"
      >
        <span v-if="!isSubmitting">解析</span>
        <Loader2Icon v-else class="spin-icon" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.form-container {
  margin-bottom: 2rem;
  animation: fadeIn 0.5s ease-out;
}

.form-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.icon {
  color: var(--primary);
  width: 28px;
  height: 28px;
}

h2 {
  margin: 0;
  font-size: 1.5rem;
}

.input-group {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 120px;
}

.spin-icon {
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@media (max-width: 600px) {
  .input-group {
    flex-direction: column;
  }
  .submit-btn {
    width: 100%;
  }
}
</style>
