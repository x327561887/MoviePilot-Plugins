import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-pcqpp-6-.js';

const {toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,createElementVNode:_createElementVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,createElementBlock:_createElementBlock} = await importShared('vue');


const _hoisted_1 = { class: "tw-plugin-page" };
const _hoisted_2 = { class: "text-h4" };
const _hoisted_3 = { class: "text-h4" };

const {computed,onMounted,reactive,ref} = await importShared('vue');



const _sfc_main = {
  __name: 'Page',
  props: {
  model: { type: Object, default: () => ({}) },
  api: { type: Object, default: () => ({}) },
  pluginId: { type: String, default: '' },
},
  setup(__props) {

const props = __props;

const title = computed(() => props.model?.nav_title || '整理海报墙');
const loading = ref(false);
const error = ref('');
const stats = reactive({ total_groups: 0, total_records: 0 });

async function load() {
  loading.value = true;
  error.value = '';
  try {
    const api = props.api || {};
    if (typeof api.get !== 'function') throw new Error('主应用未注入 API 客户端')
    let response = await api.get(`plugin/${props.pluginId || 'TransferWall'}/wall?page=1&page_size=1`);
    if (response && response.success === false) throw new Error(response.message || '请求失败')
    const data = response && 'data' in response ? response.data : response;
    stats.total_groups = Number(data?.total_groups || 0);
    stats.total_records = Number(data?.total_records || 0);
  } catch (err) {
    error.value = err?.message || String(err);
  } finally {
    loading.value = false;
  }
}

onMounted(load);

return (_ctx, _cache) => {
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_card = _resolveComponent("v-card");
  const _component_v_col = _resolveComponent("v-col");
  const _component_v_row = _resolveComponent("v-row");
  const _component_v_btn = _resolveComponent("v-btn");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createVNode(_component_v_alert, {
      type: "info",
      variant: "tonal",
      class: "tw-page-alert"
    }, {
      default: _withCtx(() => [
        _createTextVNode(" 完整海报墙已添加到主界面左侧「整理」分组。请从侧栏「" + _toDisplayString(title.value) + "」进入；此页仅显示概览。 ", 1)
      ]),
      _: 1
    }),
    _createVNode(_component_v_row, null, {
      default: _withCtx(() => [
        _createVNode(_component_v_col, {
          cols: "12",
          sm: "6"
        }, {
          default: _withCtx(() => [
            _createVNode(_component_v_card, { variant: "outlined" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_card_text, null, {
                  default: _withCtx(() => [
                    _createElementVNode("div", _hoisted_2, _toDisplayString(stats.total_groups), 1),
                    _cache[0] || (_cache[0] = _createElementVNode("div", { class: "text-caption" }, "媒体数量", -1))
                  ]),
                  _: 1
                })
              ]),
              _: 1
            })
          ]),
          _: 1
        }),
        _createVNode(_component_v_col, {
          cols: "12",
          sm: "6"
        }, {
          default: _withCtx(() => [
            _createVNode(_component_v_card, { variant: "outlined" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_card_text, null, {
                  default: _withCtx(() => [
                    _createElementVNode("div", _hoisted_3, _toDisplayString(stats.total_records), 1),
                    _cache[1] || (_cache[1] = _createElementVNode("div", { class: "text-caption" }, "整理记录", -1))
                  ]),
                  _: 1
                })
              ]),
              _: 1
            })
          ]),
          _: 1
        })
      ]),
      _: 1
    }),
    _createVNode(_component_v_btn, {
      class: "tw-refresh",
      variant: "tonal",
      loading: loading.value,
      "prepend-icon": "mdi-refresh",
      onClick: load
    }, {
      default: _withCtx(() => [...(_cache[2] || (_cache[2] = [
        _createTextVNode(" 刷新概览 ", -1)
      ]))]),
      _: 1
    }, 8, ["loading"]),
    (error.value)
      ? (_openBlock(), _createBlock(_component_v_alert, {
          key: 0,
          type: "error",
          variant: "tonal",
          class: "tw-page-alert"
        }, {
          default: _withCtx(() => [
            _createTextVNode(_toDisplayString(error.value), 1)
          ]),
          _: 1
        }))
      : _createCommentVNode("", true)
  ]))
}
}

};
const Page = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-1e8b42cc"]]);

export { Page as default };
