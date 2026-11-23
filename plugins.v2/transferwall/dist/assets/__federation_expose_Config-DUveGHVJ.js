import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-pcqpp-6-.js';

const {createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,createElementVNode:_createElementVNode,openBlock:_openBlock,createElementBlock:_createElementBlock} = await importShared('vue');


const _hoisted_1 = { class: "tw-config" };

const {onMounted,reactive,ref} = await importShared('vue');



const _sfc_main = {
  __name: 'Config',
  props: {
  initialConfig: { type: Object, default: () => ({}) },
  api: { type: Object, default: () => ({}) },
},
  emits: ['save', 'close'],
  setup(__props, { emit: __emit }) {

const props = __props;
const emit = __emit;
const saving = ref(false);

const defaults = {
  enabled: false,
  nav_title: '整理海报墙',
  nav_icon: 'mdi-view-gallery',
  max_records: 1200,
  max_batch: 20,
  default_delete_record: true,
  default_delete_src: false,
  default_delete_dest: false,
};

const config = reactive({ ...defaults });

onMounted(() => {
  Object.keys(defaults).forEach((key) => {
    if (props.initialConfig && key in props.initialConfig) {
      config[key] = props.initialConfig[key];
    }
  });
});

function reset() {
  Object.keys(defaults).forEach((key) => {
    config[key] = defaults[key];
  });
}

async function save() {
  saving.value = true;
  try {
    emit('save', { ...config });
  } finally {
    saving.value = false;
  }
}

return (_ctx, _cache) => {
  const _component_v_card_title = _resolveComponent("v-card-title");
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_card_item = _resolveComponent("v-card-item");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_switch = _resolveComponent("v-switch");
  const _component_v_text_field = _resolveComponent("v-text-field");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_spacer = _resolveComponent("v-spacer");
  const _component_v_card_actions = _resolveComponent("v-card-actions");
  const _component_v_card = _resolveComponent("v-card");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createVNode(_component_v_card, { variant: "outlined" }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card_item, null, {
          append: _withCtx(() => [
            _createVNode(_component_v_btn, {
              icon: "mdi-close",
              size: "small",
              variant: "text",
              onClick: _cache[0] || (_cache[0] = $event => (emit('close')))
            })
          ]),
          default: _withCtx(() => [
            _createVNode(_component_v_card_title, null, {
              default: _withCtx(() => [...(_cache[9] || (_cache[9] = [
                _createTextVNode("整理海报墙设置", -1)
              ]))]),
              _: 1
            })
          ]),
          _: 1
        }),
        _createVNode(_component_v_card_text, null, {
          default: _withCtx(() => [
            _createVNode(_component_v_alert, {
              type: "info",
              variant: "tonal",
              class: "tw-config-alert"
            }, {
              default: _withCtx(() => [...(_cache[10] || (_cache[10] = [
                _createTextVNode(" 启用后会在主界面「整理」分组显示海报墙。文件删除不可恢复，请谨慎设置默认项。 ", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_v_switch, {
              modelValue: config.enabled,
              "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((config.enabled) = $event)),
              label: "启用插件并显示侧栏入口",
              color: "primary",
              inset: "",
              density: "compact",
              "hide-details": ""
            }, null, 8, ["modelValue"]),
            _cache[11] || (_cache[11] = _createElementVNode("div", { class: "tw-config-section" }, "侧栏入口", -1)),
            _createVNode(_component_v_text_field, {
              modelValue: config.nav_title,
              "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.nav_title) = $event)),
              density: "compact",
              variant: "outlined",
              label: "菜单标题",
              "hide-details": ""
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_text_field, {
              modelValue: config.nav_icon,
              "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.nav_icon) = $event)),
              density: "compact",
              variant: "outlined",
              label: "MDI 图标",
              hint: "例如 mdi-view-gallery",
              "persistent-hint": "",
              class: "tw-config-field"
            }, null, 8, ["modelValue"]),
            _cache[12] || (_cache[12] = _createElementVNode("div", { class: "tw-config-section" }, "数据范围", -1)),
            _createVNode(_component_v_text_field, {
              modelValue: config.max_records,
              "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.max_records) = $event)),
              modelModifiers: { number: true },
              density: "compact",
              variant: "outlined",
              label: "最多读取记录数",
              type: "number",
              min: "100",
              max: "10000",
              hint: "海报墙按媒体聚合，记录越多加载越慢",
              "persistent-hint": ""
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_text_field, {
              modelValue: config.max_batch,
              "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.max_batch) = $event)),
              modelModifiers: { number: true },
              density: "compact",
              variant: "outlined",
              label: "单次批量删除上限",
              type: "number",
              min: "1",
              max: "100",
              class: "tw-config-field"
            }, null, 8, ["modelValue"]),
            _cache[13] || (_cache[13] = _createElementVNode("div", { class: "tw-config-section" }, "删除默认选项", -1)),
            _createVNode(_component_v_switch, {
              modelValue: config.default_delete_record,
              "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.default_delete_record) = $event)),
              label: "默认勾选：删除整理记录",
              density: "compact",
              "hide-details": ""
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_switch, {
              modelValue: config.default_delete_src,
              "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.default_delete_src) = $event)),
              label: "默认勾选：删除源文件（下载目录）",
              color: "warning",
              density: "compact",
              "hide-details": ""
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_switch, {
              modelValue: config.default_delete_dest,
              "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((config.default_delete_dest) = $event)),
              label: "默认勾选：删除媒体库文件",
              color: "error",
              density: "compact",
              "hide-details": ""
            }, null, 8, ["modelValue"])
          ]),
          _: 1
        }),
        _createVNode(_component_v_card_actions, null, {
          default: _withCtx(() => [
            _createVNode(_component_v_btn, {
              variant: "text",
              onClick: reset
            }, {
              default: _withCtx(() => [...(_cache[14] || (_cache[14] = [
                _createTextVNode("恢复默认", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_v_spacer),
            _createVNode(_component_v_btn, {
              color: "primary",
              variant: "flat",
              loading: saving.value,
              onClick: save
            }, {
              default: _withCtx(() => [...(_cache[15] || (_cache[15] = [
                _createTextVNode("保存配置", -1)
              ]))]),
              _: 1
            }, 8, ["loading"])
          ]),
          _: 1
        })
      ]),
      _: 1
    })
  ]))
}
}

};
const Config = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-eab6c8f6"]]);

export { Config as default };
