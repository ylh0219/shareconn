<script setup>
import { ref } from 'vue'
import ShareForm from './components/ShareForm.vue'
import ResultCard from './components/ResultCard.vue'
import { submitShare, getShareResult, createProgressSocket } from './api'

const currentShare = ref(null)
const currentProgress = ref(null)

const activeSocket = ref(null)

const handleNewShare = async (url, done) => {
  try {
    currentShare.value = null;
    currentProgress.value = null;
    
    // 1. Submit link
    // Normally we should register a user or pass token. 
    // Here we'll just omit user logic or mock it since auth requires token in backend.
    // Wait, the backend requires authentication for POST /shares.
    // I should mock auth or handle it gracefully if token is absent.
    // Wait... if API fails due to auth I can show auth token mockup.
    
    const taskData = await submitShare(url);
    const shareId = taskData.share_id;
    
    currentShare.value = {
      id: shareId,
      status: 'pending',
      raw_input: url
    }
    
    // 2. Connect WebSocket to stream progress
    if (activeSocket.value) {
      activeSocket.value.close();
    }
    
    activeSocket.value = createProgressSocket(shareId, (data) => {
      currentProgress.value = {
        step: data.step,
        message: data.message
      }
      
      // If completed or failed, fetch result
      if (data.step === 'analyzed' || data.step === 'analysis_failed') {
        activeSocket.value.close();
        activeSocket.value = null;
        fetchResult(shareId);
      }
    });
    
    // Fallback Polling since Celery worker cannot currently push to the FastAPI websocket memory.
    const pollInterval = setInterval(async () => {
      try {
        const data = await getShareResult(shareId);
        const s = (data.status || '').toLowerCase();
        if (s === 'completed' || s === 'failed') {
          clearInterval(pollInterval);
          if (activeSocket.value) {
            activeSocket.value.close();
            activeSocket.value = null;
          }
          currentShare.value = data;
          currentProgress.value = null;
        }
      } catch (e) {
        // ignore polling errors
      }
    }, 2500);
    
  } catch(e) {
    alert("请求提交失败, 请检查控制台日志。注意：当前API需要认证 (401)，您可能需要配置模拟Token。")
    console.error(e)
  } finally {
    if (done) done()
  }
}

const fetchResult = async (shareId) => {
  try {
    const data = await getShareResult(shareId);
    currentShare.value = data;
    currentProgress.value = null;
  } catch (e) {
    console.error("Failed to fetch result", e)
    currentShare.value.status = 'failed';
    currentShare.value.error_message = e.response?.data?.detail || "无法获取最终结果";
  }
}

// Intercept Axios to mockup a fake token auth if not logged in.
// Actually since the backend requires it, I'll pass a mockup in api.js.
</script>

<template>
  <div class="app-wrapper">
    <header class="app-header">
      <div class="logo-box">
        <div class="logo-circle">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" x2="15.42" y1="13.51" y2="17.49"/><line x1="15.41" x2="8.59" y1="6.51" y2="10.49"/></svg>
        </div>
        <h1>Share Helper</h1>
      </div>
      <p class="subtitle">您的个人智能内容管理核心</p>
    </header>

    <main class="main-content">
      <ShareForm @submit="handleNewShare" />
      
      <ResultCard 
        v-if="currentShare" 
        :share="currentShare" 
        :progress="currentProgress" 
      />
    </main>
  </div>
</template>

<style scoped>
.app-wrapper {
  max-width: 800px;
  margin: 0 auto;
}

.app-header {
  text-align: center;
  margin-bottom: 3rem;
  animation: fadeIn 0.8s ease-out;
}

.logo-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 10px;
}

.logo-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--accent-1));
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
}

.logo-circle svg {
  color: white;
}

h1 {
  font-size: 3rem;
  margin: 0;
  letter-spacing: -1px;
}

.subtitle {
  color: var(--text-muted);
  font-size: 1.1rem;
}
</style>
