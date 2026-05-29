"""
统一时间处理：数据库存储 UTC（naive DATETIME），API 返回用户本地时区格式化字符串。

约定：
- 写入数据库使用 now_utc() / now_utc_str()
- 从数据库读出后使用 format_api_datetime() 转为用户本地时间
- 用户时区通过请求头 X-Timezone 传递（IANA 时区名，如 Asia/Shanghai）
"""
from __future__ import annotations

import os
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional, Union
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

API_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_TIMEZONE = os.environ.get("APP_TIMEZONE", "Asia/Shanghai")
TIMEZONE_HEADER = "X-Timezone"
# 数据库 collected_at 语义：utc=存 UTC naive（默认）；local=存服务器/北京时间 naive
DB_TIME_STORAGE = os.environ.get("DB_TIME_STORAGE", "utc").strip().lower()

CONFIG_DATETIME_FIELDS = ("last_run_started_at",)

# tzdata 不可用时使用的固定偏移回退（小时）
TZ_FALLBACK_OFFSETS = {
    "UTC": 0,
    "Asia/Shanghai": 8,
    "Asia/Hong_Kong": 8,
    "Asia/Taipei": 8,
    "Asia/Singapore": 8,
    "Asia/Tokyo": 9,
    "Europe/London": 0,
    "Europe/Paris": 1,
    "America/New_York": -5,
    "America/Los_Angeles": -8,
}


def _timezone_from_name(tz_name: str):
    """解析 IANA 时区，失败时使用固定偏移回退。"""
    name = (tz_name or DEFAULT_TIMEZONE).strip()
    try:
        return ZoneInfo(name)
    except Exception:
        offset_hours = TZ_FALLBACK_OFFSETS.get(name)
        if offset_hours is None and name != DEFAULT_TIMEZONE:
            offset_hours = TZ_FALLBACK_OFFSETS.get(DEFAULT_TIMEZONE)
        if offset_hours is None:
            offset_hours = 8
        return timezone(timedelta(hours=offset_hours))


def resolve_timezone(tz_name: Optional[str] = None):
    """解析并校验时区名称，无效时回退到默认时区。"""
    return _timezone_from_name((tz_name or DEFAULT_TIMEZONE).strip())


def now_utc() -> datetime:
    """当前 UTC 时间（naive，用于写入数据库）。"""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def now_utc_str() -> str:
    """当前 UTC 时间字符串，格式 YYYY-MM-DD HH:MM:SS。"""
    return now_utc().strftime(API_DATETIME_FORMAT)


def get_request_timezone() -> str:
    """从 Flask 请求上下文获取用户时区，无请求时使用默认时区。"""
    try:
        from flask import g, has_request_context, request

        if has_request_context():
            cached = getattr(g, "user_timezone", None)
            if cached:
                return get_effective_timezone(cached)
            header_tz = (request.headers.get(TIMEZONE_HEADER) or "").strip()
            if header_tz:
                _timezone_from_name(header_tz)
                return get_effective_timezone(header_tz)
    except ImportError:
        pass
    return DEFAULT_TIMEZONE


def get_db_time_storage() -> str:
    """返回数据库时间存储模式：utc 或 local。"""
    mode = (DB_TIME_STORAGE or "utc").lower()
    return "local" if mode == "local" else "utc"


def get_timezone_offset_hours(tz_name: Optional[str] = None) -> int:
    """用户时区相对 UTC 的小时偏移（用于 UTC 存储 → 本地展示）。"""
    eff = get_effective_timezone(tz_name or get_request_timezone())
    hours = TZ_FALLBACK_OFFSETS.get(eff)
    if hours is not None:
        return int(hours)
    try:
        tz = ZoneInfo(eff)
        offset = datetime.now(timezone.utc).astimezone(tz).utcoffset()
        return int(offset.total_seconds() // 3600) if offset else 0
    except Exception:
        return 8


def get_effective_timezone(tz_name: Optional[str] = None) -> str:
    """
    解析展示用时区。UTC/GMT 统一映射为 DEFAULT_TIMEZONE（Asia/Shanghai），
    避免折线图按世界时 1、2 点展示而非北京时间 9、10 点。
    """
    name = (tz_name or DEFAULT_TIMEZONE).strip()
    if name.upper() in ("UTC", "ETC/UTC", "GMT", "ETC/GMT", "Z"):
        return DEFAULT_TIMEZONE
    return name or DEFAULT_TIMEZONE


def assume_utc(dt: datetime) -> datetime:
    """将 naive datetime 视为 UTC，返回 timezone-aware UTC。"""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def parse_to_utc_naive(value: Union[str, datetime, None]) -> Optional[datetime]:
    """解析时间值为 UTC naive datetime（用于数据库比较/写入）。"""
    if value is None:
        return None
    if isinstance(value, datetime):
        return assume_utc(value).replace(tzinfo=None)
    text = str(value).strip()
    if not text:
        return None
    for fmt in (
        API_DATETIME_FORMAT,
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
    ):
        try:
            parsed = datetime.strptime(text.replace("Z", "+00:00"), fmt)
            return assume_utc(parsed).replace(tzinfo=None)
        except ValueError:
            continue
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return assume_utc(parsed).replace(tzinfo=None)
    except ValueError:
        return None


def format_api_datetime(
    value: Union[str, datetime, None],
    tz_name: Optional[str] = None,
) -> Optional[str]:
    """
    将 UTC 存储的时间转换为用户本地时区字符串（YYYY-MM-DD HH:MM:SS）。
    用于所有返回前端的 API 响应。
    """
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None

    try:
        if isinstance(value, datetime):
            utc_dt = assume_utc(value)
        else:
            utc_naive = parse_to_utc_naive(value)
            if utc_naive is None:
                return str(value)
            utc_dt = utc_naive.replace(tzinfo=timezone.utc)

        local_tz = resolve_timezone(tz_name or get_request_timezone())
        local_dt = utc_dt.astimezone(local_tz)
        return local_dt.strftime(API_DATETIME_FORMAT)
    except Exception:
        if isinstance(value, datetime):
            return value.strftime(API_DATETIME_FORMAT)
        return str(value)


def format_row_datetimes(
    row: Optional[Dict[str, Any]],
    *fields: str,
    tz_name: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """批量格式化字典行中的时间字段。"""
    if not row:
        return row
    tz = tz_name or get_request_timezone()
    for field in fields:
        if row.get(field) is not None:
            row[field] = format_api_datetime(row[field], tz)
    return row


def format_rows_datetimes(
    rows: list,
    *fields: str,
    tz_name: Optional[str] = None,
) -> list:
    """批量格式化列表中每行的时间字段。"""
    for row in rows:
        format_row_datetimes(row, *fields, tz_name=tz_name)
    return rows


def format_config_for_api(
    config: Optional[Dict[str, Any]],
    tz_name: Optional[str] = None,
) -> Dict[str, Any]:
    """格式化任务 config 中的时间字段（仅用于 API 响应，不影响 DB 查询）。"""
    if not config:
        return config or {}
    result = dict(config)
    tz = tz_name or get_request_timezone()
    for field in CONFIG_DATETIME_FIELDS:
        if result.get(field):
            result[field] = format_api_datetime(result[field], tz)
    return result


def format_task_for_api(
    task: Optional[Dict[str, Any]],
    tz_name: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """格式化任务对象中所有需要展示的时间字段（仅在 API 响应层调用一次）。"""
    if not task:
        return task
    format_row_datetimes(task, "created_at", "updated_at", tz_name=tz_name)
    if isinstance(task.get("config"), dict):
        task["config"] = format_config_for_api(task["config"], tz_name=tz_name)
    return task


def format_template_for_api(
    template: Optional[Dict[str, Any]],
    tz_name: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """格式化模板对象中的时间字段（仅在 API 响应层调用一次）。"""
    if not template:
        return template
    format_row_datetimes(template, "created_at", "updated_at", tz_name=tz_name)
    return template


def utc_cutoff_days_ago(days: int) -> str:
    """返回 N 天前的 UTC 时间字符串，用于数据库清理等操作。"""
    cutoff = now_utc() - timedelta(days=days)
    return cutoff.strftime(API_DATETIME_FORMAT)


def get_local_day_bounds_utc(tz_name: Optional[str] = None):
    """返回用户本地「今天」起止时间（UTC naive），用于按本地日历日统计。"""
    tz = resolve_timezone(get_effective_timezone(tz_name or get_request_timezone()))
    now_utc_aware = datetime.now(timezone.utc)
    now_local = now_utc_aware.astimezone(tz)
    start_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    end_local = start_local + timedelta(days=1)
    start_utc = start_local.astimezone(timezone.utc).replace(tzinfo=None)
    end_utc = end_local.astimezone(timezone.utc).replace(tzinfo=None)
    return start_utc, end_utc


def local_datetime_str_to_utc_naive(
    value: Union[str, datetime, None],
    tz_name: Optional[str] = None,
) -> Optional[datetime]:
    """将 API 展示的本地时间字符串转为 UTC naive（用于数据库查询）。"""
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        tz = resolve_timezone(tz_name or get_request_timezone())
        return value.replace(tzinfo=tz).astimezone(timezone.utc).replace(tzinfo=None)
    text = str(value).strip()
    if not text:
        return None
    try:
        naive_local = datetime.strptime(text[:19], API_DATETIME_FORMAT)
    except ValueError:
        return parse_to_utc_naive(text)
    tz = resolve_timezone(tz_name or get_request_timezone())
    return naive_local.replace(tzinfo=tz).astimezone(timezone.utc).replace(tzinfo=None)


def normalize_since_for_query(
    value: Union[str, datetime, None],
    tz_name: Optional[str] = None,
) -> Optional[str]:
    """统一 since 参数：支持 UTC 或用户本地时间字符串，返回 UTC 字符串供 SQL 使用。"""
    utc_naive = local_datetime_str_to_utc_naive(value, tz_name)
    if utc_naive is None:
        return None
    return utc_naive.strftime(API_DATETIME_FORMAT)


def build_local_hour_labels(tz_name: Optional[str] = None) -> list:
    """生成 24 小时本地时区标签。"""
    return [f"{hour:02d}:00" for hour in range(24)]


def get_mysql_tz_offset(tz_name: Optional[str] = None) -> str:
    """返回 MySQL CONVERT_TZ 目标时区偏移，如 +08:00。"""
    tz = resolve_timezone(tz_name or get_request_timezone())
    offset = datetime.now(timezone.utc).astimezone(tz).utcoffset() or timedelta(0)
    total_seconds = int(offset.total_seconds())
    sign = "+" if total_seconds >= 0 else "-"
    total_seconds = abs(total_seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes = remainder // 60
    return f"{sign}{hours:02d}:{minutes:02d}"


def parse_db_datetime(value) -> Optional[datetime]:
    """将数据库读出的时间统一解析为 naive datetime。"""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.replace(tzinfo=None) if value.tzinfo else value
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.strptime(text[:19], API_DATETIME_FORMAT)
    except ValueError:
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
            return parsed.replace(tzinfo=None) if parsed.tzinfo else parsed
        except ValueError:
            return None


def to_local_hour(value, tz_name: Optional[str] = None) -> Optional[int]:
    """
    将数据库 naive 时间转为用户本地小时（0-23）。
    - DB_TIME_STORAGE=utc：库内为 UTC，按用户时区偏移转换（如 +8 → 索引 9、10）
    - DB_TIME_STORAGE=local：库内已是本地时间，直接取 hour
    """
    dt = parse_db_datetime(value)
    if dt is None:
        return None
    eff_tz = get_effective_timezone(tz_name or get_request_timezone())
    if get_db_time_storage() == "local":
        return dt.hour
    offset_hours = get_timezone_offset_hours(eff_tz)
    local_dt = dt + timedelta(hours=offset_hours)
    return local_dt.hour


def bucket_datetimes_by_local_hour(rows, tz_name: Optional[str] = None) -> list:
    """将 collected_at 记录按本地小时分桶，返回长度 24 的计数数组（索引=本地小时）。"""
    hourly = [0] * 24
    eff_tz = get_effective_timezone(tz_name or get_request_timezone())
    for row in rows:
        collected_at = row.get("collected_at") if isinstance(row, dict) else row
        local_hour = to_local_hour(collected_at, eff_tz)
        if local_hour is not None and 0 <= local_hour < 24:
            hourly[local_hour] += 1
    return hourly


def get_local_day_bounds_for_query(tz_name: Optional[str] = None):
    """
    返回「今日」查询用的起止时间（naive），与 DB_TIME_STORAGE 一致。
    utc：返回 UTC naive；local：返回本地日历日 naive。
    """
    eff_tz = get_effective_timezone(tz_name or get_request_timezone())
    if get_db_time_storage() == "local":
        tz = resolve_timezone(eff_tz)
        now_local = datetime.now(timezone.utc).astimezone(tz)
        start_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        end_local = start_local + timedelta(days=1)
        return start_local.replace(tzinfo=None), end_local.replace(tzinfo=None)
    return get_local_day_bounds_utc(eff_tz)


def setup_timezone_middleware(app) -> None:
    """注册 Flask 中间件：从请求头解析用户时区并存入 g.user_timezone。"""

    @app.before_request
    def _capture_user_timezone():
        from flask import g, request

        header_tz = (request.headers.get(TIMEZONE_HEADER) or "").strip()
        if header_tz:
            try:
                _timezone_from_name(header_tz)
                g.user_timezone = header_tz
            except Exception:
                g.user_timezone = DEFAULT_TIMEZONE
        else:
            g.user_timezone = DEFAULT_TIMEZONE
