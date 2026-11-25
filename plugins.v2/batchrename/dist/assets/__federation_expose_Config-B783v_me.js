import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-pcqpp-6-.js';

const {createElementVNode:_createElementVNode,createTextVNode:_createTextVNode,vModelText:_vModelText,withDirectives:_withDirectives,toDisplayString:_toDisplayString,normalizeClass:_normalizeClass,openBlock:_openBlock,createElementBlock:_createElementBlock} = await importShared('vue');


const _hoisted_1 = { class: "br-config" };
const _hoisted_2 = { class: "br-card" };
const _hoisted_3 = { class: "br-head" };
const _hoisted_4 = { class: "br-body" };
const _hoisted_5 = { class: "br-field" };
const _hoisted_6 = { class: "br-field" };
const _hoisted_7 = { class: "br-row-actions" };
const _hoisted_8 = ["disabled"];

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
const toastText = ref('');

const config = reactive({
  source_dir: '',
  extensions: 'mp4, mkv, srt, ass',
});

onMounted(() => {
  const initial = props.initialConfig || {};
  if ('source_dir' in initial) config.source_dir = initial.source_dir || '';
  if ('extensions' in initial) config.extensions = initial.extensions || 'mp4, mkv, srt, ass';
});

function save() {
  saving.value = true;
  try {
    emit('save', {
      enabled: true,
      source_dir: String(config.source_dir || '').trim(),
      extensions: String(config.extensions || '').trim(),
      season: Number((props.initialConfig || {}).season || 1),
      start_episode: Number((props.initialConfig || {}).start_episode || 72),
    });
    toast('配置已保存');
  } finally {
    saving.value = false;
  }
}

let toastTimer;
function toast(message) {
  toastText.value = message;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toastText.value = ''; }, 2400);
}

return (_ctx, _cache) => {
  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createElementVNode("div", _hoisted_2, [
      _createElementVNode("div", _hoisted_3, [
        _cache[4] || (_cache[4] = _createElementVNode("h1", null, "批量改名（顺序重编号） - 插件配置", -1)),
        _createElementVNode("span", {
          class: "br-close",
          onClick: _cache[0] || (_cache[0] = $event => (emit('close')))
        }, "✕")
      ]),
      _createElementVNode("div", _hoisted_4, [
        _cache[9] || (_cache[9] = _createElementVNode("div", { class: "br-info" }, [
          _createElementVNode("span", { class: "br-i" }, "i"),
          _createElementVNode("div", null, [
            _createTextVNode("只需填写剧集目录，扩展名默认 "),
            _createElementVNode("b", null, "mp4, mkv, srt, ass"),
            _createTextVNode("。保存后到插件详情页点「预览改名」，勾选要处理的文件再批量修改。改名规则：保留原标题，季号统一替换，集号按你填的起始集连续递增，「第 XX 集」自动跟随新集号。")
          ])
        ], -1)),
        _createElementVNode("div", _hoisted_5, [
          _cache[5] || (_cache[5] = _createElementVNode("label", null, "剧集目录（MoviePilot 容器内的绝对路径）", -1)),
          _withDirectives(_createElementVNode("input", {
            type: "text",
            "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((config.source_dir) = $event)),
            placeholder: "例如 /media/动画/Re：从零开始的异世界生活"
          }, null, 512), [
            [_vModelText, config.source_dir]
          ]),
          _cache[6] || (_cache[6] = _createElementVNode("div", { class: "br-hint" }, "填写容器内部路径，不是宿主机路径", -1))
        ]),
        _createElementVNode("div", _hoisted_6, [
          _cache[7] || (_cache[7] = _createElementVNode("label", null, "处理扩展名（逗号分隔）", -1)),
          _withDirectives(_createElementVNode("input", {
            type: "text",
            "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.extensions) = $event))
          }, null, 512), [
            [_vModelText, config.extensions]
          ]),
          _cache[8] || (_cache[8] = _createElementVNode("div", { class: "br-hint" }, "只有这些类型的文件会显示在预览列表中", -1))
        ]),
        _createElementVNode("div", _hoisted_7, [
          _createElementVNode("button", {
            class: "br-link-btn",
            onClick: _cache[3] || (_cache[3] = $event => (toast('配置数据由 MoviePilot 统一管理')))
          }, "▤ 查看数据"),
          _createElementVNode("button", {
            class: "br-save-btn",
            disabled: saving.value,
            onClick: save
          }, "▣ 保存", 8, _hoisted_8)
        ])
      ])
    ]),
    _createElementVNode("div", {
      class: _normalizeClass(["br-toast", { show: toastText.value }])
    }, _toDisplayString(toastText.value), 3)
  ]))
}
}

};
const Config = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-93127995"]]);

export { Config as default };
