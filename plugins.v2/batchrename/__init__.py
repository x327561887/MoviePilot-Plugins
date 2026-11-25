# -*- coding: utf-8 -*-
"""MoviePilot 批量改名插件：固定统一名称，按原集数排序后从起始集连续重编号。

示例：
    Re：从零开始的异世界生活 - S04E01 - 第 01 集.mkv
    -> Re：从零开始的异世界生活 - S01E67 - 第 67 集.mkv
    Re：从零开始的异世界生活 - S04E02 - 第 02 集.mkv
    -> Re：从零开始的异世界生活 - S01E68 - 第 68 集.mkv

同一原集数的视频、字幕等文件会一起改成同一个新集号；插件不覆盖已存在的目标文件，
执行结果会保留一份映射，可用「恢复上次改名」回滚。
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


DEFAULT_TEMPLATE = "{title} - S{season}E{episode} - 第 {episode_cn} 集"
DEFAULT_EXTENSIONS = ".mp4,.mkv,.avi,.mov,.ts,.m2ts,.webm,.strm,.srt,.ass,.ssa,.sub"
PREVIEW_KEY = "batch_rename_preview"
APPLY_KEY = "batch_rename_last_apply"

STATUS_LABELS = {
    "ready": "待改名",
    "unchanged": "无需改动",
    "conflict": "跳过（冲突）",
}


class BatchRename(_PluginBase):
    """按固定模板批量重排剧集编号的插件。"""

    plugin_name = "批量改名（顺序重编号）"
    plugin_desc = "固定统一名称与季号，按原集数排序后从指定起始集连续递增，支持预览与回滚。"
    plugin_icon = "Moviepilot_A.png"
    plugin_version = "1.0.0"
    plugin_author = "x327561887"
    author_url = "https://github.com/x327561887"
    plugin_config_prefix = "batchrename_"
    plugin_order = 50
    auth_level = 1

    _enabled = False
    _source_dir = ""
    _recursive = True
    _title = ""
    _template = DEFAULT_TEMPLATE
    _target_season = 1
    _start_episode = 1
    _season_digits = 2
    _episode_digits = 2
    _cn_digits = 2
    _extensions = DEFAULT_EXTENSIONS

    def init_plugin(self, config: Optional[Dict[str, Any]] = None) -> None:
        """读取配置并重建本次运行状态，允许重复调用。"""
        if config is None:
            try:
                config = self.get_config() or {}
            except Exception:
                config = {}
        config = config or {}
        self._enabled = bool(config.get("enabled"))
        self._source_dir = str(config.get("source_dir") or "").strip()
        self._recursive = bool(config.get("recursive", True))
        self._title = str(config.get("title") or "").strip()
        self._template = str(config.get("template") or DEFAULT_TEMPLATE).strip() or DEFAULT_TEMPLATE
        self._target_season = self._as_int(config.get("season"), 1, 0, 999)
        self._start_episode = self._as_int(config.get("start_episode"), 1, 0, 99999)
        self._season_digits = self._as_int(config.get("season_digits"), 2, 1, 6)
        self._episode_digits = self._as_int(config.get("episode_digits"), 2, 1, 6)
        self._cn_digits = self._as_int(config.get("cn_digits"), 2, 1, 6)
        self._extensions = str(config.get("extensions") or DEFAULT_EXTENSIONS).strip()

    def get_state(self) -> bool:
        """返回插件启用状态。"""
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        """当前插件不注册远程命令。"""
        return []

    def get_api(self) -> List[Dict[str, Any]]:
        """注册预览、执行与回滚接口。"""
        return [
            {
                "path": "/preview",
                "endpoint": self.api_preview,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "预览批量改名",
                "description": "扫描目录并生成改名清单，不修改文件。",
            },
            {
                "path": "/apply",
                "endpoint": self.api_apply,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "执行批量改名",
                "description": "按最近一次预览清单改名，失败时自动回滚。",
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
        """返回配置页面和默认配置。"""
        fields = [
            self._field("VSwitch", "enabled", "启用插件", md=3),
            self._field("VSwitch", "recursive", "递归扫描子目录", md=3),
            self._field(
                "VTextField", "source_dir", "待扫描目录（容器内的绝对路径）", md=6,
                placeholder="/media/动画/Re：从零开始的异世界生活",
            ),
            self._field(
                "VTextField", "title", "固定标题", md=6,
                placeholder="Re：从零开始的异世界生活",
            ),
            self._field(
                "VTextField", "template", "命名模板", md=6,
                placeholder=DEFAULT_TEMPLATE,
            ),
            self._field("VTextField", "season", "目标季号（SXX）", md=2, type="number"),
            self._field("VTextField", "start_episode", "起始集号", md=2, type="number"),
            self._field("VTextField", "season_digits", "S 位数", md=2, type="number"),
            self._field("VTextField", "episode_digits", "E 位数", md=2, type="number"),
            self._field("VTextField", "cn_digits", "第XX集位数", md=2, type="number"),
            self._field("VTextField", "extensions", "处理扩展名（逗号分隔）", md=12),
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
                                "规则：按原集数从小到大排序，季号固定，新集号从「起始集号」连续递增；"
                                "同一原集数的视频与字幕共用同一个新集号。"
                                "模板可用 {title} / {season} / {episode} / {episode_cn} / {old_episode}。"
                                "填写配置并保存后，到插件详情页点「预览改名」→「执行改名」。"
                            ),
                        },
                    },
                    {"component": "VRow", "content": fields},
                ],
            }
        ], self._current_config()

    def get_page(self) -> List[dict]:
        """返回改名清单与操作按钮。"""
        preview = self.get_data(PREVIEW_KEY) or {}
        applied = self.get_data(APPLY_KEY) or {}
        if not isinstance(preview, dict):
            preview = {}
        if not isinstance(applied, dict):
            applied = {}
        items = preview.get("items") or []
        rows = [
            {
                "old_name": str(item.get("old_name") or ""),
                "new_name": str(item.get("new_name") or ""),
                "old_episode": str(item.get("old_episode") or ""),
                "new_episode": str(item.get("new_episode") or ""),
                "status": STATUS_LABELS.get(item.get("status"), str(item.get("status") or "")),
                "reason": str(item.get("reason") or ""),
            }
            for item in items
            if isinstance(item, dict)
        ]
        skipped = preview.get("skipped") or []
        conflicts = preview.get("conflicts") or []
        summary = (
            f"预览时间：{preview.get('generated_at') or '无'} | "
            f"待改名：{preview.get('ready_count', 0)} | "
            f"跳过：{len(skipped) + len(conflicts)} | "
            f"最近执行：{applied.get('applied_at') or '无'}"
        )
        headers = [
            {"title": "状态", "key": "status"},
            {"title": "原文件名", "key": "old_name"},
            {"title": "新文件名", "key": "new_name"},
            {"title": "原集", "key": "old_episode"},
            {"title": "新集", "key": "new_episode"},
            {"title": "说明", "key": "reason"},
        ]
        return [
            {"component": "VAlert", "props": {"type": "info", "variant": "tonal", "text": summary}},
            {
                "component": "div",
                "props": {"class": "d-flex flex-wrap ga-2 my-4"},
                "content": [
                    self._action_button("预览改名", "mdi-file-search-outline", "/preview", "primary"),
                    self._action_button(
                        "执行改名", "mdi-pencil-box-multiple-outline", "/apply", "warning",
                        disabled=not rows,
                    ),
                    self._action_button(
                        "恢复上次改名", "mdi-undo", "/undo", "secondary",
                        disabled=not applied.get("items"),
                    ),
                ],
            },
            {
                "component": "VDataTable",
                "props": {
                    "density": "compact",
                    "headers": headers,
                    "items": rows,
                    "items-per-page": 50,
                },
            },
            {
                "component": "VAlert",
                "props": {
                    "type": "warning" if skipped or conflicts else "success",
                    "variant": "tonal",
                    "class": "mt-4",
                    "text": (
                        "跳过明细：" + "；".join(str(x) for x in (list(skipped) + list(conflicts))[:30])
                        if skipped or conflicts else "没有跳过项。"
                    ),
                },
            },
        ]

    def stop_service(self) -> None:
        """插件没有后台任务，无需释放资源。"""
        return None

    def api_preview(self, payload: Optional[dict] = Body(default=None)) -> JSONResponse:
        """生成改名清单并持久化，不改动任何文件。"""
        try:
            plan = self._build_plan()
        except (ValueError, OSError) as error:
            logger.warning(f"批量改名预览失败：{error}")
            return self._fail(400, str(error))
        self.save_data(PREVIEW_KEY, plan)
        return JSONResponse(
            content={
                "success": True,
                "message": f"预览完成，待改名 {plan['ready_count']} 个文件",
                "items": plan["items"],
                "skipped": plan["skipped"],
                "conflicts": plan["conflicts"],
            }
        )

    def api_apply(self, payload: Optional[dict] = Body(default=None)) -> JSONResponse:
        """按预览清单改名；任一步失败时回滚已改名的文件。"""
        plan = self.get_data(PREVIEW_KEY)
        if not isinstance(plan, dict) or not plan.get("items"):
            return self._fail(409, "请先保存配置并点击「预览改名」")

        prepared: List[Tuple[Path, Path, dict]] = []
        seen: set = set()
        errors: List[str] = []
        for item in plan["items"]:
            if not isinstance(item, dict) or item.get("status") != "ready":
                continue
            try:
                source = Path(item["src"])
                target = Path(item["dst"])
            except (KeyError, TypeError):
                continue
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

    def _build_plan(self) -> Dict[str, Any]:
        """扫描目录并计算原名到新名的映射。"""
        source = self._resolve_source()
        files, ignored = self._collect_files(source)
        if not files:
            raise ValueError("没有找到需要处理的文件，请检查目录和扩展名设置")

        groups: Dict[int, List[Tuple[Path, Optional[int]]]] = {}
        for path in files:
            old_episode, old_season = self._parse_episode(path.stem)
            if old_episode is None:
                ignored.append(f"{path.name}：未识别到集数")
                continue
            groups.setdefault(old_episode, []).append((path, old_season))
        if not groups:
            raise ValueError("文件名中没有识别到 SxxExx、第xx集 或 Exx")

        items: List[dict] = []
        conflicts: List[str] = []
        target_names: Dict[str, str] = {}
        for index, old_episode in enumerate(sorted(groups)):
            new_episode = self._start_episode + index
            season = str(self._target_season).zfill(self._season_digits)
            episode = str(new_episode).zfill(self._episode_digits)
            episode_cn = str(new_episode).zfill(self._cn_digits)
            try:
                stem = self._template.format(
                    title=self._title,
                    season=season,
                    episode=episode,
                    episode_cn=episode_cn,
                    old_episode=str(old_episode).zfill(self._episode_digits),
                )
            except (KeyError, IndexError, ValueError) as error:
                raise ValueError(f"命名模板无效：{error}") from error
            stem = self._safe_stem(stem)
            if not stem:
                raise ValueError("命名模板生成了空文件名")

            for path, old_season in groups[old_episode]:
                src = path.resolve()
                dst = src.with_name(f"{stem}{src.suffix}")
                record = {
                    "src": str(src),
                    "dst": str(dst),
                    "old_name": src.name,
                    "new_name": dst.name,
                    "old_episode": old_episode,
                    "old_season": old_season,
                    "new_episode": new_episode,
                    "status": "ready",
                    "reason": "",
                }
                target_key = str(dst)
                if target_key in target_names:
                    record["status"] = "conflict"
                    record["reason"] = f"与 {target_names[target_key]} 目标重名"
                    conflicts.append(f"{src.name}：{record['reason']}")
                elif src == dst:
                    record["status"] = "unchanged"
                    record["reason"] = "文件名已符合规则"
                    target_names[target_key] = src.name
                elif dst.exists():
                    record["status"] = "conflict"
                    record["reason"] = "目标文件已存在，拒绝覆盖"
                    conflicts.append(f"{src.name}：目标 {dst.name} 已存在")
                else:
                    target_names[target_key] = src.name
                items.append(record)

        return {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source": str(source),
            "config": self._current_config(),
            "items": items,
            "ready_count": sum(1 for item in items if item["status"] == "ready"),
            "skipped": ignored,
            "conflicts": conflicts,
        }

    def _resolve_source(self) -> Path:
        """校验并返回待扫描路径，拒绝磁盘根目录。"""
        if not self._source_dir:
            raise ValueError("请先在插件配置中填写待扫描目录")
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
        """按扩展名筛选待处理文件，并返回忽略原因。"""
        extensions = set()
        for ext in self._extensions.split(","):
            ext = ext.strip().lower()
            if not ext:
                continue
            extensions.add(ext if ext.startswith(".") else f".{ext}")

        if source.is_file():
            candidates = [source]
        else:
            pattern = "**/*" if self._recursive else "*"
            candidates = [path for path in source.glob(pattern) if path.is_file()]

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
        """从文件名中提取（集号，季号），识别失败返回 (None, None)。"""
        match = re.search(r"(?i)\bS\s*(\d{1,3})\s*E\s*(\d{1,4})\b", name)
        if match:
            return int(match.group(2)), int(match.group(1))
        match = re.search(r"第\s*(\d{1,4})\s*集", name)
        if match:
            return int(match.group(1)), None
        match = re.search(r"(?i)\bEP?\s*(\d{1,4})\b", name)
        if match:
            return int(match.group(1)), None
        return None, None

    @staticmethod
    def _safe_stem(value: str) -> str:
        """清理模板结果，避免生成非法文件名。"""
        return re.sub(r"[\\/\x00-\x1f]", "_", value).strip().strip(".")

    @staticmethod
    def _as_int(value: Any, default: int, minimum: int, maximum: int) -> int:
        """把配置值转换为限定范围内的整数。"""
        try:
            return min(max(int(value), minimum), maximum)
        except (TypeError, ValueError):
            return default

    def _current_config(self) -> Dict[str, Any]:
        """返回当前配置快照。"""
        return {
            "enabled": self._enabled,
            "source_dir": self._source_dir,
            "recursive": self._recursive,
            "title": self._title,
            "template": self._template,
            "season": self._target_season,
            "start_episode": self._start_episode,
            "season_digits": self._season_digits,
            "episode_digits": self._episode_digits,
            "cn_digits": self._cn_digits,
            "extensions": self._extensions,
        }

    @staticmethod
    def _field(component: str, model: str, label: str, md: Optional[int] = None, **props: Any) -> dict:
        """构造一个带标签的 Vuetify 表单列。"""
        column: Dict[str, Any] = {"cols": 12}
        if md:
            column["md"] = md
        return {
            "component": "VCol",
            "props": column,
            "content": [{"component": component, "props": {"model": model, "label": label, **props}}],
        }

    def _action_button(self, text: str, icon: str, path: str, color: str, disabled: bool = False) -> dict:
        """构造一个调用插件 API 的详情页按钮。"""
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
                }
            },
        }

    @staticmethod
    def _fail(status: int, message: str) -> JSONResponse:
        """返回带错误说明的响应。"""
        return JSONResponse(status_code=status, content={"success": False, "message": message})
