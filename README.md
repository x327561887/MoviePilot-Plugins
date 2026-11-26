# MoviePilot 自定义插件仓库

本仓库按 MoviePilot 插件市场规范组织，可作为自定义仓库地址添加到 `PLUGIN_MARKET`，直接安装 V2 插件。

**仓库地址：** https://github.com/x327561887/MoviePilot-Plugins

## 安装方法

1. 打开 MoviePilot → **设置** → **插件** → **插件市场设置**（`PLUGIN_MARKET`）。
2. 添加上面的仓库地址（多个仓库用英文逗号分隔）。MoviePilot 只读取 `main` 分支。
3. 进入 **插件** → **插件市场**，找到对应插件点击安装、启用。

## 仓库结构

```text
.
├── package.v2.json          # 插件市场索引（V2），键为插件 ID
├── README.md
├── icons/                   # 插件图标
│   └── transferwall.png
└── plugins.v2/              # V2 插件源码目录（目录名为插件 ID 小写）
    ├── transferwall/        # 整理海报墙
    └── batchrename/         # 批量改名
```

MoviePilot 安装时先读取根目录 `package.v2.json`，再从 `plugins.v2/<插件ID小写>/` 逐文件下载到运行目录 `app/plugins/<插件ID小写>/`。

> 索引顶层必须是「插件 ID → 元数据」对象（如 `"TransferWall": { ... }`），不是数组；源码目录必须是 `plugins.v2/`，不是 `plugins/v2/`。

## 插件列表

| 插件 ID | 名称 | 说明 |
| --- | --- | --- |
| `TransferWall` | 整理海报墙 | 在「整理」分组显示转移记录海报墙，支持删除整理记录、源文件、媒体库文件 |
| `BatchRename` | 批量改名 | 起始集号作为锚点，小于它的文件标记不匹配，其余从修改集数起累加，勾选后批量改名 |

## TransferWall（整理海报墙）

- 按 `媒体来源 + 媒体ID` 聚合整理记录，无媒体 ID 时按 `类型 + 标题 + 年份` 聚合。
- 海报墙支持搜索、成功/失败筛选、电影/电视剧筛选、分页、勾选批量删除。
- 点击海报进入详情，逐条查看源路径、目标路径、季集、状态，并可单条删除。
- 删除项可独立组合：整理记录、源文件、媒体库文件。
- 删除逻辑对齐 MoviePilot V2 原生接口：`StorageChain.delete_media_file()` 删除文件并清理空目录，清理下载记录文件项并发送 `DownloadFileDeleted` 事件，最后删除整理记录。
- 安全约束：管理权限校验、输入「删除」二次确认、单次批量上限默认 20（可在配置中调整，最高 100）、源文件删除失败时不删除对应记录。

API 前缀：`/api/v1/plugin/TransferWall`

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/wall` | 查询海报墙；`keyword`、`status=all/success/fail`、`media_type=all/movie/tv`、`page`、`page_size` |
| GET | `/config` | 读取配置 |
| POST | `/config` | 保存配置（管理权限） |
| POST | `/delete` | 删除；`ids`、`delete_record`、`delete_src`、`delete_dest`、`confirm: "删除"` |

前端源码位于 `plugins.v2/transferwall/web/`，编译产物在 `plugins.v2/transferwall/dist/assets/`，正常安装无需重新编译。重新编译：

```bash
cd plugins.v2/transferwall/web
npm install
npm run build
```

构建后删除 `index.html`、`index-*.js` 和 `__federation_shared_vuetify/`，只保留 `remoteEntry.js`、`__federation_*.js/.css`、`_plugin-vue_export-helper-*.js`。

## BatchRename（批量改名）

- Vue 联邦模块界面：配置页只填剧集目录与处理扩展名（默认 `mp4,mkv,srt,ass`）；详情页填目标季号、起始集号、修改集数。
- **起始集号是改名锚点**：目录中必须存在该集号的文件，否则全部标记「不匹配」；集号小于起始集的文件同样标记「不匹配」，不参与改名、不可勾选。
- 其余文件从「修改集数」开始累加：**新集号 = 修改集数 +（原集号 − 起始集号）**。例：起始 68、修改集数 100 → E68→E100、E69→E101、E77→E109。
- 季号统一替换为目标季号，「第 XX 集」自动跟随新集号；同一原集数的视频与字幕共用同一个新集号。
- 点「预览改名」列出清单（原文件名 → 修改后文件名），逐行勾选（支持全选）后批量执行；不覆盖已有文件，失败自动回滚，可一键恢复上次改名。

API 前缀：`/api/v1/plugin/BatchRename`

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/config` | 读取配置 |
| POST | `/config` | 保存配置 |
| POST | `/preview` | 预览改名清单（传 `season`、`start`、`target`） |
| POST | `/apply` | 按选中的原文件名执行改名 |
| POST | `/undo` | 恢复上次改名 |

## 安全说明

- 删除与改名操作直接作用于真实文件，不进入回收站，请先确认下载/做种任务状态。
- 若源文件与媒体库文件是硬链接，删除源文件不会影响同一 inode 的媒体库文件；若目标文件独立存在，请按需单独删除媒体库文件。
- 插件只读取 MoviePilot 的整理记录与本地文件，不修改宿主代码。
