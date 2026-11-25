<template>
  <div class="br-config">
    <div class="br-card">
      <div class="br-head">
        <h1>批量改名 - 插件配置</h1>
        <span class="br-close" @click="emit('close')">✕</span>
      </div>
      <div class="br-body">
        <div class="br-info"><span class="br-i">i</span>
          <div>只需填写剧集目录，扩展名默认 <b>MP4, MKV, SRT, ASS</b>。保存后到插件详情页点「预览改名」，勾选要处理的文件再批量修改。改名规则：保留原标题，季号统一替换，集号按你填的起始集连续递增，「第 XX 集」自动跟随新集号。</div>
        </div>
        <div class="br-field">
          <label>剧集目录（MoviePilot 容器内的绝对路径）</label>
          <input type="text" v-model="config.source_dir" placeholder="例如 /mdeia/动画/Re：从零开始的异世界生活">
          <div class="br-hint">填写容器内部路径，不是宿主机路径</div>
        </div>
        <div class="br-field">
          <label>处理扩展名（逗号分隔）</label>
          <input type="text" v-model="config.extensions">
          <div class="br-hint">只有这些类型的文件会显示在预览列表中</div>
        </div>
        <div class="br-row-actions">
          <button class="br-link-btn" @click="toast('配置数据由 MoviePilot 统一管理')">▤ 查看数据</button>
          <button class="br-save-btn" :disabled="saving" @click="save">▣ 保存</button>
        </div>
      </div>
    </div>
    <div class="br-toast" :class="{ show: toastText }">{{ toastText }}</div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'

const props = defineProps({
  initialConfig: { type: Object, default: () => ({}) },
  api: { type: Object, default: () => ({}) },
})
const emit = defineEmits(['save', 'close'])
const saving = ref(false)
const toastText = ref('')

const config = reactive({
  source_dir: '/mdeia',
  extensions: 'MP4, MKV, SRT, ASS',
})

onMounted(() => {
  const initial = props.initialConfig || {}
  if ('source_dir' in initial) config.source_dir = initial.source_dir || '/mdeia'
  if ('extensions' in initial) config.extensions = initial.extensions || 'MP4, MKV, SRT, ASS'
})

function save() {
  saving.value = true
  try {
    emit('save', {
      enabled: true,
      source_dir: String(config.source_dir || '').trim(),
      extensions: String(config.extensions || '').trim(),
      season: Number((props.initialConfig || {}).season || 1),
      start_episode: Number((props.initialConfig || {}).start_episode || 1),
    })
    toast('配置已保存')
  } finally {
    saving.value = false
  }
}

let toastTimer
function toast(message) {
  toastText.value = message
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toastText.value = '' }, 2400)
}
</script>

<style scoped>
.br-config {
  --primary:#7B5CE8;--primary-dark:#6847d8;--info-bg:#e7f1fd;--info-border:#b9d9fb;
  --info-text:#1b6fc4;--text:#2b2f38;--muted:#6b7280;--line:#e4e7ec;--bg:#f4f6fa;
  --card:#ffffff;
  font-family:"PingFang SC","Microsoft YaHei",-apple-system,"Segoe UI",sans-serif;
  color:var(--text);padding:8px 4px 24px;-webkit-font-smoothing:antialiased;
}
.br-card{background:var(--card);border:1px solid var(--line);border-radius:14px;
  box-shadow:0 8px 30px rgba(30,41,59,.06);overflow:hidden;}
.br-head{display:flex;align-items:center;justify-content:space-between;
  padding:20px 26px 18px;border-bottom:1px solid var(--line);}
.br-head h1{font-size:20px;font-weight:600;letter-spacing:.2px;margin:0}
.br-close{color:#9aa1ad;font-size:24px;line-height:1;cursor:pointer}
.br-body{padding:24px 26px 26px}
.br-info{display:flex;gap:12px;background:var(--info-bg);border:1px solid var(--info-border);
  color:var(--info-text);border-radius:10px;padding:15px 18px;margin-bottom:24px;font-size:14px;line-height:1.75;}
.br-i{flex:0 0 22px;height:22px;border:2px solid var(--info-text);border-radius:50%;
  display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;margin-top:1px;}
.br-field{margin-bottom:22px;position:relative}
.br-field label{display:block;font-size:13px;color:var(--muted);margin:0 0 8px 2px}
.br-field input{width:100%;padding:14px 15px;border:1px solid #d5dae2;border-radius:10px;
  font-size:15px;color:var(--text);background:#fff;transition:.18s;outline:none;font-family:inherit;box-sizing:border-box;}
.br-field input:focus{border-color:var(--primary);box-shadow:0 0 0 3px rgba(123,92,232,.12)}
.br-hint{font-size:12px;color:#9aa1ad;margin-top:7px}
.br-row-actions{display:flex;align-items:center;justify-content:space-between;margin-top:8px}
.br-link-btn{background:#eef1f7;color:#5b6270;border:0;border-radius:9px;padding:11px 18px;
  font-size:14px;cursor:pointer;display:inline-flex;align-items:center;gap:7px;font-family:inherit;}
.br-link-btn:hover{background:#e6eaf2}
.br-save-btn{background:var(--primary);color:#fff;border:0;border-radius:10px;padding:12px 26px;
  font-size:15px;cursor:pointer;font-weight:500;box-shadow:0 4px 14px rgba(123,92,232,.28);
  display:inline-flex;align-items:center;gap:8px;font-family:inherit;}
.br-save-btn:hover{background:var(--primary-dark)}
.br-save-btn:disabled{opacity:.5;cursor:not-allowed}
.br-toast{position:fixed;left:50%;bottom:34px;transform:translateX(-50%) translateY(20px);
  background:#2b2f38;color:#fff;padding:12px 24px;border-radius:10px;font-size:14px;
  opacity:0;pointer-events:none;transition:.25s;box-shadow:0 8px 24px rgba(0,0,0,.2);z-index:99;}
.br-toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
</style>
