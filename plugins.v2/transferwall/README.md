# 整理海报墙（TransferWall）

MoviePilot **V2** 插件。安装启用后，在主界面左侧 **整理** 分组中出现「整理海报墙」入口，以海报墙形式展示整理（转移）记录，并支持删除：

- 整理记录（数据库记录）
- 源文件（下载目录中的文件/目录）
- 媒体库文件（整理目标文件/目录）

插件 ID：`TransferWall`

## 功能

- 按媒体聚合整理记录：电影/电视剧按 `媒体来源 + 媒体ID` 聚合，无媒体 ID 时按 `类型 + 标题 + 年份` 聚合。
- 海报墙展示：使用整理记录中已刮削的海报，支持搜索、成功/失败筛选、电影/电视剧筛选、分页。
- 每张海报显示记录数、成功/失败数、源文件数、媒体库文件数，支持勾选和批量删除。
- 点击海报进入详情：逐条查看源路径、目标路径、季集、状态，并可单条删除。
- 删除动作与 MoviePilot 原生「删除整理记录」一致：
  - 通过 `StorageChain.delete_media_file()` 删除文件，自动清理空目录；
  - 删除源文件后清理下载记录中的文件项并发送 `DownloadFileDeleted` 事件；
  - 最后删除整理记录。
- 安全约束：
  - 删除接口需要「管理」权限；
  - 删除文件必须在弹窗中输入 `删除` 二次确认；
  - 单次批量删除默认最多 20 条，可在配置中调整（上限 100）；
  - 删除源文件失败时不会删除对应整理记录，避免丢失记录后仍残留文件。

## 安装

1. 将整个 `transferwall` 目录复制到 MoviePilot 插件目录：

   ```text
   {MOVIEPILOT_CONFIG}/plugins/transferwall/
   ```

   目录应包含：

   ```text
   transferwall/
   ├── __init__.py
   ├── dist/assets/remoteEntry.js
   ├── dist/assets/__federation_*.js / .css
   └── dist/assets/_plugin-vue_export-helper-*.js
   ```

2. 在 MoviePilot「插件」页面安装/刷新插件，打开「整理海报墙」配置：
   - 勾选 **启用插件并显示侧栏入口**；
   - 可修改菜单标题、图标、最多读取记录数、批量删除上限；
   - 文件删除默认不勾选，建议在确认弹窗中按需选择。
3. 刷新前端页面，左侧 **整理** 分组出现「整理海报墙」。

> 已构建好的联邦组件放在 `dist/assets`，无需重新编译即可使用。

## 插件市场索引条目

复制以下内容到插件仓库的 `package.v2.json`：

```json
"TransferWall": {
  "name": "整理海报墙",
  "description": "在整理菜单显示转移记录海报墙，支持删除记录、源文件和媒体库文件。",
  "labels": "整理,海报墙,文件清理",
  "version": "1.0.0",
  "icon": "Moviepilot_A.png",
  "author": "WorkBuddy",
  "system_version": ">=2.12.0",
  "level": 1
}
```

同目录的 `package.v2.json` 中也包含该条目，便于直接复制。

## 前端重新构建

源码位于 `web/`，需要 Node.js 20+：

```bash
cd web
npm install
npm run build
```

构建产物直接输出到 `../dist/assets`。构建后请删除生成的 `index.html`、`index-*.js` 和 `__federation_shared_vuetify/` 目录，只保留：

- `remoteEntry.js`
- `__federation_*.js` / `__federation_*.css`
- `_plugin-vue_export-helper-*.js`

## API

插件 API 路径前缀：`/api/v1/plugin/TransferWall`（所有接口 `auth: bear`）。

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/wall` | 查询海报墙；参数 `keyword`、`status=all/success/fail`、`media_type=all/movie/tv`、`page`、`page_size` |
| GET | `/config` | 读取当前配置 |
| POST | `/config` | 保存配置（管理权限） |
| POST | `/delete` | 删除；body：`ids`、`delete_record`、`delete_src`、`delete_dest`、`confirm: "删除"` |

## 注意事项

- 删除操作直接作用于真实文件，不进入回收站，请先确认下载/做种任务状态。
- 若源文件与媒体库文件是硬链接，删除源文件不会影响同一 inode 的媒体库文件；若目标文件独立存在，请按需单独删除媒体库文件。
- 插件只读取 MoviePilot 的整理记录，不会修改宿主代码。
