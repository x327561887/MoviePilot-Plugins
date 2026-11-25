# -*- coding: utf-8 -*-
"""MoviePilot V2 批量改名插件（Vue 联邦模块界面）。

配置页：剧集目录（默认 /mdeia）+ 处理扩展名（默认 MP4, MKV, SRT, ASS）。
详情页：目标季号 SXX、起始集号（默认 01）两个输入框；点「预览改名」列出文件；
勾选要处理的文件后执行批量改名；可一键恢复上次改名。

改名规则：保留原标题，季号统一替换为目标季号；所有识别到集数的文件按原集数从小到大
依次改为起始集起的连续集号，「第 XX 集」自动跟随新集号。已是目标季号的文件同样参与重新编号。

示例（目标季号 1、起始集号 1）：
    Re：从零开始的异世界生活 - S04E06 - 第 6 集.mkv
    -> Re：从零开始的异世界生活 - S01E01 - 第 1 集.mkv

不覆盖已有文件，执行失败自动回滚。
"""
from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fastapi import Body
from app.plugins import _PluginBase
from app.log import logger


DEFAULT_EXTENSIONS = "MP4, MKV, SRT, ASS"
DEFAULT_SOURCE_DIR = "/mdeia"
APPLY_KEY = "batch_rename_last_apply"


class BatchRename(_PluginBase):
    """按目标季号与起始集批量重排剧集编号的插件。"""

    plugin_name = "批量改名"
    plugin_desc = "设置目录后预览文件、勾选批量改名：季号统一替换，集号按起始集递增，中文集数自动同步。"
    plugin_icon = "https://raw.githubusercontent.com/x327561887/MoviePilot-Plugins/main/plugins.v2/batchrename/icon.png"
    plugin_version = "1.2.1"
    plugin_author = "x327561887"
    author_url = "https://github.com/x327561887"
    plugin_config_prefix = "batchrename_"
    plugin_order = 50
    auth_level = 1

    def __init__(self):
        super().__init__()
        config = self._default_config()
        self._enabled = True
        self._source_dir = config["source_dir"]
        self._extensions = config["extensions"]
        self._season = config["season"]
        self._start_episode = config["start_episode"]

    # ------------------------------------------------------------------
    # 生命周期
    # ------------------------------------------------------------------
    @staticmethod
    def _default_config() -> Dict[str, Any]:
        return {
            "enabled": True,
            "source_dir": DEFAULT_SOURCE_DIR,
            "extensions": DEFAULT_EXTENSIONS,
            "season": 1,
            "start_episode": 1,
        }

    def _current_config(self) -> Dict[str, Any]:
        return {
            "enabled": bool(self._enabled),
            "source_dir": self._source_dir,
            "extensions": self._extensions,
            "season": self._season,
            "start_episode": self._start_episode,
        }

    def init_plugin(self, config: dict = None):
        config = config or {}
        self._enabled = True
        self._source_dir = str(config.get("source_dir") or DEFAULT_SOURCE_DIR).strip() or DEFAULT_SOURCE_DIR
        self._extensions = str(config.get("extensions") or DEFAULT_EXTENSIONS).strip() or DEFAULT_EXTENSIONS
        self._season = self._as_int(config.get("season"), 1, 0, 999)
        self._start_episode = self._as_int(config.get("start_episode"), 1, 1, 99999)

    def get_state(self) -> bool:
        return True

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        return []

    @staticmethod
    def get_render_mode() -> Tuple[str, str]:
        """Vue 联邦模块模式：配置页由 ./Config、详情页由 ./Page 渲染。"""
        return "vue", "dist/assets"

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        return [], self._default_config()

    def get_page(self) -> List[dict]:
        return []

    def get_api(self) -> List[Dict[str, Any]]:
        return [
            {
                "path": "/config",
                "endpoint": self.config_status,
                "methods": ["GET"],
                "auth": "",
                "summary": "读取批量改名配置",
            },
            {
                "path": "/config",
                "endpoint": self.save_config,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "保存批量改名配置",
            },
            {
                "path": "/preview",
                "endpoint": self.api_preview,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "预览改名",
                "description": "按传入的季号与起始集扫描目录，生成改名清单，不修改文件。",
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
            },
        ]

    @staticmethod
    def stop_service():
        return None

    # ------------------------------------------------------------------
    # 配置接口
    # ------------------------------------------------------------------
    def config_status(self) -> Dict[str, Any]:
        return self._ok(self._current_config())

    def save_config(self, payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
        config = self._default_config()
        config.update(payload or {})
        config["enabled"] = True
        try:
            self.update_config(config)
        except Exception as error:  # pragma: no cover - 宿主未提供 update_config
            logger.warning(f"批量改名保存配置失败：{error}")
            return self._fail(500, f"保存配置失败：{error}")
        self.init_plugin(config)
        return self._ok(self._current_config(), "配置已保存")

    # ------------------------------------------------------------------
    # 业务接口
    # ------------------------------------------------------------------
    def api_preview(self, payload: Optional[dict] = Body(default=None)) -> Dict[str, Any]:
        """按传入参数生成改名清单，不改动文件。"""
        payload = payload or {}
        season = self._as_int(payload.get("season"), self._season, 0, 999)
        start = self._as_int(payload.get("start"), self._start_episode, 1, 99999)
        try:
            plan = self._build_plan(season, start)
        except (ValueError, OSError) as error:
            logger.warning(f"批量改名预览失败：{error}")
            return self._fail(400, str(error))
        return self._ok({
            "items": plan["items"],
            "total_count": plan["total_count"],
            "ready_count": plan["ready_count"],
            "exist_count": sum(1 for i in plan["items"] if i["status"] == "exist"),
            "skipped": plan["skipped"],
            "conflicts": plan["conflicts"],
            "generated_at": plan["generated_at"],
            "source": plan["source"],
        })

    def api_apply(self, payload: Optional[dict] = Body(default=None)) -> Dict[str, Any]:
        """按选中的原文件名执行改名，任一步失败回滚。"""
        payload = payload or {}
        season = self._as_int(payload.get("season"), self._season, 0, 999)
        start = self._as_int(payload.get("start"), self._start_episode, 1, 99999)
        raw_names = payload.get("names") or []
        if isinstance(raw_names, (str, int)):
            raw_names = [raw_names]
        wanted = set(str(value) for value in raw_names)
        if not wanted:
            return self._fail(400, "请至少勾选一个文件")

        try:
            fresh = self._build_plan(season, start)
        except (ValueError, OSError) as error:
            return self._fail(400, f"重新扫描失败：{error}")

        prepared: List[Tuple[Path, Path, dict]] = []
        seen: set = set()
        errors: List[str] = []
        for item in fresh["items"]:
            if item["old_name"] not in wanted:
                continue
            if item["status"] != "ready":
                errors.append(f"文件已不可修改：{item['old_name']}")
                continue
            source = Path(item["src"])
            target = Path(item["dst"])
            if source == target:
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
        message = f"改名完成，共处理 {len(done)} 个文件"
        logger.info(f"批量改名完成：{len(done)} 个文件")
        return self._ok({"renamed": len(done)}, message)

    def api_undo(self, payload: Optional[dict] = Body(default=None)) -> Dict[str, Any]:
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
            if source == target:
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
        return self._ok({"restored": restored}, message)

    # ------------------------------------------------------------------
    # 核心逻辑
    # ------------------------------------------------------------------
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

        # 所有识别到集数的文件（含已是目标季号的）统一按原集数从小到大重新编号
        old_eps = sorted({entry[2] for entry in parsed})
        episode_map = {old: start + index for index, old in enumerate(old_eps)}

        season_str = str(season).zfill(2)
        items: List[dict] = []
        conflicts: List[str] = []
        target_names: Dict[str, str] = {}
        for path, title, old_episode, old_season in parsed:
            src = path.resolve()
            new_episode = episode_map.get(old_episode, old_episode)
            stem = self._safe_stem(
                f"{title} - S{season_str}E{str(new_episode).zfill(2)} - 第 {new_episode} 集"
            )
            dst = src.with_name(f"{stem}{src.suffix}")
            # 只有改名后文件名完全不变的文件才标为「已存在」且不可勾选；
            # 其余文件（含已是目标季号但集号需重排的）均可勾选修改。
            if src == dst:
                status = "exist"
                reason = "已是目标文件名，无需改动"
            else:
                status = "ready"
                reason = ""
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

    @staticmethod
    def _ok(data: Any, message: str = "ok") -> Dict[str, Any]:
        return {"success": True, "message": message, "data": data}

    @staticmethod
    def _fail(status: int, message: str) -> Dict[str, Any]:
        logger.warning(f"批量改名失败：{message}")
        return {"success": False, "status": status, "message": message}
