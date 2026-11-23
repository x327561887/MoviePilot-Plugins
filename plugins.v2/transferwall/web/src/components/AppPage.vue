<template>
  <div class="tw-page">
    <v-card variant="outlined" class="tw-panel">
      <v-card-text>
        <div class="tw-heading">
          <div>
            <div class="text-h6">整理海报墙</div>
            <div class="text-caption text-medium-emphasis">
              按媒体聚合整理记录 · 可删除记录、源文件与媒体库文件
            </div>
          </div>
          <v-btn
            icon="mdi-refresh"
            size="small"
            variant="text"
            :loading="state.loading"
            title="刷新"
            @click="loadWall"
          />
        </div>

        <div class="tw-toolbar">
          <v-text-field
            v-model="state.keyword"
            density="compact"
            variant="outlined"
            hide-details
            prepend-inner-icon="mdi-magnify"
            label="搜索标题或路径"
            class="tw-search"
            @keyup.enter="reload"
          />
          <v-select
            v-model="state.status"
            :items="statusOptions"
            density="compact"
            variant="outlined"
            hide-details
            label="状态"
            class="tw-filter"
            @update:model-value="reload"
          />
          <v-select
            v-model="state.mediaType"
            :items="typeOptions"
            density="compact"
            variant="outlined"
            hide-details
            label="类型"
            class="tw-filter"
            @update:model-value="reload"
          />
          <v-btn size="small" variant="tonal" @click="selectCurrentPage">
            {{ allCurrentSelected ? '取消本页' : '全选本页' }}
          </v-btn>
          <v-btn
            size="small"
            color="error"
            variant="tonal"
            :disabled="!state.selected.length"
            prepend-icon="mdi-delete-outline"
            @click="bulkDelete"
          >
            批量删除（{{ state.selected.length }}）
          </v-btn>
        </div>

        <div class="tw-stats">
          <v-chip size="small" variant="tonal">媒体 {{ state.total_groups }}</v-chip>
          <v-chip size="small" variant="tonal">记录 {{ state.total_records }}</v-chip>
          <v-chip v-if="state.truncated" size="small" color="warning" variant="tonal">
            仅显示最近记录
          </v-chip>
        </div>

        <v-alert v-if="state.error || state.localMessage" type="error" variant="tonal" class="tw-alert">
          {{ state.error || state.localMessage }}
        </v-alert>
      </v-card-text>
    </v-card>

    <div v-if="state.loading && !state.groups.length" class="tw-loading">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <div v-else-if="!state.groups.length" class="tw-empty">
      <v-icon size="48">mdi-image-off-outline</v-icon>
      <div class="mt-2">暂无整理记录</div>
    </div>

    <v-row v-else class="tw-grid">
      <v-col
        v-for="group in state.groups"
        :key="group.key"
        cols="6"
        sm="4"
        md="3"
        lg="2"
        xl="2"
        class="tw-cell"
      >
        <v-card class="tw-media-card" variant="outlined" @click="openDetail(group)">
          <div class="tw-poster-wrap">
            <v-img v-if="group.poster" :src="group.poster" cover class="tw-poster" />
            <div v-else class="tw-poster tw-no-poster">
              <v-icon size="40">mdi-image-off-outline</v-icon>
              <span class="tw-no-poster-title">{{ group.title }}</span>
            </div>

            <div class="tw-select-wrap" @click.stop>
              <button
                type="button"
                class="tw-select-box"
                :class="{ 'is-selected': isSelected(group.key) }"
                :title="isSelected(group.key) ? '取消选择' : '选择此媒体'"
                @click="toggleSelect(group.key)"
              >
                <v-icon v-if="isSelected(group.key)" icon="mdi-check" size="x-small" />
              </button>
            </div>

            <div class="tw-overlay">
              <div class="tw-title" :title="group.title">{{ group.title }}</div>
              <div class="tw-meta">
                <span v-if="group.year">{{ group.year }}</span>
                <span v-if="group.type">{{ group.type }}</span>
                <span>{{ group.record_count }} 条</span>
              </div>
              <div class="tw-badges">
                <v-chip size="x-small" color="success" variant="tonal">
                  {{ group.success_count }} 成功
                </v-chip>
                <v-chip v-if="group.fail_count" size="x-small" color="error" variant="tonal">
                  {{ group.fail_count }} 失败
                </v-chip>
                <v-chip v-if="group.src_count" size="x-small" variant="tonal" title="源文件数量">
                  <v-icon start size="x-small">mdi-download</v-icon>{{ group.src_count }}
                </v-chip>
                <v-chip v-if="group.dest_count" size="x-small" variant="tonal" title="媒体库文件数量">
                  <v-icon start size="x-small">mdi-folder-play</v-icon>{{ group.dest_count }}
                </v-chip>
              </div>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <div v-if="state.total_groups > state.page_size" class="tw-pager">
      <v-btn size="small" variant="text" :disabled="state.page <= 1" @click="goPage(state.page - 1)">
        上一页
      </v-btn>
      <span class="text-caption">{{ state.page }} / {{ Math.max(1, Math.ceil(state.total_groups / state.page_size)) }}</span>
      <v-btn
        size="small"
        variant="text"
        :disabled="state.page * state.page_size >= state.total_groups"
        @click="goPage(state.page + 1)"
      >
        下一页
      </v-btn>
    </div>

    <!-- 媒体详情 -->
    <v-dialog v-model="state.detailDialog" max-width="960" scrollable>
      <v-card>
        <v-card-item>
          <v-card-title>{{ state.detail?.title || '整理详情' }}</v-card-title>
          <template #append>
            <v-btn icon="mdi-close" size="small" variant="text" @click="state.detailDialog = false" />
          </template>
        </v-card-item>
        <v-card-text class="tw-detail-body">
          <div class="tw-detail-head">
            <v-img
              v-if="state.detail?.poster"
              :src="state.detail.poster"
              cover
              width="100"
              height="150"
              class="tw-detail-poster"
            />
            <div class="tw-detail-info">
              <div class="text-subtitle-1">{{ state.detail?.year || '未知年份' }} · {{ state.detail?.type || '未分类' }}</div>
              <div class="text-caption text-medium-emphasis">
                {{ state.detail?.record_count || 0 }} 条整理记录
                <span v-if="formatSeasonList(state.detail?.seasons)"> · 季：{{ formatSeasonList(state.detail.seasons) }}</span>
                <span v-if="state.detail?.records_truncated"> · 仅显示最近 200 条</span>
              </div>
              <div class="tw-detail-actions">
                <v-btn size="x-small" variant="tonal" @click="openGroupDelete('仅删除本媒体记录', { record: true, src: false, dest: false })">
                  删除全部记录
                </v-btn>
                <v-btn size="x-small" color="warning" variant="tonal" @click="openGroupDelete('删除本媒体源文件', { record: false, src: true, dest: false })">
                  删除源文件
                </v-btn>
                <v-btn size="x-small" color="error" variant="tonal" @click="openGroupDelete('删除本媒体库文件', { record: false, src: false, dest: true })">
                  删除媒体库文件
                </v-btn>
                <v-btn size="x-small" color="error" variant="flat" @click="openGroupDelete('删除本媒体记录、源文件与媒体库文件', { record: true, src: true, dest: true })">
                  全部删除
                </v-btn>
              </div>
            </div>
          </div>

          <!-- 按季分类 + 整季勾选 -->
          <div v-if="detailSeasonTabs.length > 1" class="tw-season-bar">
            <span class="tw-season-bar-label">按季操作：</span>
            <div class="tw-season-tabs">
              <button
                v-for="tab in detailSeasonTabs"
                :key="tab.key"
                type="button"
                class="tw-season-tab"
                :class="{ active: state.seasonFilter === tab.key }"
                @click="state.seasonFilter = tab.key"
              >
                {{ tab.label }} <span class="tw-season-tab-count">{{ tab.count }}</span>
              </button>
            </div>
            <div class="tw-season-selects">
              <template v-for="tab in detailSeasonTabs" :key="'sel-' + tab.key">
                <div v-if="tab.key !== 'all'" class="tw-season-select-item">
                  <button
                    type="button"
                    class="tw-select-box tw-season-select"
                    :class="{ 'is-selected': isSeasonFullySelected(tab.key) }"
                    :title="`勾选/取消${tab.label}全部记录`"
                    @click="toggleSeasonSelection(tab.key, !isSeasonFullySelected(tab.key))"
                  >
                    <v-icon
                      v-if="isSeasonFullySelected(tab.key)"
                      icon="mdi-check"
                      size="x-small"
                    />
                    <v-icon
                      v-else-if="isSeasonPartiallySelected(tab.key)"
                      icon="mdi-minus"
                      size="x-small"
                    />
                  </button>
                  <span class="text-caption">{{ tab.label }}</span>
                </div>
              </template>
            </div>
          </div>

          <div class="tw-detail-select-bar">
            <button
              type="button"
              class="tw-select-box"
              :class="{ 'is-selected': allFilteredSelected }"
              :title="allFilteredSelected ? '取消全选当前季' : '全选当前季'"
              @click="toggleFilteredSelection(!allFilteredSelected)"
            >
              <v-icon v-if="allFilteredSelected" icon="mdi-check" size="x-small" />
              <v-icon v-else-if="someFilteredSelected" icon="mdi-minus" size="x-small" />
            </button>
            <span class="text-caption">全选当前季（{{ filteredDetailRecords.length }} 条）</span>
            <v-spacer />
            <span class="text-caption text-medium-emphasis tw-selected-count">
              已勾选 {{ state.detailSelected.length }} 条
            </span>
            <v-btn
              size="small"
              color="error"
              variant="flat"
              :disabled="!state.detailSelected.length"
              prepend-icon="mdi-delete-outline"
              @click="deleteSelectedInDetail"
            >
              删除所选（{{ state.detailSelected.length }}）
            </v-btn>
          </div>

          <div
            v-for="record in filteredDetailRecords"
            :key="record.id"
            class="tw-record"
            :class="{ 'is-checked': state.detailSelected.includes(record.id) }"
          >
            <div class="tw-record-top">
              <button
                type="button"
                class="tw-select-box tw-record-select"
                :class="{ 'is-selected': state.detailSelected.includes(record.id) }"
                :title="state.detailSelected.includes(record.id) ? '取消选择' : '选择此记录'"
                @click="toggleDetailSelect(record.id)"
              >
                <v-icon v-if="state.detailSelected.includes(record.id)" icon="mdi-check" size="x-small" />
              </button>
              <v-chip size="x-small" :color="record.status ? 'success' : 'error'" variant="tonal">
                {{ record.status ? '成功' : '失败' }}
              </v-chip>
              <span class="text-caption">{{ record.date || ' unknown date' }}</span>
              <span v-if="formatSeasonEpisode(record.seasons, record.episodes)" class="text-caption tw-season-ep">
                {{ formatSeasonEpisode(record.seasons, record.episodes) }}
              </span>
              <v-spacer />
              <v-btn size="x-small" variant="text" @click="openDelete([record.id], '删除单条整理记录', { record: true, src: false, dest: false })">
                删记录
              </v-btn>
              <v-btn size="x-small" color="warning" variant="text" @click="openDelete([record.id], '删除单条源文件', { record: false, src: true, dest: false })">
                删源
              </v-btn>
              <v-btn size="x-small" color="error" variant="text" @click="openDelete([record.id], '删除单条媒体库文件', { record: false, src: false, dest: true })">
                删库
              </v-btn>
              <v-btn size="x-small" color="error" variant="tonal" @click="openDelete([record.id], '删除单条记录及全部关联文件', { record: true, src: true, dest: true })">
                全删
              </v-btn>
            </div>
            <div class="tw-path"><span class="tw-path-label">源：</span>{{ record.src || '—' }}</div>
            <div class="tw-path"><span class="tw-path-label">库：</span>{{ record.dest || '—' }}</div>
            <div v-if="!record.status && record.errmsg" class="text-caption text-error">
              {{ record.errmsg }}
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- 删除确认 -->
    <v-dialog v-model="state.confirmDialog" max-width="720" persistent>
      <v-card>
        <v-card-item>
          <v-card-title class="tw-confirm-title">确认删除</v-card-title>
        </v-card-item>
        <v-card-text>
          <v-alert type="warning" variant="tonal" class="tw-alert">
            文件删除不可恢复，也不会进入回收站。请确认已停止相关下载/做种任务。
          </v-alert>
          <div class="tw-confirm-summary">
            {{ state.confirmLabel }} · 共 {{ state.confirmIds.length }} 条记录
            <span v-if="state.confirmIds.length > (state.config.max_batch || 20)">
              （将分 {{ Math.ceil(state.confirmIds.length / (state.config.max_batch || 20)) }} 批执行）
            </span>
          </div>
          <div class="tw-path-list">
            <div v-for="record in state.confirmRecords.slice(0, 8)" :key="record.id" class="tw-path-list-item">
              <div class="text-caption font-weight-medium">#{{ record.id }} {{ record.title || '' }}</div>
              <div class="tw-path">源：{{ record.src || '—' }}</div>
              <div class="tw-path">库：{{ record.dest || '—' }}</div>
            </div>
            <div v-if="state.confirmRecords.length > 8" class="text-caption text-medium-emphasis">
              另有 {{ state.confirmRecords.length - 8 }} 条未显示
            </div>
          </div>
          <v-checkbox v-model="state.flags.record" label="删除整理记录" density="compact" hide-details />
          <v-checkbox v-model="state.flags.src" label="删除源文件（下载目录）" density="compact" hide-details color="warning" />
          <v-checkbox v-model="state.flags.dest" label="删除媒体库文件" density="compact" hide-details color="error" />
          <v-text-field
            v-if="needsConfirmText"
            v-model="state.confirmText"
            density="compact"
            variant="outlined"
            hide-details
            class="tw-confirm-input"
            label="请输入「删除」以确认文件删除"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" :disabled="state.busy" @click="state.confirmDialog = false">取消</v-btn>
          <v-btn color="error" variant="flat" :loading="state.busy" @click="executeDelete">确认删除</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, inject, onMounted, reactive } from 'vue'

const props = defineProps({
  api: { type: Object, default: () => ({}) },
  navKey: { type: String, default: 'main' },
  pluginId: { type: String, default: '' },
})

const toast = inject('moviepilot:toast', null)

const statusOptions = [
  { title: '全部', value: 'all' },
  { title: '成功', value: 'success' },
  { title: '失败', value: 'fail' },
]
const typeOptions = [
  { title: '全部类型', value: 'all' },
  { title: '电影', value: 'movie' },
  { title: '电视剧', value: 'tv' },
]

// 季集数据原始值形如 "S02" / "E08"（自带前缀），解析为数字数组
function parseNums(value) {
  if (value === null || value === undefined || value === '') return []
  return String(value)
    .toUpperCase()
    .split(/[^0-9]+/)
    .filter(Boolean)
    .map((part) => Number(part))
    .filter((num) => Number.isFinite(num) && num > 0)
}

// "S02" + "E08" => "第2季第8集"；支持多个季/集
function formatSeasonEpisode(seasons, episodes) {
  const ss = parseNums(seasons)
  const es = parseNums(episodes)
  const parts = []
  if (ss.length) parts.push(ss.length === 1 ? `第${ss[0]}季` : `第${ss.join('、')}季`)
  if (es.length) parts.push(es.length === 1 ? `第${es[0]}集` : `第${es.join('、')}集`)
  return parts.join('')
}

// "S01,S02" => "第1季、第2季"
function formatSeasonList(value) {
  return parseNums(value)
    .map((num) => `第${num}季`)
    .join('、')
}

// 记录归属的季（取第一个季数字），无季返回 'none'
function seasonKeyOf(record) {
  const nums = parseNums(record?.seasons)
  return nums.length ? String(nums[0]) : 'none'
}

function seasonLabelOf(key) {
  return key === 'none' ? '未分季' : `第${key}季`
}

const state = reactive({
  groups: [],
  page: 1,
  page_size: 24,
  total_groups: 0,
  total_records: 0,
  truncated: false,
  keyword: '',
  status: 'all',
  mediaType: 'all',
  loading: false,
  error: '',
  localMessage: '',
  selected: [],
  detail: null,
  detailDialog: false,
  seasonFilter: 'all',
  detailSelected: [],
  confirmDialog: false,
  confirmLabel: '',
  confirmIds: [],
  confirmRecords: [],
  flags: { record: true, src: false, dest: false },
  confirmText: '',
  busy: false,
  config: {
    max_batch: 100,
    default_delete_record: true,
    default_delete_src: false,
    default_delete_dest: false,
  },
})

const apiPrefix = computed(() => `plugin/${props.pluginId || 'TransferWall'}`)
const needsConfirmText = computed(() => Boolean(state.flags.src || state.flags.dest))
const currentKeys = computed(() => state.groups.map((group) => group.key))
const allCurrentSelected = computed(
  () => currentKeys.value.length > 0 && currentKeys.value.every((key) => state.selected.includes(key))
)

// 详情弹窗：按季分类标签
const detailSeasonTabs = computed(() => {
  const records = state.detail?.records || []
  const counts = new Map()
  records.forEach((record) => {
    const key = seasonKeyOf(record)
    counts.set(key, (counts.get(key) || 0) + 1)
  })
  const tabs = [{ key: 'all', label: '全部', count: records.length }]
  ;[...counts.entries()]
    .sort((a, b) => {
      if (a[0] === 'none') return 1
      if (b[0] === 'none') return -1
      return Number(a[0]) - Number(b[0])
    })
    .forEach(([key, count]) => tabs.push({ key, label: seasonLabelOf(key), count }))
  return tabs
})

const filteredDetailRecords = computed(() => {
  const records = state.detail?.records || []
  if (state.seasonFilter === 'all') return records
  return records.filter((record) => seasonKeyOf(record) === state.seasonFilter)
})

const filteredDetailIds = computed(() =>
  filteredDetailRecords.value.map((record) => record.id).filter((id) => id !== null && id !== undefined)
)

const allFilteredSelected = computed(
  () => filteredDetailIds.value.length > 0 && filteredDetailIds.value.every((id) => state.detailSelected.includes(id))
)
const someFilteredSelected = computed(
  () => !allFilteredSelected.value && filteredDetailIds.value.some((id) => state.detailSelected.includes(id))
)

function seasonIds(key) {
  return (state.detail?.records || [])
    .filter((record) => seasonKeyOf(record) === key)
    .map((record) => record.id)
    .filter((id) => id !== null && id !== undefined)
}

function isSeasonFullySelected(key) {
  const ids = seasonIds(key)
  return ids.length > 0 && ids.every((id) => state.detailSelected.includes(id))
}

function isSeasonPartiallySelected(key) {
  const ids = seasonIds(key)
  return !isSeasonFullySelected(key) && ids.some((id) => state.detailSelected.includes(id))
}

function toggleSeasonSelection(key, value) {
  const ids = seasonIds(key)
  if (value === true || (value !== false && !isSeasonFullySelected(key))) {
    ids.forEach((id) => {
      if (!state.detailSelected.includes(id)) state.detailSelected.push(id)
    })
  } else {
    const remove = new Set(ids)
    state.detailSelected = state.detailSelected.filter((id) => !remove.has(id))
  }
}

function toggleDetailSelect(id) {
  const index = state.detailSelected.indexOf(id)
  if (index >= 0) state.detailSelected.splice(index, 1)
  else state.detailSelected.push(id)
}

function toggleFilteredSelection(value) {
  const shouldSelect = value === true || (value !== false && !allFilteredSelected.value)
  const ids = filteredDetailIds.value
  if (shouldSelect) {
    ids.forEach((id) => {
      if (!state.detailSelected.includes(id)) state.detailSelected.push(id)
    })
  } else {
    const remove = new Set(ids)
    state.detailSelected = state.detailSelected.filter((id) => !remove.has(id))
  }
}

function notify(type, message) {
  const fn = toast && typeof toast[type] === 'function' ? toast[type] : null
  if (fn) {
    fn(message)
    return
  }
  state.localMessage = message
  window.setTimeout(() => {
    if (state.localMessage === message) state.localMessage = ''
  }, 6000)
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
    if (typeof api.request === 'function') {
      return unwrap(await api.request({ url: path, method: 'get', params: payload }))
    }
  } else {
    if (typeof api.post === 'function') return unwrap(await api.post(path, payload))
    if (typeof api.request === 'function') {
      return unwrap(await api.request({ url: path, method: 'post', data: payload }))
    }
  }
  throw new Error('主应用未注入 API 客户端，请确认插件已启用')
}

async function loadWall() {
  state.loading = true
  state.error = ''
  try {
    const params = new URLSearchParams()
    params.set('page', String(state.page))
    params.set('page_size', String(state.page_size))
    params.set('status', state.status)
    params.set('media_type', state.mediaType)
    if (state.keyword) params.set('keyword', state.keyword)
    const data = await callApi(`${apiPrefix.value}/wall?${params.toString()}`)
    state.groups = data?.groups || []
    state.total_groups = Number(data?.total_groups || 0)
    state.total_records = Number(data?.total_records || 0)
    state.truncated = Boolean(data?.truncated)
    if (data?.config) Object.assign(state.config, data.config)
  } catch (err) {
    state.error = err?.message || String(err)
  } finally {
    state.loading = false
  }
}

function reload() {
  state.page = 1
  state.selected = []
  loadWall()
}

function goPage(page) {
  state.page = page
  state.selected = []
  loadWall()
}

function isSelected(key) {
  return state.selected.includes(key)
}

function toggleSelect(key) {
  const index = state.selected.indexOf(key)
  if (index >= 0) state.selected.splice(index, 1)
  else state.selected.push(key)
}

function selectCurrentPage() {
  if (allCurrentSelected.value) {
    state.selected = state.selected.filter((key) => !currentKeys.value.includes(key))
    return
  }
  currentKeys.value.forEach((key) => {
    if (!state.selected.includes(key)) state.selected.push(key)
  })
}

function openDetail(group) {
  state.detail = group
  state.seasonFilter = 'all'
  state.detailSelected = []
  state.detailDialog = true
}

function recordsOfGroups(keys) {
  const records = []
  const wanted = new Set(keys)
  state.groups.forEach((group) => {
    if (!wanted.has(group.key)) return
    ;(group.records || []).forEach((record) => records.push(record))
  })
  return records
}

function openDelete(ids, label, preset) {
  const wanted = new Set((ids || []).map(Number))
  const records = []
  state.groups.forEach((group) => {
    ;(group.records || []).forEach((record) => {
      if (wanted.has(Number(record.id))) records.push(record)
    })
  })
  if (state.detail) {
    ;(state.detail.records || []).forEach((record) => {
      if (wanted.has(Number(record.id)) && !records.some((item) => item.id === record.id)) {
        records.push(record)
      }
    })
  }
  if (!records.length) {
    notify('warning', '未找到对应的整理记录，请刷新后重试')
    return
  }
  state.confirmIds = [...wanted]
  state.confirmRecords = records
  state.confirmLabel = label
  state.flags = {
    record: preset?.record ?? state.config.default_delete_record,
    src: preset?.src ?? state.config.default_delete_src,
    dest: preset?.dest ?? state.config.default_delete_dest,
  }
  state.confirmText = ''
  state.confirmDialog = true
}

function openGroupDelete(label, preset) {
  if (!state.detail) return
  const ids = (state.detail.records || []).map((record) => record.id).filter(Boolean)
  openDelete(ids, label, preset)
}

function bulkDelete() {
  const records = recordsOfGroups(state.selected)
  if (!records.length) {
    notify('warning', '所选媒体没有可删除的记录')
    return
  }
  const ids = records.map((record) => record.id).filter(Boolean)
  openDelete(ids, `批量删除 ${state.selected.length} 部媒体`, {
    record: state.config.default_delete_record,
    src: state.config.default_delete_src,
    dest: state.config.default_delete_dest,
  })
}

function deleteSelectedInDetail() {
  if (!state.detailSelected.length) {
    notify('warning', '请先勾选要删除的记录或选择整季')
    return
  }
  const ids = [...state.detailSelected]
  openDelete(ids, `所选 ${ids.length} 条记录（按季/勾选）`, {
    record: state.config.default_delete_record,
    src: state.config.default_delete_src,
    dest: state.config.default_delete_dest,
  })
}

async function executeDelete() {
  if (needsConfirmText.value && state.confirmText.trim() !== '删除') {
    notify('warning', '请输入「删除」以确认文件删除')
    return
  }
  state.busy = true
  const maxBatch = Math.max(1, Number(state.config.max_batch || 20))
  const ids = [...state.confirmIds]
  let success = 0
  let failed = 0
  const failures = []
  try {
    for (let index = 0; index < ids.length; index += maxBatch) {
      const chunk = ids.slice(index, index + maxBatch)
      const result = await callApi(`${apiPrefix.value}/delete`, 'post', {
        ids: chunk,
        delete_record: Boolean(state.flags.record),
        delete_src: Boolean(state.flags.src),
        delete_dest: Boolean(state.flags.dest),
        confirm: '删除',
      })
      success += Number(result?.success_count || 0)
      failed += Number(result?.failed_count || 0)
      ;(result?.results || []).forEach((item) => {
        if (item && !item.ok && item.message) failures.push(`#${item.id} ${item.message}`)
      })
    }
    state.confirmDialog = false
    state.detailDialog = false
    state.selected = []
    if (failed) {
      notify('warning', `成功 ${success} 条，失败 ${failed} 条：${failures.slice(0, 3).join('；')}`)
    } else {
      notify('success', `已处理 ${success} 条记录`)
    }
    await loadWall()
  } catch (err) {
    notify('error', err?.message || String(err))
  } finally {
    state.busy = false
  }
}

onMounted(loadWall)
</script>

<style scoped>
.tw-page {
  padding: 12px;
}
.tw-panel {
  margin-bottom: 12px;
}
.tw-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.tw-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
}
.tw-search {
  min-width: 220px;
  flex: 1 1 240px;
}
.tw-filter {
  min-width: 120px;
  max-width: 180px;
}
.tw-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}
.tw-alert {
  margin-top: 12px;
}
.tw-grid {
  margin-top: 0;
}
.tw-cell {
  padding: 6px !important;
}
.tw-media-card {
  cursor: pointer;
  overflow: hidden;
}
.tw-poster-wrap {
  position: relative;
  width: 100%;
  aspect-ratio: 2 / 3;
  background: rgba(127, 127, 127, 0.12);
}
.tw-poster {
  width: 100%;
  height: 100%;
}
.tw-no-poster {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  text-align: center;
}
.tw-no-poster-title {
  font-size: 0.85rem;
  line-height: 1.2;
  word-break: break-all;
}
.tw-select-wrap {
  position: absolute;
  top: 4px;
  right: 4px;
  z-index: 3;
  background: transparent;
  border-radius: 4px;
}
/* 右上角勾选框：未选中为亮绿色描边空心框，选中为绿色实心 + 白色对勾 */
.tw-select-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  padding: 0;
  border: 2px solid #22c55e;
  border-radius: 5px;
  background: rgba(255, 255, 255, 0.95);
  color: #16a34a;
  cursor: pointer;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.35), 0 0 6px rgba(34, 197, 94, 0.7);
  transition: background 0.15s, border-color 0.15s;
}
.tw-select-box.is-selected {
  border-color: #16a34a;
  background: #22c55e;
  color: #ffffff;
}
.tw-record-select {
  width: 20px;
  height: 20px;
  flex: 0 0 auto;
}
.tw-season-ep {
  color: rgb(var(--v-theme-primary));
  font-weight: 600;
}
.tw-season-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  margin-bottom: 8px;
  border: 1px solid rgba(34, 197, 94, 0.45);
  border-radius: 6px;
  background: rgba(34, 197, 94, 0.06);
}
.tw-season-bar-label {
  font-size: 0.8rem;
  font-weight: 600;
  white-space: nowrap;
}
.tw-season-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.tw-season-tab {
  padding: 4px 10px;
  border: 1px solid rgba(127, 127, 127, 0.4);
  border-radius: 14px;
  background: transparent;
  color: inherit;
  font-size: 0.8rem;
  cursor: pointer;
  white-space: nowrap;
}
.tw-season-tab.active {
  border-color: #22c55e;
  background: rgba(34, 197, 94, 0.18);
  color: #16a34a;
  font-weight: 600;
}
.tw-season-tab-count {
  opacity: 0.75;
  font-size: 0.72rem;
}
.tw-season-selects {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px 10px;
  margin-left: auto;
}
.tw-season-select-item {
  display: flex;
  align-items: center;
  gap: 4px;
}
.tw-season-select {
  width: 18px;
  height: 18px;
}
.tw-detail-select-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px 10px;
  margin-bottom: 10px;
  border: 1px solid rgba(127, 127, 127, 0.3);
  border-radius: 6px;
}
.tw-selected-count {
  white-space: nowrap;
}
.tw-overlay {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 2;
  padding: 24px 8px 8px;
  color: #fff;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.82), rgba(0, 0, 0, 0));
}
.tw-title {
  font-size: 0.9rem;
  font-weight: 600;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.tw-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 2px;
  font-size: 0.72rem;
  opacity: 0.9;
}
.tw-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 6px;
}
.tw-loading,
.tw-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 240px;
  gap: 8px;
}
.tw-pager {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 12px;
}
.tw-detail-body {
  padding-top: 4px;
}
.tw-detail-head {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 12px;
}
.tw-detail-poster {
  flex: 0 0 auto;
  border-radius: 6px;
}
.tw-detail-info {
  flex: 1 1 auto;
}
.tw-detail-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
}
.tw-record {
  padding: 10px 12px;
  margin-bottom: 8px;
  border: 1px solid rgba(127, 127, 127, 0.3);
  border-radius: 6px;
}
.tw-record.is-checked {
  border-color: #22c55e;
  background: rgba(34, 197, 94, 0.07);
}
.tw-record-top {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.tw-path {
  font-size: 0.8rem;
  line-height: 1.5;
  word-break: break-all;
}
.tw-path-label {
  font-weight: 600;
}
.tw-confirm-title {
  color: rgb(var(--v-theme-error));
}
.tw-confirm-summary {
  margin: 8px 0 12px;
  font-weight: 600;
}
.tw-path-list {
  max-height: 180px;
  overflow-y: auto;
  padding: 8px 12px;
  margin-bottom: 12px;
  border: 1px solid rgba(127, 127, 127, 0.3);
  border-radius: 6px;
}
.tw-path-list-item {
  margin-bottom: 8px;
}
.tw-confirm-input {
  margin-top: 12px;
}
</style>
