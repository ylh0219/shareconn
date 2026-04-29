<script setup>
import { computed } from 'vue'
import { 
  FileTextIcon, ClockIcon, AlertCircleIcon, 
  LightbulbIcon, HistoryIcon, ExternalLinkIcon, CheckCircle2Icon
} from 'lucide-vue-next'

const props = defineProps({
  share: {
    type: Object,
    required: true
  },
  progress: {
    type: Object,
    default: null
  }
})

// Extract core analysis
const analysisOk = computed(() => props.share.status === 'completed' && props.share.theme != null)
const hasProgress = computed(() => props.progress != null && props.share.status !== 'completed' && props.share.status !== 'failed')

const platformName = computed(() => {
  const map = {
    'bilibili': '哔哩哔哩',
    'wechat': '微信公众号',
    'generic': '通用网页'
  }
  return map[props.share.source_platform] || props.share.source_platform || '未知平台'
})

</script>

<template>
  <div class="glass-panel result-card">
    <div v-if="share.status === 'failed'" class="error-state">
      <AlertCircleIcon class="error-icon" />
      <h3>处理失败</h3>
      <p>{{ share.error_message || '未知错误' }}</p>
    </div>
    
    <div v-else-if="hasProgress" class="progress-state">
      <div class="spinner"></div>
      <h3>正在处理中</h3>
      <p class="progress-step">{{ progress.message || '正在排队...' }}</p>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progress.step === 'classified' ? '30%' : progress.step === 'parsed' ? '60%' : '80%' }"></div>
      </div>
    </div>
    
    <div v-else-if="analysisOk" class="analysis-state">
      <!-- Header Info -->
      <div class="result-header">
        <div class="badges">
          <span class="badge platform-badge">{{ platformName }}</span>
          <span class="badge time-badge"><ClockIcon class="icon-sm"/> 约 {{ share.estimated_time_minutes }} 分钟</span>
        </div>
        <a v-if="share.raw_input" :href="share.raw_input" target="_blank" class="original-link">
          查看原文 <ExternalLinkIcon class="icon-sm"/>
        </a>
      </div>
      
      <!-- Titles -->
      <h2 class="title">{{ share.parsed_title || share.theme || '无标题内容' }}</h2>
      <p v-if="share.parsed_author" class="author">作者: {{ share.parsed_author }}</p>
      <p v-else-if="share.theme" class="author">主题: {{ share.theme }}</p>

      <div class="separator"></div>

      <!-- Core Summary -->
      <div class="section-block summary-block">
        <h3><FileTextIcon class="icon"/> AI 智能摘要</h3>
        <p class="summary-text">{{ share.summary }}</p>
      </div>

      <!-- Metrics -->
      <div class="metrics-grid">
        <div class="metric-card imp-card">
          <div class="metric-val">{{ share.importance }}<span class="max-val">/10</span></div>
          <div class="metric-label">重要性评分</div>
        </div>
        <div class="metric-card urg-card">
          <div class="metric-val">{{ share.urgency }}<span class="max-val">/10</span></div>
          <div class="metric-label">紧急程度</div>
        </div>
      </div>

      <!-- History Context if any -->
      <div v-if="share.related_past_shares && share.related_past_shares.length" class="section-block history-block">
        <h3><HistoryIcon class="icon"/> 历史记忆关联</h3>
        <ul class="history-list">
          <li v-for="(item, idx) in share.related_past_shares" :key="idx">
            <CheckCircle2Icon class="list-icon" /> {{ item }}
          </li>
        </ul>
      </div>
    </div>
    
    <div v-else class="pending-state">
      等待处理...
    </div>
  </div>
</template>

<style scoped>
.result-card {
  animation: fadeIn 0.6s ease-out;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.badges {
  display: flex;
  gap: 12px;
}

.badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.platform-badge {
  background: rgba(99, 102, 241, 0.2);
  color: #818cf8;
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.time-badge {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.original-link {
  color: var(--text-muted);
  text-decoration: none;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: color 0.2s;
}

.original-link:hover {
  color: var(--text-main);
}

.icon-sm {
  width: 16px;
  height: 16px;
}

.icon {
  width: 20px;
  height: 20px;
  color: var(--primary);
}

.title {
  font-size: 1.8rem;
  margin-bottom: 8px;
  line-height: 1.3;
}

.author {
  color: #94a3b8;
  font-size: 1rem;
  margin-bottom: 24px;
}

.separator {
  height: 1px;
  background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0) 100%);
  margin: 30px 0;
}

.section-block h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.2rem;
  margin-bottom: 16px;
}

.summary-text {
  font-size: 1.05rem;
  text-align: justify;
}

.metrics-grid {
  display: flex;
  gap: 20px;
  margin: 30px 0;
}

.metric-card {
  flex: 1;
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.metric-val {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--text-main);
  line-height: 1;
  margin-bottom: 8px;
}

.max-val {
  font-size: 1.2rem;
  color: var(--text-muted);
  font-weight: 500;
}

.metric-label {
  font-size: 0.9rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.imp-card .metric-val { color: #f472b6; }
.urg-card .metric-val { color: #fbbf24; }

.history-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.history-list li {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: rgba(255,255,255,0.03);
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 10px;
  color: var(--text-muted);
}

.list-icon {
  width: 18px;
  height: 18px;
  color: var(--primary);
  flex-shrink: 0;
  margin-top: 2px;
}

/* Progress State */
.progress-state, .error-state {
  text-align: center;
  padding: 40px 0;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 3px solid rgba(255,255,255,0.1);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin { 100% { transform: rotate(360deg); } }

.progress-step {
  color: var(--primary);
  font-weight: 500;
  margin-bottom: 20px;
}

.progress-bar {
  width: 60%;
  height: 6px;
  background: rgba(255,255,255,0.1);
  border-radius: 10px;
  margin: 0 auto;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--accent-1));
  border-radius: 10px;
  transition: width 0.5s ease;
}

.error-icon {
  width: 50px;
  height: 50px;
  color: #ef4444;
  margin-bottom: 20px;
}

.error-state h3 { color: #ef4444; }

@media (max-width: 600px) {
  .result-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .metrics-grid { flex-direction: column; }
}
</style>
