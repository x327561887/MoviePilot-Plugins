import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-pcqpp-6-.js';

const {createElementVNode:_createElementVNode,vModelText:_vModelText,withDirectives:_withDirectives,toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,openBlock:_openBlock,createElementBlock:_createElementBlock,createCommentVNode:_createCommentVNode,renderList:_renderList,Fragment:_Fragment,normalizeClass:_normalizeClass} = await importShared('vue');


const _hoisted_1 = { class: "br-page" };
const _hoisted_2 = { class: "br-card" };
const _hoisted_3 = { class: "br-head" };
const _hoisted_4 = { class: "br-body" };
const _hoisted_5 = { class: "br-toolbar" };
const _hoisted_6 = { class: "br-param" };
const _hoisted_7 = { class: "br-param" };
const _hoisted_8 = ["disabled"];
const _hoisted_9 = { class: "br-rule" };
const _hoisted_10 = {
  key: 0,
  class: "br-alert error"
};
const _hoisted_11 = { key: 1 };
const _hoisted_12 = { class: "br-summary" };
const _hoisted_13 = { class: "br-pill" };
const _hoisted_14 = { class: "br-pill" };
const _hoisted_15 = { class: "br-pill" };
const _hoisted_16 = { class: "br-pill" };
const _hoisted_17 = { class: "br-table-wrap" };
const _hoisted_18 = { style: {"width":"46px"} };
const _hoisted_19 = ["checked", "disabled"];
const _hoisted_20 = ["checked", "disabled", "onChange"];
const _hoisted_21 = {
  key: 0,
  class: "br-fname new"
};
const _hoisted_22 = {
  key: 1,
  class: "br-fname dim"
};
const _hoisted_23 = { key: 0 };
const _hoisted_24 = { class: "br-bottom-bar" };
const _hoisted_25 = { class: "br-selected-count" };
const _hoisted_26 = { class: "br-btn-group" };
const _hoisted_27 = ["disabled"];
const _hoisted_28 = ["disabled"];

const {computed,onMounted,reactive,ref} = await importShared('vue');



const _sfc_main = {
  __name: 'Page',
  props: {
  model: { type: Object, default: () => ({}) },
  api: { type: Object, default: () => ({}) },
  pluginId: { type: String, default: 'BatchRename' },
},
  emits: ['close', 'openConfig'],
  setup(__props, { emit: __emit }) {

const props = __props;
const emit = __emit;

const season = ref(Number((props.model || {}).season || 1));
const start = ref(Number((props.model || {}).start_episode || 1));
const sourceLabel = computed(() => (props.model || {}).source_dir || '未设置目录');

const loading = ref(false);
const applying = ref(false);
const error = ref('');
const hasPreview = ref(false);
const items = ref([]);
const summary = reactive({ generated_at: '', total: 0, ready: 0, exist: 0 });
const selected = ref(new Set());
const canUndo = ref(false);
const toastText = ref('');

const readyIndexes = computed(() => items.value.filter(i => i.status === 'ready').map(i => i.old_name));
const allChecked = computed(() => readyIndexes.value.length > 0 && readyIndexes.value.every(n => selected.value.has(n)));
const selectedReadyCount = computed(() => readyIndexes.value.filter(n => selected.value.has(n)).length);

function pad(value) { return String(value || 0).padStart(2, '0') }
function statusText(status) {
  return { ready: '待修改', exist: '已存在', conflict: '跳过', done: '已改名' }[status] || status
}
function statusClass(status) {
  return { ready: 'wait', exist: 'exist', conflict: 'conflict', done: 'done' }[status] || 'wait'
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
  const api = props.api || {};
  if (method === 'get') {
    if (typeof api.get === 'function') return unwrap(await api.get(path, payload))
    if (typeof api.request === 'function') return unwrap(await api.request({ url: path, method: 'get', params: payload }))
  } else {
    if (typeof api.post === 'function') return unwrap(await api.post(path, payload))
    if (typeof api.request === 'function') return unwrap(await api.request({ url: path, method: 'post', data: payload }))
  }
  throw new Error('主应用未注入 API 客户端，请确认插件已启用')
}

const apiPrefix = computed(() => `plugin/${props.pluginId || 'BatchRename'}`);

async function preview() {
  loading.value = true;
  error.value = '';
  try {
    const data = await callApi(`${apiPrefix.value}/preview`, 'post', {
      season: Number(season.value) || 0,
      start: Number(start.value) || 1,
    });
    items.value = data.items || [];
    summary.generated_at = data.generated_at || '';
    summary.total = Number(data.total_count || 0);
    summary.ready = Number(data.ready_count || 0);
    summary.exist = Number(data.exist_count || 0);
    selected.value = new Set(items.value.filter(i => i.status === 'ready').map(i => i.old_name));
    hasPreview.value = true;
    toast(`已扫描到 ${summary.total} 个媒体文件，其中 ${summary.ready} 个待改名`);
  } catch (err) {
    error.value = err?.message || String(err);
    toast(error.value);
  } finally {
    loading.value = false;
  }
}

let previewTimer;
function refreshPreview() {
  clearTimeout(previewTimer);
  previewTimer = setTimeout(() => { if (hasPreview.value) preview(); }, 350);
}

function toggleAll(on) {
  const next = new Set(selected.value);
  readyIndexes.value.forEach(name => { if (on) next.add(name); else next.delete(name); });
  selected.value = next;
}
function toggleOne(name, on) {
  const next = new Set(selected.value);
  if (on) next.add(name); else next.delete(name);
  selected.value = next;
}

async function apply() {
  const names = readyIndexes.value.filter(n => selected.value.has(n));
  if (!names.length) return
  applying.value = true;
  error.value = '';
  try {
    const data = await callApi(`${apiPrefix.value}/apply`, 'post', {
      season: Number(season.value) || 0,
      start: Number(start.value) || 1,
      names,
    });
    toast(data?.message || `已完成批量改名，共处理 ${names.length} 个文件`);
    canUndo.value = true;
    await preview();
  } catch (err) {
    error.value = err?.message || String(err);
    toast(error.value);
  } finally {
    applying.value = false;
  }
}

async function undo() {
  applying.value = true;
  error.value = '';
  try {
    const data = await callApi(`${apiPrefix.value}/undo`, 'post', {});
    toast(data?.message || '已恢复上次改名');
    canUndo.value = false;
    await preview();
  } catch (err) {
    error.value = err?.message || String(err);
    toast(error.value);
  } finally {
    applying.value = false;
  }
}

onMounted(() => {
  // 详情页不自动扫描：用户点「预览改名」后再列出文件，与原原型一致
});

let toastTimer;
function toast(message) {
  toastText.value = message;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toastText.value = ''; }, 2800);
}

return (_ctx, _cache) => {
  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createElementVNode("div", _hoisted_2, [
      _createElementVNode("div", _hoisted_3, [
        _cache[5] || (_cache[5] = _createElementVNode("h1", null, "批量改名 - 插件详情", -1)),
        _createElementVNode("span", {
          class: "br-close",
          onClick: _cache[0] || (_cache[0] = $event => (emit('close')))
        }, "✕")
      ]),
      _createElementVNode("div", _hoisted_4, [
        _createElementVNode("div", _hoisted_5, [
          _createElementVNode("div", _hoisted_6, [
            _cache[6] || (_cache[6] = _createElementVNode("label", null, "目标季号 SXX", -1)),
            _withDirectives(_createElementVNode("input", {
              type: "number",
              "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((season).value = $event)),
              min: "0",
              max: "99",
              onInput: refreshPreview
            }, null, 544), [
              [
                _vModelText,
                season.value,
                void 0,
                { number: true }
              ]
            ])
          ]),
          _createElementVNode("div", _hoisted_7, [
            _cache[7] || (_cache[7] = _createElementVNode("label", null, "起始集号", -1)),
            _withDirectives(_createElementVNode("input", {
              type: "number",
              "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((start).value = $event)),
              min: "1",
              max: "9999",
              onInput: refreshPreview
            }, null, 544), [
              [
                _vModelText,
                start.value,
                void 0,
                { number: true }
              ]
            ])
          ]),
          _createElementVNode("button", {
            class: "br-btn primary",
            disabled: loading.value,
            onClick: preview
          }, " 🔍 " + _toDisplayString(loading.value ? '扫描中…' : '预览改名'), 9, _hoisted_8),
          _createElementVNode("button", {
            class: "br-btn ghost",
            onClick: _cache[3] || (_cache[3] = $event => (emit('openConfig')))
          }, "⚙ 修改目录设置")
        ]),
        _createElementVNode("div", _hoisted_9, [
          _cache[8] || (_cache[8] = _createTextVNode(" 当前目录：", -1)),
          _createElementVNode("b", null, _toDisplayString(sourceLabel.value), 1),
          _cache[9] || (_cache[9] = _createElementVNode("br", null, null, -1)),
          _cache[10] || (_cache[10] = _createTextVNode(" 改名规则：", -1)),
          _createElementVNode("b", null, "S" + _toDisplayString(pad(season.value)), 1),
          _cache[11] || (_cache[11] = _createTextVNode("（所有季号统一替换）； 所有文件 ", -1)),
          _cache[12] || (_cache[12] = _createElementVNode("b", null, "按原集数从小到大", -1)),
          _cache[13] || (_cache[13] = _createTextVNode("，依次改为 ", -1)),
          _createElementVNode("b", null, "E" + _toDisplayString(start.value) + " 起连续递增", 1),
          _cache[14] || (_cache[14] = _createTextVNode("； ", -1)),
          _cache[15] || (_cache[15] = _createElementVNode("b", null, "「第 XX 集」按新集号自动改写", -1)),
          _cache[16] || (_cache[16] = _createTextVNode("。所有文件均可勾选修改（含已是目标季号的）。 ", -1))
        ]),
        (error.value)
          ? (_openBlock(), _createElementBlock("div", _hoisted_10, _toDisplayString(error.value), 1))
          : _createCommentVNode("", true),
        (hasPreview.value)
          ? (_openBlock(), _createElementBlock("div", _hoisted_11, [
              _createElementVNode("div", _hoisted_12, [
                _createElementVNode("span", _hoisted_13, _toDisplayString(summary.generated_at), 1),
                _createElementVNode("span", _hoisted_14, "共 " + _toDisplayString(summary.total) + " 个媒体文件", 1),
                _createElementVNode("span", _hoisted_15, "待改名 " + _toDisplayString(summary.ready), 1),
                _createElementVNode("span", _hoisted_16, "已存在 " + _toDisplayString(summary.exist), 1)
              ]),
              _createElementVNode("div", _hoisted_17, [
                _createElementVNode("table", null, [
                  _createElementVNode("thead", null, [
                    _createElementVNode("tr", null, [
                      _createElementVNode("th", _hoisted_18, [
                        _createElementVNode("input", {
                          type: "checkbox",
                          class: "br-chk",
                          checked: allChecked.value,
                          disabled: readyIndexes.value.length===0,
                          onChange: _cache[4] || (_cache[4] = $event => (toggleAll($event.target.checked)))
                        }, null, 40, _hoisted_19)
                      ]),
                      _cache[17] || (_cache[17] = _createElementVNode("th", { style: {"width":"96px"} }, "状态", -1)),
                      _cache[18] || (_cache[18] = _createElementVNode("th", null, "原文件名", -1)),
                      _cache[19] || (_cache[19] = _createElementVNode("th", { style: {"width":"30px"} }, null, -1)),
                      _cache[20] || (_cache[20] = _createElementVNode("th", null, "修改后文件名", -1))
                    ])
                  ]),
                  _createElementVNode("tbody", null, [
                    (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(items.value, (item, i) => {
                      return (_openBlock(), _createElementBlock("tr", {
                        key: item.old_name
                      }, [
                        _createElementVNode("td", null, [
                          _createElementVNode("input", {
                            type: "checkbox",
                            class: "br-chk",
                            checked: selected.value.has(item.old_name),
                            disabled: item.status!=='ready',
                            onChange: $event => (toggleOne(item.old_name, $event.target.checked))
                          }, null, 40, _hoisted_20)
                        ]),
                        _createElementVNode("td", null, [
                          _createElementVNode("span", {
                            class: _normalizeClass(["br-tag", statusClass(item.status)])
                          }, _toDisplayString(statusText(item.status)), 3)
                        ]),
                        _createElementVNode("td", null, [
                          _createElementVNode("span", {
                            class: _normalizeClass(["br-fname", { dim: item.status==='exist' }])
                          }, _toDisplayString(item.old_name), 3)
                        ]),
                        _cache[21] || (_cache[21] = _createElementVNode("td", null, [
                          _createElementVNode("span", { class: "br-arrow" }, "→")
                        ], -1)),
                        _createElementVNode("td", null, [
                          (item.status==='ready')
                            ? (_openBlock(), _createElementBlock("span", _hoisted_21, _toDisplayString(item.new_name), 1))
                            : (_openBlock(), _createElementBlock("span", _hoisted_22, "已是目标名"))
                        ])
                      ]))
                    }), 128)),
                    (items.value.length===0)
                      ? (_openBlock(), _createElementBlock("tr", _hoisted_23, [...(_cache[22] || (_cache[22] = [
                          _createElementVNode("td", {
                            colspan: "5",
                            style: {"text-align":"center","color":"#9aa1ad","padding":"24px"}
                          }, "没有可显示的文件", -1)
                        ]))]))
                      : _createCommentVNode("", true)
                  ])
                ])
              ]),
              _createElementVNode("div", _hoisted_24, [
                _createElementVNode("div", _hoisted_25, [
                  _cache[23] || (_cache[23] = _createTextVNode("已选择 ", -1)),
                  _createElementVNode("b", null, _toDisplayString(selectedReadyCount.value), 1),
                  _cache[24] || (_cache[24] = _createTextVNode(" 个文件", -1))
                ]),
                _createElementVNode("div", _hoisted_26, [
                  _createElementVNode("button", {
                    class: "br-btn ghost",
                    disabled: !canUndo.value,
                    onClick: undo
                  }, "↩ 恢复上次改名", 8, _hoisted_27),
                  _createElementVNode("button", {
                    class: "br-btn go",
                    disabled: selectedReadyCount.value===0 || applying.value,
                    onClick: apply
                  }, " ✓ " + _toDisplayString(applying.value ? '执行中…' : '执行批量改名'), 9, _hoisted_28)
                ])
              ])
            ]))
          : _createCommentVNode("", true)
      ])
    ]),
    _createElementVNode("div", {
      class: _normalizeClass(["br-toast", { show: toastText.value }])
    }, _toDisplayString(toastText.value), 3)
  ]))
}
}

};
const Page = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-df16e81b"]]);

export { Page as default };
