<template>
  <div class="tw-config">
    <v-card variant="outlined">
      <v-card-item>
        <v-card-title>整理海报墙设置</v-card-title>
        <template #append>
          <v-btn icon="mdi-close" size="small" variant="text" @click="emit('close')" />
        </template>
      </v-card-item>
      <v-card-text>
        <v-alert type="info" variant="tonal" class="tw-config-alert">
          启用后会在主界面「整理」分组显示海报墙。文件删除不可恢复，请谨慎设置默认项。
        </v-alert>

        <v-switch
          v-model="config.enabled"
          label="启用插件并显示侧栏入口"
          color="primary"
          inset
          density="compact"
          hide-details
        />

        <div class="tw-config-section">侧栏入口</div>
        <v-text-field
          v-model="config.nav_title"
          density="compact"
          variant="outlined"
          label="菜单标题"
          hide-details
        />
        <v-text-field
          v-model="config.nav_icon"
          density="compact"
          variant="outlined"
          label="MDI 图标"
          hint="例如 mdi-view-gallery"
          persistent-hint
          class="tw-config-field"
        />

        <div class="tw-config-section">数据范围</div>
        <v-text-field
          v-model.number="config.max_records"
          density="compact"
          variant="outlined"
          label="最多读取记录数"
          type="number"
          min="100"
          max="10000"
          hint="海报墙按媒体聚合，记录越多加载越慢"
          persistent-hint
        />
        <v-text-field
          v-model.number="config.max_batch"
          density="compact"
          variant="outlined"
          label="单次批量删除上限"
          type="number"
          min="1"
          max="100"
          class="tw-config-field"
        />

        <div class="tw-config-section">删除默认选项</div>
        <v-switch
          v-model="config.default_delete_record"
          label="默认勾选：删除整理记录"
          density="compact"
          hide-details
        />
        <v-switch
          v-model="config.default_delete_src"
          label="默认勾选：删除源文件（下载目录）"
          color="warning"
          density="compact"
          hide-details
        />
        <v-switch
          v-model="config.default_delete_dest"
          label="默认勾选：删除媒体库文件"
          color="error"
          density="compact"
          hide-details
        />
      </v-card-text>
      <v-card-actions>
        <v-btn variant="text" @click="reset">恢复默认</v-btn>
        <v-spacer />
        <v-btn color="primary" variant="flat" :loading="saving" @click="save">保存配置</v-btn>
      </v-card-actions>
    </v-card>
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

const defaults = {
  enabled: false,
  nav_title: '整理海报墙',
  nav_icon: 'mdi-view-gallery',
  max_records: 1200,
  max_batch: 20,
  default_delete_record: true,
  default_delete_src: false,
  default_delete_dest: false,
}

const config = reactive({ ...defaults })

onMounted(() => {
  Object.keys(defaults).forEach((key) => {
    if (props.initialConfig && key in props.initialConfig) {
      config[key] = props.initialConfig[key]
    }
  })
})

function reset() {
  Object.keys(defaults).forEach((key) => {
    config[key] = defaults[key]
  })
}

async function save() {
  saving.value = true
  try {
    emit('save', { ...config })
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.tw-config-alert {
  margin-bottom: 12px;
}
.tw-config-section {
  margin-top: 16px;
  margin-bottom: 8px;
  font-weight: 600;
}
.tw-config-field {
  margin-top: 12px;
}
</style>
