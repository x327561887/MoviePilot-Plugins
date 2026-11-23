import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-pcqpp-6-.js';

const {createElementVNode:_createElementVNode,resolveComponent:_resolveComponent,createVNode:_createVNode,withKeys:_withKeys,toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,withCtx:_withCtx,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,createElementBlock:_createElementBlock,renderList:_renderList,Fragment:_Fragment,withModifiers:_withModifiers} = await importShared('vue');


const _hoisted_1 = { class: "tw-page" };
const _hoisted_2 = { class: "tw-heading" };
const _hoisted_3 = { class: "tw-toolbar" };
const _hoisted_4 = { class: "tw-stats" };
const _hoisted_5 = {
  key: 0,
  class: "tw-loading"
};
const _hoisted_6 = {
  key: 1,
  class: "tw-empty"
};
const _hoisted_7 = { class: "tw-poster-wrap" };
const _hoisted_8 = {
  key: 1,
  class: "tw-poster tw-no-poster"
};
const _hoisted_9 = { class: "tw-no-poster-title" };
const _hoisted_10 = { class: "tw-overlay" };
const _hoisted_11 = ["title"];
const _hoisted_12 = { class: "tw-meta" };
const _hoisted_13 = { key: 0 };
const _hoisted_14 = { key: 1 };
const _hoisted_15 = { class: "tw-badges" };
const _hoisted_16 = {
  key: 3,
  class: "tw-pager"
};
const _hoisted_17 = { class: "text-caption" };
const _hoisted_18 = { class: "tw-detail-head" };
const _hoisted_19 = { class: "tw-detail-info" };
const _hoisted_20 = { class: "text-subtitle-1" };
const _hoisted_21 = { class: "text-caption text-medium-emphasis" };
const _hoisted_22 = { key: 0 };
const _hoisted_23 = { key: 1 };
const _hoisted_24 = { class: "tw-detail-actions" };
const _hoisted_25 = { class: "tw-record-top" };
const _hoisted_26 = { class: "text-caption" };
const _hoisted_27 = {
  key: 0,
  class: "text-caption"
};
const _hoisted_28 = {
  key: 1,
  class: "text-caption"
};
const _hoisted_29 = { class: "tw-path" };
const _hoisted_30 = { class: "tw-path" };
const _hoisted_31 = {
  key: 0,
  class: "text-caption text-error"
};
const _hoisted_32 = { class: "tw-confirm-summary" };
const _hoisted_33 = { key: 0 };
const _hoisted_34 = { class: "tw-path-list" };
const _hoisted_35 = { class: "text-caption font-weight-medium" };
const _hoisted_36 = { class: "tw-path" };
const _hoisted_37 = { class: "tw-path" };
const _hoisted_38 = {
  key: 0,
  class: "text-caption text-medium-emphasis"
};

const {computed,inject,onMounted,reactive} = await importShared('vue');



const _sfc_main = {
  __name: 'AppPage',
  props: {
  api: { type: Object, default: () => ({}) },
  navKey: { type: String, default: 'main' },
  pluginId: { type: String, default: '' },
},
  setup(__props) {

const props = __props;

const toast = inject('moviepilot:toast', null);

const statusOptions = [
  { title: '全部', value: 'all' },
  { title: '成功', value: 'success' },
  { title: '失败', value: 'fail' },
];
const typeOptions = [
  { title: '全部类型', value: 'all' },
  { title: '电影', value: 'movie' },
  { title: '电视剧', value: 'tv' },
];

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
  confirmDialog: false,
  confirmLabel: '',
  confirmIds: [],
  confirmRecords: [],
  flags: { record: true, src: false, dest: false },
  confirmText: '',
  busy: false,
  config: {
    max_batch: 20,
    default_delete_record: true,
    default_delete_src: false,
    default_delete_dest: false,
  },
});

const apiPrefix = computed(() => `plugin/${props.pluginId || 'TransferWall'}`);
const needsConfirmText = computed(() => Boolean(state.flags.src || state.flags.dest));
const currentKeys = computed(() => state.groups.map((group) => group.key));
const allCurrentSelected = computed(
  () => currentKeys.value.length > 0 && currentKeys.value.every((key) => state.selected.includes(key))
);

function notify(type, message) {
  const fn = toast && typeof toast[type] === 'function' ? toast[type] : null;
  if (fn) {
    fn(message);
    return
  }
  state.localMessage = message;
  window.setTimeout(() => {
    if (state.localMessage === message) state.localMessage = '';
  }, 6000);
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
  state.loading = true;
  state.error = '';
  try {
    const params = new URLSearchParams();
    params.set('page', String(state.page));
    params.set('page_size', String(state.page_size));
    params.set('status', state.status);
    params.set('media_type', state.mediaType);
    if (state.keyword) params.set('keyword', state.keyword);
    const data = await callApi(`${apiPrefix.value}/wall?${params.toString()}`);
    state.groups = data?.groups || [];
    state.total_groups = Number(data?.total_groups || 0);
    state.total_records = Number(data?.total_records || 0);
    state.truncated = Boolean(data?.truncated);
    if (data?.config) Object.assign(state.config, data.config);
  } catch (err) {
    state.error = err?.message || String(err);
  } finally {
    state.loading = false;
  }
}

function reload() {
  state.page = 1;
  state.selected = [];
  loadWall();
}

function goPage(page) {
  state.page = page;
  state.selected = [];
  loadWall();
}

function isSelected(key) {
  return state.selected.includes(key)
}

function toggleSelect(key) {
  const index = state.selected.indexOf(key);
  if (index >= 0) state.selected.splice(index, 1);
  else state.selected.push(key);
}

function selectCurrentPage() {
  if (allCurrentSelected.value) {
    state.selected = state.selected.filter((key) => !currentKeys.value.includes(key));
    return
  }
  currentKeys.value.forEach((key) => {
    if (!state.selected.includes(key)) state.selected.push(key);
  });
}

function openDetail(group) {
  state.detail = group;
  state.detailDialog = true;
}

function recordsOfGroups(keys) {
  const records = [];
  const wanted = new Set(keys);
  state.groups.forEach((group) => {
    if (!wanted.has(group.key)) return
    ;(group.records || []).forEach((record) => records.push(record));
  });
  return records
}

function openDelete(ids, label, preset) {
  const wanted = new Set((ids || []).map(Number));
  const records = [];
  state.groups.forEach((group) => {
(group.records || []).forEach((record) => {
      if (wanted.has(Number(record.id))) records.push(record);
    });
  });
  if (state.detail) {
(state.detail.records || []).forEach((record) => {
      if (wanted.has(Number(record.id)) && !records.some((item) => item.id === record.id)) {
        records.push(record);
      }
    });
  }
  if (!records.length) {
    notify('warning', '未找到对应的整理记录，请刷新后重试');
    return
  }
  state.confirmIds = [...wanted];
  state.confirmRecords = records;
  state.confirmLabel = label;
  state.flags = {
    record: preset?.record ?? state.config.default_delete_record,
    src: preset?.src ?? state.config.default_delete_src,
    dest: preset?.dest ?? state.config.default_delete_dest,
  };
  state.confirmText = '';
  state.confirmDialog = true;
}

function openGroupDelete(label, preset) {
  if (!state.detail) return
  const ids = (state.detail.records || []).map((record) => record.id).filter(Boolean);
  openDelete(ids, label, preset);
}

function bulkDelete() {
  const records = recordsOfGroups(state.selected);
  if (!records.length) {
    notify('warning', '所选媒体没有可删除的记录');
    return
  }
  const ids = records.map((record) => record.id).filter(Boolean);
  openDelete(ids, `批量删除 ${state.selected.length} 部媒体`, {
    record: state.config.default_delete_record,
    src: state.config.default_delete_src,
    dest: state.config.default_delete_dest,
  });
}

async function executeDelete() {
  if (needsConfirmText.value && state.confirmText.trim() !== '删除') {
    notify('warning', '请输入「删除」以确认文件删除');
    return
  }
  state.busy = true;
  const maxBatch = Math.max(1, Number(state.config.max_batch || 20));
  const ids = [...state.confirmIds];
  let success = 0;
  let failed = 0;
  const failures = [];
  try {
    for (let index = 0; index < ids.length; index += maxBatch) {
      const chunk = ids.slice(index, index + maxBatch);
      const result = await callApi(`${apiPrefix.value}/delete`, 'post', {
        ids: chunk,
        delete_record: Boolean(state.flags.record),
        delete_src: Boolean(state.flags.src),
        delete_dest: Boolean(state.flags.dest),
        confirm: '删除',
      });
      success += Number(result?.success_count || 0);
      failed += Number(result?.failed_count || 0)
      ;(result?.results || []).forEach((item) => {
        if (item && !item.ok && item.message) failures.push(`#${item.id} ${item.message}`);
      });
    }
    state.confirmDialog = false;
    state.detailDialog = false;
    state.selected = [];
    if (failed) {
      notify('warning', `成功 ${success} 条，失败 ${failed} 条：${failures.slice(0, 3).join('；')}`);
    } else {
      notify('success', `已处理 ${success} 条记录`);
    }
    await loadWall();
  } catch (err) {
    notify('error', err?.message || String(err));
  } finally {
    state.busy = false;
  }
}

onMounted(loadWall);

return (_ctx, _cache) => {
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_text_field = _resolveComponent("v-text-field");
  const _component_v_select = _resolveComponent("v-select");
  const _component_v_chip = _resolveComponent("v-chip");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_card = _resolveComponent("v-card");
  const _component_v_progress_circular = _resolveComponent("v-progress-circular");
  const _component_v_icon = _resolveComponent("v-icon");
  const _component_v_img = _resolveComponent("v-img");
  const _component_v_checkbox_btn = _resolveComponent("v-checkbox-btn");
  const _component_v_col = _resolveComponent("v-col");
  const _component_v_row = _resolveComponent("v-row");
  const _component_v_card_title = _resolveComponent("v-card-title");
  const _component_v_card_item = _resolveComponent("v-card-item");
  const _component_v_spacer = _resolveComponent("v-spacer");
  const _component_v_dialog = _resolveComponent("v-dialog");
  const _component_v_checkbox = _resolveComponent("v-checkbox");
  const _component_v_card_actions = _resolveComponent("v-card-actions");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createVNode(_component_v_card, {
      variant: "outlined",
      class: "tw-panel"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card_text, null, {
          default: _withCtx(() => [
            _createElementVNode("div", _hoisted_2, [
              _cache[18] || (_cache[18] = _createElementVNode("div", null, [
                _createElementVNode("div", { class: "text-h6" }, "整理海报墙"),
                _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, " 按媒体聚合整理记录 · 可删除记录、源文件与媒体库文件 ")
              ], -1)),
              _createVNode(_component_v_btn, {
                icon: "mdi-refresh",
                size: "small",
                variant: "text",
                loading: state.loading,
                title: "刷新",
                onClick: loadWall
              }, null, 8, ["loading"])
            ]),
            _createElementVNode("div", _hoisted_3, [
              _createVNode(_component_v_text_field, {
                modelValue: state.keyword,
                "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => ((state.keyword) = $event)),
                density: "compact",
                variant: "outlined",
                "hide-details": "",
                "prepend-inner-icon": "mdi-magnify",
                label: "搜索标题或路径",
                class: "tw-search",
                onKeyup: _withKeys(reload, ["enter"])
              }, null, 8, ["modelValue"]),
              _createVNode(_component_v_select, {
                modelValue: state.status,
                "onUpdate:modelValue": [
                  _cache[1] || (_cache[1] = $event => ((state.status) = $event)),
                  reload
                ],
                items: statusOptions,
                density: "compact",
                variant: "outlined",
                "hide-details": "",
                label: "状态",
                class: "tw-filter"
              }, null, 8, ["modelValue"]),
              _createVNode(_component_v_select, {
                modelValue: state.mediaType,
                "onUpdate:modelValue": [
                  _cache[2] || (_cache[2] = $event => ((state.mediaType) = $event)),
                  reload
                ],
                items: typeOptions,
                density: "compact",
                variant: "outlined",
                "hide-details": "",
                label: "类型",
                class: "tw-filter"
              }, null, 8, ["modelValue"]),
              _createVNode(_component_v_btn, {
                size: "small",
                variant: "tonal",
                onClick: selectCurrentPage
              }, {
                default: _withCtx(() => [
                  _createTextVNode(_toDisplayString(allCurrentSelected.value ? '取消本页' : '全选本页'), 1)
                ]),
                _: 1
              }),
              _createVNode(_component_v_btn, {
                size: "small",
                color: "error",
                variant: "tonal",
                disabled: !state.selected.length,
                "prepend-icon": "mdi-delete-outline",
                onClick: bulkDelete
              }, {
                default: _withCtx(() => [
                  _createTextVNode(" 批量删除（" + _toDisplayString(state.selected.length) + "） ", 1)
                ]),
                _: 1
              }, 8, ["disabled"])
            ]),
            _createElementVNode("div", _hoisted_4, [
              _createVNode(_component_v_chip, {
                size: "small",
                variant: "tonal"
              }, {
                default: _withCtx(() => [
                  _createTextVNode("媒体 " + _toDisplayString(state.total_groups), 1)
                ]),
                _: 1
              }),
              _createVNode(_component_v_chip, {
                size: "small",
                variant: "tonal"
              }, {
                default: _withCtx(() => [
                  _createTextVNode("记录 " + _toDisplayString(state.total_records), 1)
                ]),
                _: 1
              }),
              (state.truncated)
                ? (_openBlock(), _createBlock(_component_v_chip, {
                    key: 0,
                    size: "small",
                    color: "warning",
                    variant: "tonal"
                  }, {
                    default: _withCtx(() => [...(_cache[19] || (_cache[19] = [
                      _createTextVNode(" 仅显示最近记录 ", -1)
                    ]))]),
                    _: 1
                  }))
                : _createCommentVNode("", true)
            ]),
            (state.error || state.localMessage)
              ? (_openBlock(), _createBlock(_component_v_alert, {
                  key: 0,
                  type: "error",
                  variant: "tonal",
                  class: "tw-alert"
                }, {
                  default: _withCtx(() => [
                    _createTextVNode(_toDisplayString(state.error || state.localMessage), 1)
                  ]),
                  _: 1
                }))
              : _createCommentVNode("", true)
          ]),
          _: 1
        })
      ]),
      _: 1
    }),
    (state.loading && !state.groups.length)
      ? (_openBlock(), _createElementBlock("div", _hoisted_5, [
          _createVNode(_component_v_progress_circular, {
            indeterminate: "",
            color: "primary"
          })
        ]))
      : (!state.groups.length)
        ? (_openBlock(), _createElementBlock("div", _hoisted_6, [
            _createVNode(_component_v_icon, { size: "48" }, {
              default: _withCtx(() => [...(_cache[20] || (_cache[20] = [
                _createTextVNode("mdi-image-off-outline", -1)
              ]))]),
              _: 1
            }),
            _cache[21] || (_cache[21] = _createElementVNode("div", { class: "mt-2" }, "暂无整理记录", -1))
          ]))
        : (_openBlock(), _createBlock(_component_v_row, {
            key: 2,
            class: "tw-grid"
          }, {
            default: _withCtx(() => [
              (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(state.groups, (group) => {
                return (_openBlock(), _createBlock(_component_v_col, {
                  key: group.key,
                  cols: "6",
                  sm: "4",
                  md: "3",
                  lg: "2",
                  xl: "2",
                  class: "tw-cell"
                }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_card, {
                      class: "tw-media-card",
                      variant: "outlined",
                      onClick: $event => (openDetail(group))
                    }, {
                      default: _withCtx(() => [
                        _createElementVNode("div", _hoisted_7, [
                          (group.poster)
                            ? (_openBlock(), _createBlock(_component_v_img, {
                                key: 0,
                                src: group.poster,
                                cover: "",
                                class: "tw-poster"
                              }, null, 8, ["src"]))
                            : (_openBlock(), _createElementBlock("div", _hoisted_8, [
                                _createVNode(_component_v_icon, { size: "40" }, {
                                  default: _withCtx(() => [...(_cache[22] || (_cache[22] = [
                                    _createTextVNode("mdi-image-off-outline", -1)
                                  ]))]),
                                  _: 1
                                }),
                                _createElementVNode("span", _hoisted_9, _toDisplayString(group.title), 1)
                              ])),
                          _createElementVNode("div", {
                            class: "tw-select-wrap",
                            onClick: _cache[3] || (_cache[3] = _withModifiers(() => {}, ["stop"]))
                          }, [
                            _createVNode(_component_v_checkbox_btn, {
                              "model-value": isSelected(group.key),
                              color: "primary",
                              density: "compact",
                              "onUpdate:modelValue": $event => (toggleSelect(group.key))
                            }, null, 8, ["model-value", "onUpdate:modelValue"])
                          ]),
                          _createElementVNode("div", _hoisted_10, [
                            _createElementVNode("div", {
                              class: "tw-title",
                              title: group.title
                            }, _toDisplayString(group.title), 9, _hoisted_11),
                            _createElementVNode("div", _hoisted_12, [
                              (group.year)
                                ? (_openBlock(), _createElementBlock("span", _hoisted_13, _toDisplayString(group.year), 1))
                                : _createCommentVNode("", true),
                              (group.type)
                                ? (_openBlock(), _createElementBlock("span", _hoisted_14, _toDisplayString(group.type), 1))
                                : _createCommentVNode("", true),
                              _createElementVNode("span", null, _toDisplayString(group.record_count) + " 条", 1)
                            ]),
                            _createElementVNode("div", _hoisted_15, [
                              _createVNode(_component_v_chip, {
                                size: "x-small",
                                color: "success",
                                variant: "tonal"
                              }, {
                                default: _withCtx(() => [
                                  _createTextVNode(_toDisplayString(group.success_count) + " 成功 ", 1)
                                ]),
                                _: 2
                              }, 1024),
                              (group.fail_count)
                                ? (_openBlock(), _createBlock(_component_v_chip, {
                                    key: 0,
                                    size: "x-small",
                                    color: "error",
                                    variant: "tonal"
                                  }, {
                                    default: _withCtx(() => [
                                      _createTextVNode(_toDisplayString(group.fail_count) + " 失败 ", 1)
                                    ]),
                                    _: 2
                                  }, 1024))
                                : _createCommentVNode("", true),
                              (group.src_count)
                                ? (_openBlock(), _createBlock(_component_v_chip, {
                                    key: 1,
                                    size: "x-small",
                                    variant: "tonal",
                                    title: "源文件数量"
                                  }, {
                                    default: _withCtx(() => [
                                      _createVNode(_component_v_icon, {
                                        start: "",
                                        size: "x-small"
                                      }, {
                                        default: _withCtx(() => [...(_cache[23] || (_cache[23] = [
                                          _createTextVNode("mdi-download", -1)
                                        ]))]),
                                        _: 1
                                      }),
                                      _createTextVNode(_toDisplayString(group.src_count), 1)
                                    ]),
                                    _: 2
                                  }, 1024))
                                : _createCommentVNode("", true),
                              (group.dest_count)
                                ? (_openBlock(), _createBlock(_component_v_chip, {
                                    key: 2,
                                    size: "x-small",
                                    variant: "tonal",
                                    title: "媒体库文件数量"
                                  }, {
                                    default: _withCtx(() => [
                                      _createVNode(_component_v_icon, {
                                        start: "",
                                        size: "x-small"
                                      }, {
                                        default: _withCtx(() => [...(_cache[24] || (_cache[24] = [
                                          _createTextVNode("mdi-folder-play", -1)
                                        ]))]),
                                        _: 1
                                      }),
                                      _createTextVNode(_toDisplayString(group.dest_count), 1)
                                    ]),
                                    _: 2
                                  }, 1024))
                                : _createCommentVNode("", true)
                            ])
                          ])
                        ])
                      ]),
                      _: 2
                    }, 1032, ["onClick"])
                  ]),
                  _: 2
                }, 1024))
              }), 128))
            ]),
            _: 1
          })),
    (state.total_groups > state.page_size)
      ? (_openBlock(), _createElementBlock("div", _hoisted_16, [
          _createVNode(_component_v_btn, {
            size: "small",
            variant: "text",
            disabled: state.page <= 1,
            onClick: _cache[4] || (_cache[4] = $event => (goPage(state.page - 1)))
          }, {
            default: _withCtx(() => [...(_cache[25] || (_cache[25] = [
              _createTextVNode(" 上一页 ", -1)
            ]))]),
            _: 1
          }, 8, ["disabled"]),
          _createElementVNode("span", _hoisted_17, _toDisplayString(state.page) + " / " + _toDisplayString(Math.max(1, Math.ceil(state.total_groups / state.page_size))), 1),
          _createVNode(_component_v_btn, {
            size: "small",
            variant: "text",
            disabled: state.page * state.page_size >= state.total_groups,
            onClick: _cache[5] || (_cache[5] = $event => (goPage(state.page + 1)))
          }, {
            default: _withCtx(() => [...(_cache[26] || (_cache[26] = [
              _createTextVNode(" 下一页 ", -1)
            ]))]),
            _: 1
          }, 8, ["disabled"])
        ]))
      : _createCommentVNode("", true),
    _createVNode(_component_v_dialog, {
      modelValue: state.detailDialog,
      "onUpdate:modelValue": _cache[11] || (_cache[11] = $event => ((state.detailDialog) = $event)),
      "max-width": "960",
      scrollable: ""
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card, null, {
          default: _withCtx(() => [
            _createVNode(_component_v_card_item, null, {
              append: _withCtx(() => [
                _createVNode(_component_v_btn, {
                  icon: "mdi-close",
                  size: "small",
                  variant: "text",
                  onClick: _cache[6] || (_cache[6] = $event => (state.detailDialog = false))
                })
              ]),
              default: _withCtx(() => [
                _createVNode(_component_v_card_title, null, {
                  default: _withCtx(() => [
                    _createTextVNode(_toDisplayString(state.detail?.title || '整理详情'), 1)
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_text, { class: "tw-detail-body" }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_18, [
                  (state.detail?.poster)
                    ? (_openBlock(), _createBlock(_component_v_img, {
                        key: 0,
                        src: state.detail.poster,
                        cover: "",
                        width: "100",
                        height: "150",
                        class: "tw-detail-poster"
                      }, null, 8, ["src"]))
                    : _createCommentVNode("", true),
                  _createElementVNode("div", _hoisted_19, [
                    _createElementVNode("div", _hoisted_20, _toDisplayString(state.detail?.year || '未知年份') + " · " + _toDisplayString(state.detail?.type || '未分类'), 1),
                    _createElementVNode("div", _hoisted_21, [
                      _createTextVNode(_toDisplayString(state.detail?.record_count || 0) + " 条整理记录 ", 1),
                      (state.detail?.seasons)
                        ? (_openBlock(), _createElementBlock("span", _hoisted_22, " · 季：" + _toDisplayString(state.detail.seasons), 1))
                        : _createCommentVNode("", true),
                      (state.detail?.records_truncated)
                        ? (_openBlock(), _createElementBlock("span", _hoisted_23, " · 仅显示最近 200 条"))
                        : _createCommentVNode("", true)
                    ]),
                    _createElementVNode("div", _hoisted_24, [
                      _createVNode(_component_v_btn, {
                        size: "x-small",
                        variant: "tonal",
                        onClick: _cache[7] || (_cache[7] = $event => (openGroupDelete('仅删除本媒体记录', { record: true, src: false, dest: false })))
                      }, {
                        default: _withCtx(() => [...(_cache[27] || (_cache[27] = [
                          _createTextVNode(" 删除全部记录 ", -1)
                        ]))]),
                        _: 1
                      }),
                      _createVNode(_component_v_btn, {
                        size: "x-small",
                        color: "warning",
                        variant: "tonal",
                        onClick: _cache[8] || (_cache[8] = $event => (openGroupDelete('删除本媒体源文件', { record: false, src: true, dest: false })))
                      }, {
                        default: _withCtx(() => [...(_cache[28] || (_cache[28] = [
                          _createTextVNode(" 删除源文件 ", -1)
                        ]))]),
                        _: 1
                      }),
                      _createVNode(_component_v_btn, {
                        size: "x-small",
                        color: "error",
                        variant: "tonal",
                        onClick: _cache[9] || (_cache[9] = $event => (openGroupDelete('删除本媒体库文件', { record: false, src: false, dest: true })))
                      }, {
                        default: _withCtx(() => [...(_cache[29] || (_cache[29] = [
                          _createTextVNode(" 删除媒体库文件 ", -1)
                        ]))]),
                        _: 1
                      }),
                      _createVNode(_component_v_btn, {
                        size: "x-small",
                        color: "error",
                        variant: "flat",
                        onClick: _cache[10] || (_cache[10] = $event => (openGroupDelete('删除本媒体记录、源文件与媒体库文件', { record: true, src: true, dest: true })))
                      }, {
                        default: _withCtx(() => [...(_cache[30] || (_cache[30] = [
                          _createTextVNode(" 全部删除 ", -1)
                        ]))]),
                        _: 1
                      })
                    ])
                  ])
                ]),
                (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(state.detail?.records || [], (record) => {
                  return (_openBlock(), _createElementBlock("div", {
                    key: record.id,
                    class: "tw-record"
                  }, [
                    _createElementVNode("div", _hoisted_25, [
                      _createVNode(_component_v_chip, {
                        size: "x-small",
                        color: record.status ? 'success' : 'error',
                        variant: "tonal"
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode(_toDisplayString(record.status ? '成功' : '失败'), 1)
                        ]),
                        _: 2
                      }, 1032, ["color"]),
                      _createElementVNode("span", _hoisted_26, _toDisplayString(record.date || ' unknown date'), 1),
                      (record.seasons)
                        ? (_openBlock(), _createElementBlock("span", _hoisted_27, "S" + _toDisplayString(record.seasons), 1))
                        : _createCommentVNode("", true),
                      (record.episodes)
                        ? (_openBlock(), _createElementBlock("span", _hoisted_28, "E" + _toDisplayString(record.episodes), 1))
                        : _createCommentVNode("", true),
                      _createVNode(_component_v_spacer),
                      _createVNode(_component_v_btn, {
                        size: "x-small",
                        variant: "text",
                        onClick: $event => (openDelete([record.id], '删除单条整理记录', { record: true, src: false, dest: false }))
                      }, {
                        default: _withCtx(() => [...(_cache[31] || (_cache[31] = [
                          _createTextVNode(" 删记录 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["onClick"]),
                      _createVNode(_component_v_btn, {
                        size: "x-small",
                        color: "warning",
                        variant: "text",
                        onClick: $event => (openDelete([record.id], '删除单条源文件', { record: false, src: true, dest: false }))
                      }, {
                        default: _withCtx(() => [...(_cache[32] || (_cache[32] = [
                          _createTextVNode(" 删源 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["onClick"]),
                      _createVNode(_component_v_btn, {
                        size: "x-small",
                        color: "error",
                        variant: "text",
                        onClick: $event => (openDelete([record.id], '删除单条媒体库文件', { record: false, src: false, dest: true }))
                      }, {
                        default: _withCtx(() => [...(_cache[33] || (_cache[33] = [
                          _createTextVNode(" 删库 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["onClick"]),
                      _createVNode(_component_v_btn, {
                        size: "x-small",
                        color: "error",
                        variant: "tonal",
                        onClick: $event => (openDelete([record.id], '删除单条记录及全部关联文件', { record: true, src: true, dest: true }))
                      }, {
                        default: _withCtx(() => [...(_cache[34] || (_cache[34] = [
                          _createTextVNode(" 全删 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["onClick"])
                    ]),
                    _createElementVNode("div", _hoisted_29, [
                      _cache[35] || (_cache[35] = _createElementVNode("span", { class: "tw-path-label" }, "源：", -1)),
                      _createTextVNode(_toDisplayString(record.src || '—'), 1)
                    ]),
                    _createElementVNode("div", _hoisted_30, [
                      _cache[36] || (_cache[36] = _createElementVNode("span", { class: "tw-path-label" }, "库：", -1)),
                      _createTextVNode(_toDisplayString(record.dest || '—'), 1)
                    ]),
                    (!record.status && record.errmsg)
                      ? (_openBlock(), _createElementBlock("div", _hoisted_31, _toDisplayString(record.errmsg), 1))
                      : _createCommentVNode("", true)
                  ]))
                }), 128))
              ]),
              _: 1
            })
          ]),
          _: 1
        })
      ]),
      _: 1
    }, 8, ["modelValue"]),
    _createVNode(_component_v_dialog, {
      modelValue: state.confirmDialog,
      "onUpdate:modelValue": _cache[17] || (_cache[17] = $event => ((state.confirmDialog) = $event)),
      "max-width": "720",
      persistent: ""
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card, null, {
          default: _withCtx(() => [
            _createVNode(_component_v_card_item, null, {
              default: _withCtx(() => [
                _createVNode(_component_v_card_title, { class: "tw-confirm-title" }, {
                  default: _withCtx(() => [...(_cache[37] || (_cache[37] = [
                    _createTextVNode("确认删除", -1)
                  ]))]),
                  _: 1
                })
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_text, null, {
              default: _withCtx(() => [
                _createVNode(_component_v_alert, {
                  type: "warning",
                  variant: "tonal",
                  class: "tw-alert"
                }, {
                  default: _withCtx(() => [...(_cache[38] || (_cache[38] = [
                    _createTextVNode(" 文件删除不可恢复，也不会进入回收站。请确认已停止相关下载/做种任务。 ", -1)
                  ]))]),
                  _: 1
                }),
                _createElementVNode("div", _hoisted_32, [
                  _createTextVNode(_toDisplayString(state.confirmLabel) + " · 共 " + _toDisplayString(state.confirmIds.length) + " 条记录 ", 1),
                  (state.confirmIds.length > (state.config.max_batch || 20))
                    ? (_openBlock(), _createElementBlock("span", _hoisted_33, " （将分 " + _toDisplayString(Math.ceil(state.confirmIds.length / (state.config.max_batch || 20))) + " 批执行） ", 1))
                    : _createCommentVNode("", true)
                ]),
                _createElementVNode("div", _hoisted_34, [
                  (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(state.confirmRecords.slice(0, 8), (record) => {
                    return (_openBlock(), _createElementBlock("div", {
                      key: record.id,
                      class: "tw-path-list-item"
                    }, [
                      _createElementVNode("div", _hoisted_35, "#" + _toDisplayString(record.id) + " " + _toDisplayString(record.title || ''), 1),
                      _createElementVNode("div", _hoisted_36, "源：" + _toDisplayString(record.src || '—'), 1),
                      _createElementVNode("div", _hoisted_37, "库：" + _toDisplayString(record.dest || '—'), 1)
                    ]))
                  }), 128)),
                  (state.confirmRecords.length > 8)
                    ? (_openBlock(), _createElementBlock("div", _hoisted_38, " 另有 " + _toDisplayString(state.confirmRecords.length - 8) + " 条未显示 ", 1))
                    : _createCommentVNode("", true)
                ]),
                _createVNode(_component_v_checkbox, {
                  modelValue: state.flags.record,
                  "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((state.flags.record) = $event)),
                  label: "删除整理记录",
                  density: "compact",
                  "hide-details": ""
                }, null, 8, ["modelValue"]),
                _createVNode(_component_v_checkbox, {
                  modelValue: state.flags.src,
                  "onUpdate:modelValue": _cache[13] || (_cache[13] = $event => ((state.flags.src) = $event)),
                  label: "删除源文件（下载目录）",
                  density: "compact",
                  "hide-details": "",
                  color: "warning"
                }, null, 8, ["modelValue"]),
                _createVNode(_component_v_checkbox, {
                  modelValue: state.flags.dest,
                  "onUpdate:modelValue": _cache[14] || (_cache[14] = $event => ((state.flags.dest) = $event)),
                  label: "删除媒体库文件",
                  density: "compact",
                  "hide-details": "",
                  color: "error"
                }, null, 8, ["modelValue"]),
                (needsConfirmText.value)
                  ? (_openBlock(), _createBlock(_component_v_text_field, {
                      key: 0,
                      modelValue: state.confirmText,
                      "onUpdate:modelValue": _cache[15] || (_cache[15] = $event => ((state.confirmText) = $event)),
                      density: "compact",
                      variant: "outlined",
                      "hide-details": "",
                      class: "tw-confirm-input",
                      label: "请输入「删除」以确认文件删除"
                    }, null, 8, ["modelValue"]))
                  : _createCommentVNode("", true)
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_actions, null, {
              default: _withCtx(() => [
                _createVNode(_component_v_spacer),
                _createVNode(_component_v_btn, {
                  variant: "text",
                  disabled: state.busy,
                  onClick: _cache[16] || (_cache[16] = $event => (state.confirmDialog = false))
                }, {
                  default: _withCtx(() => [...(_cache[39] || (_cache[39] = [
                    _createTextVNode("取消", -1)
                  ]))]),
                  _: 1
                }, 8, ["disabled"]),
                _createVNode(_component_v_btn, {
                  color: "error",
                  variant: "flat",
                  loading: state.busy,
                  onClick: executeDelete
                }, {
                  default: _withCtx(() => [...(_cache[40] || (_cache[40] = [
                    _createTextVNode("确认删除", -1)
                  ]))]),
                  _: 1
                }, 8, ["loading"])
              ]),
              _: 1
            })
          ]),
          _: 1
        })
      ]),
      _: 1
    }, 8, ["modelValue"])
  ]))
}
}

};
const AppPage = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-e6c329aa"]]);

export { AppPage as default };
