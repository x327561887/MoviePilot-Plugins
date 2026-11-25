<template>
  <div class="br-page">
    <div class="br-card">
      <div class="br-head">
        <h1>批量改名 - 插件详情</h1>
        <span class="br-close" @click="emit('close')">✕</span>
      </div>
      <div class="br-body">
        <div class="br-toolbar">
          <div class="br-param">
            <label>目标季号 SXX</label>
            <input type="number" v-model.number="season" min="0" max="99" @input="refreshPreview">
          </div>
          <div class="br-param">
            <label>起始集号（当前）</label>
            <input type="number" v-model.number="start" min="1" max="9999" @input="refreshPreview">
          </div>
          <div class="br-param">
            <label>修改集数（目标）</label>
            <input type="number" v-model.number="target" min="1" max="9999" @input="refreshPreview">
          </div>
          <button class="br-btn primary" :disabled="loading" @click="preview">
            🔍 {{ loading ? '扫描中…' : '预览改名' }}
          </button>
          <button class="br-btn ghost" @click="emit('switch')">⚙ 修改目录设置</button>
        </div>

        <div class="br-rule">
          当前目录：<b>{{ sourceLabel }}</b><br>
          改名规则：<b>S{{ pad(season) }}</b>（所有季号统一替换）；
          <b>起始集号 E{{ start }}</b> 是改名起点（目录中须存在该集，否则全部「不匹配」）；
          集号 <b>小于 {{ start }}</b> 的文件标记「不匹配」不参与；
          集号 <b>≥ {{ start }}</b> 的从 <b>E{{ target }}</b> 起累加，即 <b>新集号 = {{ target }} +（原集号 − {{ start }}）</b>（例：E{{ start }}→E{{ target }}、E{{ start + 1 }}→E{{ target + 1 }}）；
          <b>「第 XX 集」按新集号自动改写</b>。
        </div>

        <div class="br-alert error" v-if="error">{{ error }}</div>

        <div v-if="hasPreview">
          <div class="br-summary">
            <span class="br-pill">{{ summary.generated_at }}</span>
            <span class="br-pill">共 {{ summary.total }} 个媒体文件</span>
            <span class="br-pill">待改名 {{ summary.ready }}</span>
            <span class="br-pill">已存在 {{ summary.exist }}</span>
            <span class="br-pill">不匹配 {{ summary.unmatched }}</span>
          </div>
          <div class="br-table-wrap">
            <table>
              <thead><tr>
                <th style="width:46px"><input type="checkbox" class="br-chk" :checked="allChecked" :disabled="readyIndexes.length===0" @change="toggleAll($event.target.checked)"></th>
                <th style="width:96px">状态</th>
                <th>原文件名</th>
                <th style="width:30px"></th>
                <th>修改后文件名</th>
              </tr></thead>
              <tbody>
                <tr v-for="(item, i) in items" :key="item.old_name">
                  <td><input type="checkbox" class="br-chk" :checked="selected.has(item.old_name)" :disabled="item.status!=='ready'" @change="toggleOne(item.old_name, $event.target.checked)"></td>
                  <td><span class="br-tag" :class="statusClass(item.status)">{{ statusText(item.status) }}</span></td>
                  <td><span class="br-fname" :class="{ dim: item.status==='exist'||item.status==='unmatched' }">{{ item.old_name }}</span></td>
                  <td><span class="br-arrow">→</span></td>
                  <td><span class="br-fname new" v-if="item.status==='ready'">{{ item.new_name }}</span><span class="br-fname dim" v-else-if="item.status==='unmatched'">不匹配（不修改）</span><span class="br-fname dim" v-else>已是目标名</span></td>
                </tr>
                <tr v-if="items.length===0"><td colspan="5" style="text-align:center;color:#9aa1ad;padding:24px">没有可显示的文件</td></tr>
              </tbody>
            </table>
          </div>
          <div class="br-bottom-bar">
            <div class="br-selected-count">已选择 <b>{{ selectedReadyCount }}</b> 个文件</div>
            <div class="br-btn-group">
              <button class="br-btn ghost" :disabled="!canUndo" @click="undo">↩ 恢复上次改名</button>
              <button class="br-btn go" :disabled="selectedReadyCount===0 || applying" @click="apply">
                ✓ {{ applying ? '执行中…' : '执行批量改名' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="br-toast" :class="{ show: toastText }">{{ toastText }}</div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

const props = defineProps({
  model: { type: Object, default: () => ({}) },
  api: { type: Object, default: () => ({}) },
  pluginId: { type: String, default: 'BatchRename' },
})
const emit = defineEmits(['close', 'switch'])

const season = ref(Number((props.model || {}).season || 1))
const start = ref(Number((props.model || {}).start_episode || 1))
const target = ref(Number((props.model || {}).target_episode || 1))
const sourceLabel = ref((props.model || {}).source_dir || '')

const loading = ref(false)
const applying = ref(false)
const error = ref('')
const hasPreview = ref(false)
const items = ref([])
const summary = reactive({ generated_at: '', total: 0, ready: 0, exist: 0, unmatched: 0 })
const selected = ref(new Set())
const canUndo = ref(false)
const toastText = ref('')

const readyIndexes = computed(() => items.value.filter(i => i.status === 'ready').map(i => i.old_name))
const allChecked = computed(() => readyIndexes.value.length > 0 && readyIndexes.value.every(n => selected.value.has(n)))
const selectedReadyCount = computed(() => readyIndexes.value.filter(n => selected.value.has(n)).length)

function pad(value) { return String(value || 0).padStart(2, '0') }
function statusText(status) {
  return { ready: '待修改', exist: '已存在', unmatched: '不匹配', conflict: '跳过', done: '已改名' }[status] || status
}
function statusClass(status) {
  return { ready: 'wait', exist: 'exist', unmatched: 'unmatched', conflict: 'conflict', done: 'done' }[status] || 'wait'
}

function unwrap(response) {
  if (!response || typeof response !== 'object') return response
  if ('success' in response && 'data' in response) {
    if (!response.success) throw new Error(response.message || '请求失败')
    return response.data
  }
  return response
}

async function callApi(path, method = 'get', payload) {
  const api = props.api || {}
  if (method === 'get') {
    if (typeof api.get === 'function') return unwrap(await api.get(path, payload))
    if (typeof api.request === 'function') return unwrap(await api.request({ url: path, method: 'get', params: payload }))
  } else {
    if (typeof api.post === 'function') return unwrap(await api.post(path, payload))
    if (typeof api.request === 'function') return unwrap(await api.request({ url: path, method: 'post', data: payload }))
  }
  throw new Error('主应用未注入 API 客户端，请确认插件已启用')
}

const apiPrefix = computed(() => `plugin/${props.pluginId || 'BatchRename'}`)

async function preview() {
  loading.value = true
  error.value = ''
  try {
    const data = await callApi(`${apiPrefix.value}/preview`, 'post', {
      season: Number(season.value) || 0,
      start: Number(start.value) || 1,
      target: Number(target.value) || 1,
    })
    items.value = data.items || []
    summary.generated_at = data.generated_at || ''
    summary.total = Number(data.total_count || 0)
    summary.ready = Number(data.ready_count || 0)
    summary.exist = Number(data.exist_count || 0)
    summary.unmatched = Number(data.unmatched_count || 0)
    selected.value = new Set(items.value.filter(i => i.status === 'ready').map(i => i.old_name))
    hasPreview.value = true
    const extra = data.anchor_exists === false ? '；起始集号在目录中不存在，全部不匹配' : ''
    toast(`已扫描到 ${summary.total} 个文件，${summary.ready} 个待改名、${summary.unmatched} 个不匹配${extra}`)
  } catch (err) {
    error.value = err?.message || String(err)
    toast(error.value)
  } finally {
    loading.value = false
  }
}

let previewTimer
function refreshPreview() {
  clearTimeout(previewTimer)
  previewTimer = setTimeout(() => { if (hasPreview.value) preview() }, 350)
}

function toggleAll(on) {
  const next = new Set(selected.value)
  readyIndexes.value.forEach(name => { if (on) next.add(name); else next.delete(name) })
  selected.value = next
}
function toggleOne(name, on) {
  const next = new Set(selected.value)
  if (on) next.add(name); else next.delete(name)
  selected.value = next
}

async function apply() {
  const names = readyIndexes.value.filter(n => selected.value.has(n))
  if (!names.length) return
  applying.value = true
  error.value = ''
  try {
    const data = await callApi(`${apiPrefix.value}/apply`, 'post', {
      season: Number(season.value) || 0,
      start: Number(start.value) || 1,
      target: Number(target.value) || 1,
      names,
    })
    toast(data?.message || `已完成批量改名，共处理 ${names.length} 个文件`)
    canUndo.value = true
    await preview()
  } catch (err) {
    error.value = err?.message || String(err)
    toast(error.value)
  } finally {
    applying.value = false
  }
}

async function undo() {
  applying.value = true
  error.value = ''
  try {
    const data = await callApi(`${apiPrefix.value}/undo`, 'post', {})
    toast(data?.message || '已恢复上次改名')
    canUndo.value = false
    await preview()
  } catch (err) {
    error.value = err?.message || String(err)
    toast(error.value)
  } finally {
    applying.value = false
  }
}

onMounted(async () => {
  // 主程序通过 api 注入插件客户端；拉取配置以填充输入框与当前目录显示。
  // 详情页不自动扫描：用户点「预览改名」后再列出文件，与原原型一致。
  try {
    const cfg = await callApi(`${apiPrefix.value}/config`, 'get')
    if (cfg) {
      if (cfg.season != null) season.value = Number(cfg.season)
      if (cfg.start_episode != null) start.value = Number(cfg.start_episode)
      if (cfg.target_episode != null) target.value = Number(cfg.target_episode)
      if (cfg.source_dir) sourceLabel.value = cfg.source_dir
    }
  } catch (err) {
    // 拉取失败不影响手动输入
  }
})

let toastTimer
function toast(message) {
  toastText.value = message
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toastText.value = '' }, 2800)
}
</script>

<style scoped>
.br-page {
  --primary:#7B5CE8;--primary-dark:#6847d8;--info-bg:#e7f1fd;--info-border:#b9d9fb;
  --info-text:#1b6fc4;--text:#2b2f38;--muted:#6b7280;--line:#e4e7ec;--bg:#f4f6fa;
  --card:#ffffff;--ok:#2e9e5b;--warn:#e08a1e;
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
.br-toolbar{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:20px}
.br-param{display:flex;flex-direction:column;gap:5px;background:#fff;border:1px solid #d5dae2;
  border-radius:10px;padding:7px 12px 8px;min-width:112px;}
.br-param label{font-size:12px;color:var(--muted)}
.br-param input{border:0;outline:none;font-size:16px;color:var(--primary-dark);font-weight:600;
  width:92px;background:transparent;font-family:inherit;padding:0;-moz-appearance:textfield;}
.br-param input::-webkit-outer-spin-button,.br-param input::-webkit-inner-spin-button{-webkit-appearance:none;margin:0}
.br-btn{border:0;border-radius:9px;padding:11px 20px;font-size:14px;cursor:pointer;font-weight:500;
  display:inline-flex;align-items:center;gap:8px;font-family:inherit;transition:.18s;}
.br-btn.primary{background:var(--primary);color:#fff;box-shadow:0 4px 14px rgba(123,92,232,.25)}
.br-btn.primary:hover{background:var(--primary-dark)}
.br-btn.go{background:var(--ok);color:#fff}.br-btn.go:hover{background:#278a50}
.br-btn.ghost{background:#eef1f7;color:#5b6270}.br-btn.ghost:hover{background:#e6eaf2}
.br-btn:disabled{opacity:.45;cursor:not-allowed;box-shadow:none}
.br-rule{background:#f7f8fb;border:1px dashed #d7dce5;border-radius:9px;padding:12px 16px;
  font-size:13px;color:var(--muted);margin-bottom:18px;line-height:1.8;}
.br-rule b{color:var(--text)}
.br-alert{background:#fdecec;border:1px solid #f5c2c2;color:#c0392b;border-radius:9px;
  padding:12px 16px;font-size:13px;margin-bottom:18px;line-height:1.6}
.br-summary{display:flex;align-items:center;gap:10px;font-size:13px;color:var(--muted);
  margin-bottom:12px;flex-wrap:wrap;}
.br-pill{background:#eef1f7;border-radius:20px;padding:5px 13px}
.br-table-wrap{border:1px solid var(--line);border-radius:11px;overflow:auto;max-height:560px}
table{width:100%;border-collapse:collapse;font-size:13.5px}
thead th{background:#f7f8fb;text-align:left;padding:12px 14px;color:var(--muted);
  font-weight:500;border-bottom:1px solid var(--line);white-space:nowrap;position:sticky;top:0;z-index:2;}
tbody td{padding:10px 14px;border-bottom:1px solid #f0f2f6;vertical-align:middle}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:#fafbfe}
.br-chk{width:18px;height:18px;accent-color:var(--primary);cursor:pointer}
.br-fname{font-family:"SF Mono",Consolas,monospace;font-size:12.5px;color:#374151;word-break:break-all}
.br-fname.new{color:var(--primary-dark)}
.br-fname.dim{color:#9aa1ad}
.br-arrow{color:#b6bdc9;font-size:17px;padding:0 3px}
.br-tag{display:inline-block;padding:3px 10px;border-radius:20px;font-size:12px;white-space:nowrap}
.br-tag.wait{background:#fff3e0;color:var(--warn)}
.br-tag.done{background:#e7f6ed;color:var(--ok)}
.br-tag.exist{background:#eef1f7;color:#8a90a3}
.br-tag.unmatched{background:#f0f1f3;color:#a0a5ae;border:1px solid #e2e5ea}
.br-tag.conflict{background:#fdecec;color:#c0392b}
.br-bottom-bar{display:flex;align-items:center;justify-content:space-between;margin-top:18px;gap:12px;flex-wrap:wrap}
.br-selected-count{font-size:14px;color:var(--muted)}
.br-selected-count b{color:var(--primary);font-size:17px}
.br-btn-group{display:flex;gap:10px}
.br-toast{position:fixed;left:50%;bottom:34px;transform:translateX(-50%) translateY(20px);
  background:#2b2f38;color:#fff;padding:12px 24px;border-radius:10px;font-size:14px;
  opacity:0;pointer-events:none;transition:.25s;box-shadow:0 8px 24px rgba(0,0,0,.2);z-index:99;}
.br-toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
</style>
