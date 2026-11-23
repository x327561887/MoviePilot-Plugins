<template>
  <div class="tw-plugin-page">
    <v-alert type="info" variant="tonal" class="tw-page-alert">
      完整海报墙已添加到主界面左侧「整理」分组。请从侧栏「{{ title }}」进入；此页仅显示概览。
    </v-alert>

    <v-row>
      <v-col cols="12" sm="6">
        <v-card variant="outlined">
          <v-card-text>
            <div class="text-h4">{{ stats.total_groups }}</div>
            <div class="text-caption">媒体数量</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6">
        <v-card variant="outlined">
          <v-card-text>
            <div class="text-h4">{{ stats.total_records }}</div>
            <div class="text-caption">整理记录</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-btn class="tw-refresh" variant="tonal" :loading="loading" prepend-icon="mdi-refresh" @click="load">
      刷新概览
    </v-btn>
    <v-alert v-if="error" type="error" variant="tonal" class="tw-page-alert">{{ error }}</v-alert>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

const props = defineProps({
  model: { type: Object, default: () => ({}) },
  api: { type: Object, default: () => ({}) },
  pluginId: { type: String, default: '' },
})

const title = computed(() => props.model?.nav_title || '整理海报墙')
const loading = ref(false)
const error = ref('')
const stats = reactive({ total_groups: 0, total_records: 0 })

async function load() {
  loading.value = true
  error.value = ''
  try {
    const api = props.api || {}
    if (typeof api.get !== 'function') throw new Error('主应用未注入 API 客户端')
    let response = await api.get(`plugin/${props.pluginId || 'TransferWall'}/wall?page=1&page_size=1`)
    if (response && response.success === false) throw new Error(response.message || '请求失败')
    const data = response && 'data' in response ? response.data : response
    stats.total_groups = Number(data?.total_groups || 0)
    stats.total_records = Number(data?.total_records || 0)
  } catch (err) {
    error.value = err?.message || String(err)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.tw-page-alert {
  margin-bottom: 12px;
}
.tw-refresh {
  margin-top: 12px;
}
</style>
