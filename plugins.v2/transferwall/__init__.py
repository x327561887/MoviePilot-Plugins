"""MoviePilot V2 插件：整理海报墙。

在主界面「整理」分组增加全页入口，以海报墙形式展示整理记录，
并支持删除整理记录、源文件和媒体库文件。

删除逻辑参考 MoviePilot V2 原生接口 /api/v1/history/transfer：
- 媒体库文件与源文件通过 StorageChain.delete_media_file 删除
- 源文件删除后同步清理下载记录中的文件项并发送 DownloadFileDeleted 事件
- 最后删除整理记录本身
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

from fastapi import Body, Depends, HTTPException
from app.plugins import _PluginBase

# 权限与数据库依赖：宿主可用时直接使用原生依赖，不可用时不降级为"允许"，而是返回 503
try:
    from app.db import get_db as _moviepilot_get_db
    DB_DEPENDENCY = Depends(_moviepilot_get_db)
except Exception:  # pragma: no cover - 仅在非 MoviePilot 环境导入时触发
    def _db_unavailable():
        raise HTTPException(status_code=503, detail="MoviePilot 数据库依赖未就绪")

    DB_DEPENDENCY = Depends(_db_unavailable)

try:
    from app.db.user_oper import get_current_active_manage_user as _manage_user
    MANAGE_DEPENDENCY = Depends(_manage_user)
except Exception:  # pragma: no cover
    def _auth_unavailable():
        raise HTTPException(status_code=503, detail="MoviePilot 权限依赖未就绪")

    MANAGE_DEPENDENCY = Depends(_auth_unavailable)


CONFIRM_TOKEN = "删除"


class TransferWall(_PluginBase):
    """整理记录海报墙插件。"""

    plugin_name = "整理海报墙 TransferWall"
    plugin_desc = "TransferWall 整理海报墙：在「整理」中显示转移记录海报墙，可删除记录、源文件与媒体库文件。"
    plugin_icon = "https://raw.githubusercontent.com/x327561887/MoviePilot-Plugins/main/icons/transferwall.png"
    plugin_version = "1.0.0"
    plugin_author = "x327561887"
    author_url = "https://github.com/x327561887"
    plugin_config_prefix = "transferwall_"
    plugin_order = 35
    auth_level = 1

    def __init__(self):
        super().__init__()
        config = self._default_config()
        self._enabled = False
        self._nav_title = config["nav_title"]
        self._nav_icon = config["nav_icon"]
        self._max_records = config["max_records"]
        self._max_batch = config["max_batch"]
        self._default_delete_record = config["default_delete_record"]
        self._default_delete_src = config["default_delete_src"]
        self._default_delete_dest = config["default_delete_dest"]

    # ------------------------------------------------------------------
    # 插件生命周期
    # ------------------------------------------------------------------
    @staticmethod
    def _default_config() -> Dict[str, Any]:
        return {
            "enabled": False,
            "nav_title": "整理海报墙",
            "nav_icon": "mdi-view-gallery",
            "max_records": 1200,
            "max_batch": 100,
            "default_delete_record": True,
            "default_delete_src": False,
            "default_delete_dest": False,
        }

    def _current_config(self) -> Dict[str, Any]:
        return {
            "enabled": bool(self._enabled),
            "nav_title": self._nav_title,
            "nav_icon": self._nav_icon,
            "max_records": self._max_records,
            "max_batch": self._max_batch,
            "default_delete_record": bool(self._default_delete_record),
            "default_delete_src": bool(self._default_delete_src),
            "default_delete_dest": bool(self._default_delete_dest),
        }

    def init_plugin(self, config: dict = None):
        defaults = self._default_config()
        config = config or {}
        self._enabled = bool(config.get("enabled", defaults["enabled"]))
        self._nav_title = str(config.get("nav_title") or defaults["nav_title"]).strip()
        self._nav_icon = str(config.get("nav_icon") or defaults["nav_icon"]).strip()

        def _positive_int(value: Any, fallback: int, upper: int) -> int:
            try:
                parsed = int(value)
            except (TypeError, ValueError):
                return fallback
            return max(1, min(upper, parsed))

        self._max_records = _positive_int(
            config.get("max_records"), defaults["max_records"], 10000
        )
        self._max_batch = _positive_int(
            config.get("max_batch"), defaults["max_batch"], 100
        )
        self._default_delete_record = bool(
            config.get("default_delete_record", defaults["default_delete_record"])
        )
        self._default_delete_src = bool(
            config.get("default_delete_src", defaults["default_delete_src"])
        )
        self._default_delete_dest = bool(
            config.get("default_delete_dest", defaults["default_delete_dest"])
        )

    def get_state(self) -> bool:
        return bool(self._enabled)

    @staticmethod
    def get_render_mode() -> Tuple[str, str]:
        return "vue", "dist/assets"

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        # Vue 模式下配置页由联邦远程组件 ./Config 渲染
        return [], self._default_config()

    def get_page(self) -> List[dict]:
        # Vue 模式下详情页由联邦远程组件 ./Page 渲染
        return []

    def get_sidebar_nav(self) -> List[Dict[str, Any]]:
        """在主界面「整理」分组下注册全页入口。"""
        if not self.get_state():
            return []
        return [
            {
                "nav_key": "main",
                "title": self._nav_title or "整理海报墙",
                "icon": self._nav_icon or "mdi-view-gallery",
                "section": "organize",
                "permission": "manage",
                "order": 35,
            }
        ]

    def get_api(self) -> List[Dict[str, Any]]:
        return [
            {
                "path": "/wall",
                "endpoint": self.wall,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "查询整理记录海报墙",
            },
            {
                "path": "/config",
                "endpoint": self.config_status,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "读取海报墙配置",
            },
            {
                "path": "/config",
                "endpoint": self.save_wall_config,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "保存海报墙配置",
            },
            {
                "path": "/delete",
                "endpoint": self.delete_histories,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "删除整理记录及关联文件",
            },
        ]

    @staticmethod
    def stop_service():
        return None

    # ------------------------------------------------------------------
    # 配置接口
    # ------------------------------------------------------------------
    def config_status(self) -> Dict[str, Any]:
        return self._current_config()

    def save_wall_config(
        self,
        payload: Dict[str, Any] = Body(...),
        user: Any = MANAGE_DEPENDENCY,
    ) -> Dict[str, Any]:
        del user  # 仅用于权限校验
        config = self._default_config()
        config.update(payload or {})
        self.update_config(config)
        self.init_plugin(config)
        return self._current_config()

    # ------------------------------------------------------------------
    # 海报墙数据
    # ------------------------------------------------------------------
    @staticmethod
    def _history_to_dict(history: Any) -> Dict[str, Any]:
        try:
            data = history.to_dict()
        except Exception:
            data = {
                column.name: getattr(history, column.name, None)
                for column in history.__table__.columns
            }
        data = dict(data or {})
        for key in ("src", "dest", "image", "title", "year", "type", "mode",
                    "seasons", "episodes", "media_source", "media_id", "category"):
            value = data.get(key)
            data[key] = str(value).strip() if value is not None else ""
        data["id"] = data.get("id")
        data["status"] = bool(data.get("status"))
        data["src_fileitem"] = data.get("src_fileitem") if isinstance(data.get("src_fileitem"), dict) else {}
        data["dest_fileitem"] = data.get("dest_fileitem") if isinstance(data.get("dest_fileitem"), dict) else {}
        data["files"] = data.get("files") if isinstance(data.get("files"), list) else []

        # 海报 URL 规范化：对齐 MoviePilot V2 官方 getHistoryPosterUrl 逻辑。
        # 相对路径（如 /xx.jpg、posters/xx.jpg）浏览器无法直接加载，需交给
        # 宿主图片代理 api/v1/system/img/0 解析补全，否则会显示灰色占位图。
        image = str(data.get("image") or "").strip()
        if image and not re.match(r"^https?://", image, re.IGNORECASE):
            data["image"] = "api/v1/system/img/0?imgurl=" + quote(image, safe="")
        return data

    @staticmethod
    def _group_key(record: Dict[str, Any]) -> str:
        source = str(record.get("media_source") or "").strip()
        media_id = str(record.get("media_id") or "").strip()
        if source and media_id and media_id != "0":
            return f"media|{source}|{media_id}"
        title = str(record.get("title") or "").strip()
        if title:
            return (
                f"title|{record.get('type') or ''}|{title}|{record.get('year') or ''}"
            )
        return f"path|{record.get('src') or record.get('dest') or record.get('id')}"

    @staticmethod
    def _file_identity(raw: Dict[str, Any], fallback: str) -> str:
        if not raw:
            return fallback
        storage = str(raw.get("storage") or "local")
        path = str(raw.get("path") or fallback)
        return f"{storage}|{path}"

    def wall(
        self,
        keyword: Optional[str] = None,
        status: Optional[str] = None,
        media_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 24,
    ) -> Dict[str, Any]:
        """按媒体聚合整理记录，返回海报墙数据。"""
        from app.db.models.transferhistory import TransferHistory

        try:
            page = max(1, int(page or 1))
        except (TypeError, ValueError):
            page = 1
        try:
            page_size = max(1, min(120, int(page_size or 24)))
        except (TypeError, ValueError):
            page_size = 24

        status_bool: Optional[bool] = None
        if status == "success":
            status_bool = True
        elif status == "fail":
            status_bool = False

        # 避免用户输入的 SQL LIKE 通配符放大查询范围
        keyword = (keyword or "").strip().replace("%", "").replace("_", "").replace("\\", "")
        keyword = keyword[:100]

        if keyword:
            rows = TransferHistory.list_by_title(
                title=keyword, page=1, count=self._max_records, status=status_bool
            )
        else:
            rows = TransferHistory.list_by_page(
                page=1, count=self._max_records, status=status_bool
            )
        rows = list(rows or [])

        if media_type in ("movie", "tv"):
            wanted = ("电影", "movie") if media_type == "movie" else ("电视剧", "tv")
            rows = [
                row for row in rows
                if str(getattr(row, "type", "") or "").lower() in wanted
            ]

        groups: Dict[str, Dict[str, Any]] = {}
        for row in rows:
            record = self._history_to_dict(row)
            key = self._group_key(record)
            group = groups.get(key)
            if group is None:
                group = {
                    "key": key,
                    "title": record.get("title") or "未识别媒体",
                    "year": record.get("year") or "",
                    "type": record.get("type") or "",
                    "poster": "",
                    "media_source": record.get("media_source") or "",
                    "media_id": record.get("media_id") or "",
                    "tmdbid": record.get("tmdbid"),
                    "records": [],
                    "record_count": 0,
                    "success_count": 0,
                    "fail_count": 0,
                    "src_count": 0,
                    "dest_count": 0,
                    "latest": "",
                    "seasons": set(),
                    "_src_paths": set(),
                    "_dest_paths": set(),
                }
                groups[key] = group

            if not group.get("poster") and record.get("image"):
                group["poster"] = record["image"]
            if not group.get("title") or group["title"] == "未识别媒体":
                if record.get("title"):
                    group["title"] = record["title"]
            group["records"].append(record)
            group["record_count"] += 1
            if record.get("status"):
                group["success_count"] += 1
            else:
                group["fail_count"] += 1
            date = str(record.get("date") or "")
            if date > str(group.get("latest") or ""):
                group["latest"] = date
            if record.get("seasons"):
                group["seasons"].add(record["seasons"])
            group["_src_paths"].add(
                self._file_identity(record.get("src_fileitem"), record.get("src") or "")
            )
            group["_dest_paths"].add(
                self._file_identity(record.get("dest_fileitem"), record.get("dest") or "")
            )

        ordered: List[Dict[str, Any]] = []
        for group in groups.values():
            group["src_count"] = len(group.pop("_src_paths"))
            group["dest_count"] = len(group.pop("_dest_paths"))
            group["seasons"] = ",".join(sorted(group.pop("seasons")))[:60]
            # 单部媒体的记录较多时只返回前 200 条，避免响应过大
            group["records_truncated"] = len(group["records"]) > 200
            group["records"] = group["records"][:200]
            ordered.append(group)

        ordered.sort(
            key=lambda item: (str(item.get("latest") or ""), item.get("record_count") or 0),
            reverse=True,
        )

        start = (page - 1) * page_size
        chunk = ordered[start:start + page_size]
        return {
            "groups": chunk,
            "page": page,
            "page_size": page_size,
            "total_groups": len(ordered),
            "total_records": len(rows),
            "truncated": len(rows) >= self._max_records,
            "config": {
                "max_batch": self._max_batch,
                "default_delete_record": bool(self._default_delete_record),
                "default_delete_src": bool(self._default_delete_src),
                "default_delete_dest": bool(self._default_delete_dest),
            },
        }

    # ------------------------------------------------------------------
    # 删除
    # ------------------------------------------------------------------
    @staticmethod
    def _build_fileitem(raw: Any):
        if not isinstance(raw, dict) or not raw.get("path"):
            return None
        try:
            from app.schemas import FileItem

            return FileItem(**raw)
        except Exception:
            return None

    def _delete_one(
        self,
        db: Any,
        history_id: int,
        delete_record: bool,
        delete_src: bool,
        delete_dest: bool,
    ) -> Dict[str, Any]:
        """删除单条整理记录及其关联文件，语义与 MoviePilot 原生接口一致。"""
        from pathlib import Path as HostPath

        from app.chain.storage import StorageChain
        from app.core.event import eventmanager
        from app.db.models.transferhistory import TransferHistory
        from app.schemas.types import EventType

        try:
            from app.db.models.downloadhistory import DownloadFiles
        except ImportError:  # 兼容未暴露 DownloadFiles 的旧版 V2
            DownloadFiles = None

        history = TransferHistory.get(db, history_id)
        result: Dict[str, Any] = {
            "id": history_id,
            "ok": False,
            "message": "",
            "deleted": {"record": False, "src": False, "dest": False},
            "paths": {},
        }
        if not history:
            result["message"] = "整理记录不存在"
            return result

        result["paths"] = {
            "src": str(history.src or ""),
            "dest": str(history.dest or ""),
        }

        if delete_dest and history.dest_fileitem:
            item = self._build_fileitem(history.dest_fileitem)
            if item:
                try:
                    StorageChain().delete_media_file(item)
                    result["deleted"]["dest"] = True
                except Exception as err:
                    result["message"] = f"删除媒体库文件失败：{err}"
                    return result

        if delete_src and history.src_fileitem:
            item = self._build_fileitem(history.src_fileitem)
            if item:
                try:
                    state = StorageChain().delete_media_file(item)
                    if not state:
                        result["message"] = f"{item.path} 删除失败"
                        return result
                    if DownloadFiles is not None:
                        DownloadFiles.delete_by_fullpath(
                            db, HostPath(str(item.path)).as_posix()
                        )
                    eventmanager.send_event(
                        EventType.DownloadFileDeleted,
                        {"src": history.src, "hash": history.download_hash},
                    )
                    result["deleted"]["src"] = True
                except Exception as err:
                    result["message"] = f"删除源文件失败：{err}"
                    return result

        if delete_record:
            try:
                TransferHistory.delete(db, history_id)
                result["deleted"]["record"] = True
            except Exception as err:
                result["message"] = f"删除整理记录失败：{err}"
                return result

        result["ok"] = True
        result["message"] = "完成"
        return result

    def delete_histories(
        self,
        payload: Dict[str, Any] = Body(...),
        user: Any = MANAGE_DEPENDENCY,
        db: Any = DB_DEPENDENCY,
    ) -> Dict[str, Any]:
        """批量删除；所有文件删除都需要前端二次确认。"""
        del user
        payload = payload or {}

        if payload.get("confirm") != CONFIRM_TOKEN:
            raise HTTPException(status_code=400, detail=f"请在确认框输入「{CONFIRM_TOKEN}」")

        delete_record = bool(payload.get("delete_record", False))
        delete_src = bool(payload.get("delete_src", False))
        delete_dest = bool(payload.get("delete_dest", False))
        if not (delete_record or delete_src or delete_dest):
            raise HTTPException(status_code=400, detail="请至少选择一项删除内容")

        raw_ids = payload.get("ids") or []
        if isinstance(raw_ids, (str, int)):
            raw_ids = [raw_ids]
        ids: List[int] = []
        for raw_id in raw_ids:
            try:
                parsed = int(raw_id)
            except (TypeError, ValueError):
                continue
            if parsed > 0 and parsed not in ids:
                ids.append(parsed)
        if not ids:
            raise HTTPException(status_code=400, detail="未提供有效的整理记录 ID")

        if len(ids) > self._max_batch:
            raise HTTPException(
                status_code=400,
                detail=f"单次最多删除 {self._max_batch} 条记录，请分批操作",
            )

        results: List[Dict[str, Any]] = []
        for history_id in ids:
            try:
                results.append(
                    self._delete_one(
                        db, history_id, delete_record, delete_src, delete_dest
                    )
                )
            except Exception as err:  # 单条失败不影响后续记录
                results.append(
                    {
                        "id": history_id,
                        "ok": False,
                        "message": str(err),
                        "deleted": {"record": False, "src": False, "dest": False},
                        "paths": {},
                    }
                )

        return {
            "results": results,
            "success_count": sum(1 for item in results if item.get("ok")),
            "failed_count": sum(1 for item in results if not item.get("ok")),
        }
