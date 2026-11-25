# -*- coding: utf-8 -*-
"""MoviePilot V2 批量改名插件。

配置页填写剧集目录、处理扩展名、目标季号与起始集号；详情页点「预览改名」列出文件，
逐行点「选择」挑选要改的文件，再执行批量改名。

改名规则：保留原标题，季号统一替换为目标季号，选中文件按原集数从小到大依次改为
起始集起的连续集号，「第 XX 集」自动跟随新集号。已为目标季号的文件标为「已存在」不改动。

示例（目标季号 1、起始集号 72）：
    Re：从零开始的异世界生活 - S04E06 - 第 6 集.mkv
    -> Re：从零开始的异世界生活 - S01E72 - 第 72 集.mkv

执行不覆盖已有文件，失败自动回滚，并可一键恢复上次改名。
"""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fastapi import Body
from fastapi.responses import JSONResponse

from app.plugins import _PluginBase
from app.log import logger


DEFAULT_EXTENSIONS = "mp4,mkv,srt,ass"
PREVIEW_KEY = "batch_rename_preview"
APPLY_KEY = "batch_rename_last_apply"
SELECT_KEY = "batch_rename_selection"

STATUS_LABELS = {
    "ready": "待修改",
    "exist": "已存在",
    "done": "已改名",
    "conflict": "跳过（冲突）",
}


class BatchRename(_PluginBase):
    """按目标季号与起始集批量重排剧集编号的插件。"""

    plugin_name = "批量改名（顺序重编号）"
    plugin_desc = "设置目录后预览文件、逐行勾选批量改名：季号统一替换，集号按起始集递增，中文集数自动同步。"
    plugin_icon = "https://raw.githubusercontent.com/x327561887/MoviePilot-Plugins/main/plugins.v2/batchrename/icon.png"
    plugin_version = "1.1.0"
    plugin_author = "x327561887"
    author_url = "https://github.com/x327561887"
    plugin_config_prefix = "batchrename_"
    plugin_order = 50
    auth_level = 1

    _enabled = False
    _source_dir = ""
    _extensions = DEFAULT_EXTENSIONS
    _season = 1
    _start_episode = 1

    def init_plugin(self, config: Optional[Dict[str, Any]] = None) -> None:
        if config is None:
            try:
                config = self.get_config() or {}
            except Exception:
                config = {}
        config = config or {}
        self._enabled = bool(config.get("enabled"))
        self._source_dir = str(config.get("source_dir") or "").strip()
        self._extensions = str(config.get("extensions") or DEFAULT_EXTENSIONS).strip() or DEFAULT_EXTENSIONS
        self._season = self._as_int(config.get("season"), 1, 0, 999)
        self._start_episode = self._as_int(config.get("start_episode"), 1, 1, 99999)

    def get_state(self) -> bool:
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        return []

    def get_api(self) -> List[Dict[str, Any]]:
        return [
            {
                "path": "/preview",
                "endpoint": self.api_preview,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "预览改名",
                "description": "按配置扫描目录生成改名清单，不修改文件。",
            },
            {
                "path": "/select",
                "endpoint": self.api_select,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "选择/取消文件",
                "description": "传入 index 切换该文件的选中状态，或传 action=all/none 全选/清空。",
            },
            {
                "path": "/apply",
                "endpoint": self.api_apply,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "执行批量改名",
                "description": "按选中的文件执行改名，失败时自动回滚。",
            },
            {
                "path": "/undo",
                "endpoint": self.api_undo,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "恢复上次改名",
                "description": "按最近一次执行记录把文件名改回原名。",
            },
        ]

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """配置页：目录、扩展名、目标季号、起始集号。"""
        fields = [
            self._field("VSwitch", "enabled", "启用插件", md=3),
            self._field(
                "VTextField", "source_dir", "剧集目录（容器内的绝对路径）", md=9,
                placeholder="/media/电视剧/日番/Re：从零开始的异世界生活/Season 4",
            ),
            self._field("VTextField", "extensions", "处理扩展名（逗号分隔）", md=6,
                        placeholder=DEFAULT_EXTENSIONS),
            self._field("VTextField", "season", "目标季号 SXX", md=3, type="number"),
            self._field("VTextField", "start_episode", "起始集号", md=3, type="number"),
        ]
        return [
            {
                "component": "VForm",
                "content": [
                    {
                        "component": "VAlert",
                        "props": {
                            "type": "info",
                            "variant": "tonal",
                            "class": "mb-4",
                            "text": (
                                "填写目录与扩展名（默认 mp4, mkv, srt, ass），并设置目标季号与起始集号。"
                                "保存后到详情页点「预览改名」，逐行选择要改的文件再执行。"
                                "改名规则：保留原标题，季号统一替换，集号按原顺序从起始集连续递增，"
                                "「第 XX 集」自动跟随新集号。"
                            ),
                        },
                    },
                    {"component": "VRow", "content": fields},
                ],
            }
        ], self._current_config()

    def get_page(self) -> List[dict]:
        """详情页：预览清单 + 逐行选择 + 执行/恢复。"""
        preview = self.get_data(PREVIEW_KEY) or {}
        applied = self.get_data(APPLY_KEY) or {}
        selection = self.get_data(SELECT_KEY) or {}
        if not isinstance(preview, dict):
            preview = {}
        if not isinstance(applied, dict):
            applied = {}
        if not isinstance(selection, dict):
            selection = {}

        items = preview.get("items") or []
        ready_count = sum(
            1 for item in items
            if isinstance(item, dict) and item.get("status") == "ready"
        )
        selected_ids = set(selection.get("ids") or [])
        selected_ready = sum(
            1 for index, item in enumerate(items)
            if isinstance(item, dict) and item.get("status") == "ready" and str(index) in selected_ids
        )

        summary = (
            f"预览时间：{preview.get('generated_at') or '无'} | "
            f"待修改：{ready_count} | 已选择：{selected_ready} | "
            f"目标季号：S{str(self._season).zfill(2)} | 起始集：{self._start_episode} | "
            f"最近执行：{applied.get('applied_at') or '无'}"
        )
        headers = [
            {"title": "选择", "key": "pick"},
            {"title": "状态", "key": "status"},
            {"title": "原文件名", "key": "old_name"},
            {"title": "新文件名", "key": "new_name"},
            {"title": "原集", "key": "old_episode"},
            {"title": "新集", "key": "new_episode"},
        ]
        rows: List[dict] = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            status_raw = str(item.get("status") or "")
            is_ready = status_raw == "ready"
            picked = str(index) in selected_ids
            rows.append({
                "pick": "已选" if picked else "选择",
                "status": STATUS_LABELS.get(status_raw, status_raw),
                "old_name": str(item.get("old_name") or ""),
                "new_name": str(item.get("new_name") or ""),
                "old_episode": str(item.get("old_episode") or ""),
                "new_episode": str(item.get("new_episode") or ""),
                "_index": str(index),
                "_ready": is_ready,
            })

        pick_buttons = []
        for row in rows:
            if not row["_ready"]:
                continue
            index = row["_index"]
            picked = index in selected_ids
            pick_buttons.append(
                self._select_button(index, picked)
            )

        return [
            {"component": "VAlert", "props": {"type": "info", "variant": "tonal", "text": summary}},
            {
                "component": "div",
                "props": {"class": "d-flex flex-wrap align-center ga-2 my-4"},
                "content": [
                    self._action_button("预览改名", "mdi-file-search-outline", "/preview", "primary"),
                    self._action_button("全选", "mdi-check-all", "/select", "secondary",
                                        params={"action": "all"}),
                    self._action_button("清空选择", "mdi-close-circle-outline", "/select", "secondary",
                                        params={"action": "none"}),
                    self._action_button(
                        "执行批量改名", "mdi-pencil-box-multiple-outline", "/apply", "success",
                        disabled=selected_ready == 0,
                    ),
                    self._action_button(
                        "恢复上次改名", "mdi-undo", "/undo", "secondary",
                        disabled=not applied.get("items"),
                    ),
                ],
            },
            {
                "component": "VAlert",
                "props": {
                    "type": "info", "variant": "tonal", "class": "mb-4",
                    "text": (
                        "改名规则：保留原标题，季号统一替换为目标季号；选中文件按原集数从小到大，"
                        "依次改为起始集起的连续集号；「第 XX 集」按新集号自动改写。"
                        "点击每行「选择」按钮可切换是否处理该文件，已存在的不参与。"
                    ),
                },
            },
            {
                "component": "VDataTable",
                "props": {
                    "density": "compact",
                    "headers": headers,
                    "items": [{k: v for k, v in row.items() if not k.startswith("_")} for row in rows],
                    "item-value": "old_name",
                    "items-per-page": 50,
                },
            },
            {
                "component": "VAlert",
                "props": {
                    "type": "warning" if preview.get("skipped") or preview.get("conflicts") else "success",
                    "variant": "tonal",
                    "class": "mt-4",
                    "text": (
                        "跳过明细：" + "；".join(
                            str(x) for x in (list(preview.get("skipped") or []) + list(preview.get("conflicts") or []))[:30]
                        ) if preview.get("skipped") or preview.get("conflicts") else "没有跳过项。"
                    ),
                },
            },
        ]

    def stop_service(self) -> None:
        return None

    # ---------------- API ----------------

    def api_preview(self, payload: Optional[dict] = Body(default=None)) -> JSONResponse:
        """按当前配置生成改名清单，默认全选所有待修改项。"""
        try:
            plan = self._build_plan(self._season, self._start_episode)
        except (ValueError, OSError) as error:
            logger.warning(f"批量改名预览失败：{error}")
            return self._fail(400, str(error))
        self.save_data(PREVIEW_KEY, plan)
        self.save_data(SELECT_KEY, {
            "ids": [
                str(index) for index, item in enumerate(plan["items"])
                if item.get("status") == "ready"
            ]
        })
        return JSONResponse(content={
            "success": True,
            "message": f"预览完成，待修改 {plan['ready_count']} 个文件",
            "ready_count": plan["ready_count"],
            "items": plan["items"],
            "skipped": plan["skipped"],
            "conflicts": plan["conflicts"],
        })

    def api_select(self, payload: dict = Body(...)) -> JSONResponse:
        """切换单个文件的选中状态，或全选/清空。"""
        payload = payload or {}
        preview = self.get_data(PREVIEW_KEY)
        if not isinstance(preview, dict) or not preview.get("items"):
            return self._fail(409, "请先点击「预览改名」")
        selection = self.get_data(SELECT_KEY) or {}
        if not isinstance(selection, dict):
            selection = {}
        ids = set(str(value) for value in selection.get("ids") or [])
        action = str(payload.get("action") or "").strip()
        if action == "all":
            ids = {
                str(index) for index, item in enumerate(preview["items"])
                if isinstance(item, dict) and item.get("status") == "ready"
            }
            message = "已全选待修改文件"
        elif action == "none":
            ids = set()
            message = "已清空选择"
        else:
            raw_index = payload.get("index")
            if raw_index is None:
                return self._fail(400, "缺少 index 参数")
            index = str(raw_index)
            if index not in {str(i) for i in range(len(preview["items"]))}:
                return self._fail(400, "文件序号无效")
            if index in ids:
                ids.discard(index)
                message = "已取消选择"
            else:
                ids.add(index)
                message = "已选择"
        self.save_data(SELECT_KEY, {"ids": sorted(ids, key=lambda value: int(value) if value.isdigit() else 0)})
        return JSONResponse(content={"success": True, "message": message, "selected": len(ids)})

    def api_apply(self, payload: Optional[dict] = Body(default=None)) -> JSONResponse:
        """按选中的文件执行改名，任一步失败回滚。"""
        preview = self.get_data(PREVIEW_KEY)
        if not isinstance(preview, dict) or not preview.get("items"):
            return self._fail(409, "请先点击「预览改名」")
        selection = self.get_data(SELECT_KEY) or {}
        if not isinstance(selection, dict):
            selection = {}
        selected_ids = set(str(value) for value in selection.get("ids") or [])
        if not selected_ids:
            return self._fail(409, "请至少选择一个文件")

        # 重新扫描，避免预览后目录发生变化
        try:
            fresh = self._build_plan(self._season, self._start_episode)
        except (ValueError, OSError) as error:
            return self._fail(400, f"重新扫描失败：{error}")

        prepared: List[Tuple[Path, Path, dict]] = []
        seen: set = set()
        errors: List[str] = []
        for index, item in enumerate(fresh["items"]):
            if str(index) not in selected_ids:
                continue
            if item.get("status") != "ready":
                errors.append(f"文件已不可修改：{item.get('old_name')}")
                continue
            source = Path(item["src"])
            target = Path(item["dst"])
            if not source.is_file():
                errors.append(f"源文件已不存在：{source.name}")
                continue
            if target.exists():
                errors.append(f"目标文件已存在：{target.name}")
                continue
            if str(target) in seen:
                errors.append(f"目标重名：{target.name}")
                continue
            seen.add(str(target))
            prepared.append((source, target, item))
        if errors:
            return self._fail(409, "；".join(errors[:5]))
        if not prepared:
            return self._fail(409, "没有可修改的文件")

        done: List[dict] = []
        for source, target, item in prepared:
            try:
                source.rename(target)
                done.append(item)
            except OSError as error:
                for rollback in reversed(done):
                    try:
                        Path(rollback["dst"]).rename(Path(rollback["src"]))
                    except OSError as rollback_error:
                        logger.error(f"批量改名回滚失败：{rollback_error}")
                logger.error(f"批量改名失败：{error}")
                return self._fail(500, f"改名失败，已回滚：{error}")

        if done:
            self.save_data(
                APPLY_KEY,
                {"applied_at": time.strftime("%Y-%m-%d %H:%M:%S"), "items": done},
            )
        self.del_data(PREVIEW_KEY)
        self.del_data(SELECT_KEY)
        message = f"改名完成，共处理 {len(done)} 个文件"
        logger.info(f"批量改名完成：{len(done)} 个文件")
        return JSONResponse(content={"success": True, "message": message, "renamed": len(done)})

    def api_undo(self, payload: Optional[dict] = Body(default=None)) -> JSONResponse:
        """把最近一次改名的文件恢复为原名。"""
        record = self.get_data(APPLY_KEY)
        if not isinstance(record, dict) or not record.get("items"):
            return self._fail(409, "没有可恢复的改名记录")

        prepared: List[Tuple[Path, Path]] = []
        errors: List[str] = []
        for item in record["items"]:
            if not isinstance(item, dict):
                continue
            try:
                source = Path(item["src"])
                target = Path(item["dst"])
            except (KeyError, TypeError):
                continue
            if not target.is_file():
                errors.append(f"改名后的文件不存在：{target.name}")
                continue
            if source.exists():
                errors.append(f"原文件名已被占用：{source.name}")
                continue
            prepared.append((target, source))
        if errors:
            return self._fail(409, "；".join(errors[:5]))

        restored = 0
        for target, source in prepared:
            try:
                target.rename(source)
                restored += 1
            except OSError as error:
                logger.error(f"恢复改名失败：{error}")
                return self._fail(500, f"恢复失败：{error}")
        self.del_data(APPLY_KEY)
        message = f"已恢复 {restored} 个文件名"
        logger.info(f"批量改名回滚完成：{restored} 个文件")
        return JSONResponse(content={"success": True, "message": message, "restored": restored})

    # ---------------- 核心逻辑 ----------------

    def _build_plan(self, season: int, start: int) -> Dict[str, Any]:
        """扫描目录并生成改名清单。"""
        source = self._resolve_source()
        files, ignored = self._collect_files(source)
        if not files:
            raise ValueError("没有找到需要处理的文件，请检查目录和扩展名设置")

        parsed: List[Tuple[Path, str, int, int]] = []
        for path in files:
            old_episode, old_season = self._parse_episode(path.stem)
            if old_episode is None:
                ignored.append(f"{path.name}：未识别到集数")
                continue
            title = self._parse_title(path.stem)
            if not title:
                ignored.append(f"{path.name}：未识别到标题")
                continue
            parsed.append((path, title, old_episode, old_season))
        if not parsed:
            raise ValueError("文件名中没有识别到 SxxExx 或「第xx集」")

        pending = [entry for entry in parsed if entry[3] != season]
        old_eps = sorted({entry[2] for entry in pending})
        episode_map = {old: start + index for index, old in enumerate(old_eps)}

        season_str = str(season).zfill(2)
        items: List[dict] = []
        conflicts: List[str] = []
        target_names: Dict[str, str] = {}
        for path, title, old_episode, old_season in parsed:
            src = path.resolve()
            if old_season == season:
                new_episode = old_episode
                status = "exist"
                reason = "已是目标季号，不改动"
            else:
                new_episode = episode_map.get(old_episode, old_episode)
                status = "ready" if old_episode in episode_map else "exist"
                reason = "" if status == "ready" else "无需改动"

            stem = self._safe_stem(
                f"{title} - S{season_str}E{str(new_episode).zfill(2)} - 第 {new_episode} 集"
            )
            dst = src.with_name(f"{stem}{src.suffix}")
            record = {
                "src": str(src), "dst": str(dst),
                "old_name": src.name, "new_name": dst.name,
                "title": title,
                "old_episode": old_episode, "old_season": old_season,
                "new_episode": new_episode,
                "status": status, "reason": reason,
            }
            target_key = str(dst)
            if status == "ready":
                if target_key in target_names:
                    record["status"] = "conflict"
                    record["reason"] = f"与 {target_names[target_key]} 目标重名"
                    conflicts.append(f"{src.name}：{record['reason']}")
                elif dst.exists():
                    record["status"] = "conflict"
                    record["reason"] = "目标文件已存在，拒绝覆盖"
                    conflicts.append(f"{src.name}：目标 {dst.name} 已存在")
                else:
                    target_names[target_key] = src.name
            items.append(record)

        items.sort(key=lambda item: (item["old_episode"], item["old_name"]))
        return {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source": str(source),
            "config": self._current_config(),
            "season": season,
            "start_episode": start,
            "items": items,
            "total_count": len(items),
            "ready_count": sum(1 for item in items if item["status"] == "ready"),
            "skipped": ignored,
            "conflicts": conflicts,
        }

    def _resolve_source(self) -> Path:
        if not self._source_dir:
            raise ValueError("请先在插件配置中填写剧集目录")
        source = Path(self._source_dir).expanduser()
        if not source.is_absolute():
            source = Path.cwd() / source
        source = source.resolve()
        if source == Path(source.anchor):
            raise ValueError("出于安全考虑，不能扫描磁盘根目录")
        if not source.exists():
            raise ValueError(f"目录不存在：{source}")
        return source

    def _collect_files(self, source: Path) -> Tuple[List[Path], List[str]]:
        extensions = set()
        for ext in self._extensions.split(","):
            ext = ext.strip().lower()
            if ext:
                extensions.add(ext if ext.startswith(".") else f".{ext}")
        if source.is_file():
            candidates = [source]
        else:
            candidates = [path for path in source.glob("*") if path.is_file()]
        files: List[Path] = []
        ignored: List[str] = []
        for path in sorted(candidates, key=lambda item: str(item).lower()):
            if path.name.startswith("."):
                ignored.append(f"{path.name}：隐藏文件")
                continue
            if extensions and path.suffix.lower() not in extensions:
                ignored.append(f"{path.name}：扩展名不在处理范围")
                continue
            files.append(path)
        return files, ignored

    @staticmethod
    def _parse_episode(name: str) -> Tuple[Optional[int], Optional[int]]:
        match = re.search(r"(?i)\bS\s*(\d{1,3})\s*E\s*(\d{1,4})\b", name)
        if match:
            return int(match.group(2)), int(match.group(1))
        match = re.search(r"第\s*(\d{1,4})\s*集", name)
        if match:
            return int(match.group(1)), None
        return None, None

    @staticmethod
    def _parse_title(name: str) -> str:
        title = re.sub(r"(?i)\s*-?\s*S\s*\d{1,3}\s*E\s*\d{1,4}\b.*$", "", name)
        title = re.sub(r"\s*-?\s*第\s*\d{1,4}\s*集\s*$", "", title)
        return title.strip(" -_.·")

    @staticmethod
    def _safe_stem(value: str) -> str:
        return re.sub(r"[\\/\x00-\x1f]", "_", value).strip().strip(".")

    @staticmethod
    def _as_int(value: Any, default: int, minimum: int, maximum: int) -> int:
        try:
            return min(max(int(value), minimum), maximum)
        except (TypeError, ValueError):
            return default

    def _current_config(self) -> Dict[str, Any]:
        return {
            "enabled": self._enabled,
            "source_dir": self._source_dir,
            "extensions": self._extensions,
            "season": self._season,
            "start_episode": self._start_episode,
        }

    @staticmethod
    def _field(component: str, model: str, label: str, md: Optional[int] = None, **props: Any) -> dict:
        column: Dict[str, Any] = {"cols": 12}
        if md:
            column["md"] = md
        return {
            "component": "VCol",
            "props": column,
            "content": [{"component": component, "props": {"model": model, "label": label, **props}}],
        }

    def _action_button(self, text: str, icon: str, path: str, color: str,
                       disabled: bool = False, params: Optional[dict] = None) -> dict:
        return {
            "component": "VBtn",
            "props": {
                "class": "ma-1",
                "variant": "tonal",
                "color": color,
                "prepend-icon": icon,
                "disabled": disabled,
            },
            "text": text,
            "events": {
                "click": {
                    "api": f"plugin/{self.__class__.__name__}{path}",
                    "method": "post",
                    "params": params or {},
                }
            },
        }

    @staticmethod
    def _select_button(index: str, picked: bool) -> dict:
        """详情页每行的选择按钮，静态 params 回传 index。"""
        return {
            "component": "VBtn",
            "props": {
                "size": "small",
                "variant": "tonal",
                "color": "success" if picked else "primary",
                "prepend-icon": "mdi-check" if picked else "mdi-plus",
            },
            "text": "已选" if picked else "选择",
            "events": {
                "click": {
                    "api": "plugin/BatchRename/select",
                    "method": "post",
                    "params": {"index": index},
                }
            },
        }

    @staticmethod
    def _fail(status: int, message: str) -> JSONResponse:
        return JSONResponse(status_code=status, content={"success": False, "message": message})
