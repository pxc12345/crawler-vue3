from flask import Blueprint, jsonify, request

from blessing_db import blessing_db
from festival_engine import calculate_nearest_festival, generate_festival_text

blessing_bp = Blueprint("blessing", __name__)


DEFAULT_THEME = {
    "id": None,
    "name": "默认晨雾",
    "category": "高级粉色系",
    "background_color": "#f8efe9",
    "title_color": "#7b2f36",
    "body_color": "#3d312e",
    "button_color": "#cf6f5d",
    "card_color": "#fffaf6",
}

DEFAULT_EFFECT_PROFILE = {
    "id": None,
    "name": "默认高级流光",
    "welcome_effects": ["mist-glow", "light-particles"],
    "intro_effects": ["silk-flow", "letter-unfold"],
    "main_effects": ["stardust", "festival-bokeh", "card-highlight"],
    "closing_effects": ["signature-draw", "seal-fade", "afterglow"],
    "particle_density": 0.65,
    "motion_level": 0.55,
    "glow_intensity": 0.72,
}

CONTENT_STEPS = [
    ("welcome", 1, "开场欢迎页"),
    ("intro", 2, "导语页"),
    ("main", 3, "主祝福页"),
    ("closing", 4, "收尾落款页"),
]


def success(data=None, msg="成功"):
    return jsonify({"code": 200, "msg": msg, "data": data})


def fail(msg="失败", code=400):
    return jsonify({"code": code, "msg": msg, "data": None})


def split_effects(raw):
    return [item.strip() for item in (raw or "").split(",") if item.strip()]


def join_effects(items):
    return ",".join([item.strip() for item in items if item and item.strip()])


def theme_payload(row):
    if not row:
        return dict(DEFAULT_THEME)
    return {
        "id": row.get("theme_id") or row.get("id"),
        "name": row.get("theme_name") or row.get("name") or DEFAULT_THEME["name"],
        "category": row.get("theme_category") or row.get("category") or DEFAULT_THEME["category"],
        "background_color": row.get("background_color") or row.get("bg_color") or DEFAULT_THEME["background_color"],
        "title_color": row.get("title_color") or row.get("text_color") or DEFAULT_THEME["title_color"],
        "body_color": row.get("body_color") or row.get("text_color") or DEFAULT_THEME["body_color"],
        "button_color": row.get("button_color") or DEFAULT_THEME["button_color"],
        "card_color": row.get("card_color") or DEFAULT_THEME["card_color"],
    }


def effect_profile_payload(row):
    if not row:
        return dict(DEFAULT_EFFECT_PROFILE)
    return {
        "id": row.get("effect_profile_id") or row.get("id"),
        "name": row.get("effect_profile_name") or row.get("name") or DEFAULT_EFFECT_PROFILE["name"],
        "welcome_effects": split_effects(row.get("welcome_effects")) or DEFAULT_EFFECT_PROFILE["welcome_effects"],
        "intro_effects": split_effects(row.get("intro_effects")) or DEFAULT_EFFECT_PROFILE["intro_effects"],
        "main_effects": split_effects(row.get("main_effects")) or DEFAULT_EFFECT_PROFILE["main_effects"],
        "closing_effects": split_effects(row.get("closing_effects")) or DEFAULT_EFFECT_PROFILE["closing_effects"],
        "particle_density": float(row.get("particle_density") or DEFAULT_EFFECT_PROFILE["particle_density"]),
        "motion_level": float(row.get("motion_level") or DEFAULT_EFFECT_PROFILE["motion_level"]),
        "glow_intensity": float(row.get("glow_intensity") or DEFAULT_EFFECT_PROFILE["glow_intensity"]),
    }


def normalize_theme(data):
    required = ["name", "category", "background_color", "title_color", "body_color", "button_color", "card_color"]
    normalized = {}
    for key in required:
        value = (data.get(key) or "").strip()
        if not value:
            raise ValueError(f"缺少主题字段: {key}")
        normalized[key] = value
    normalized["sort"] = int(data.get("sort") or 0)
    return normalized


def normalize_effect_profile(data):
    name = (data.get("name") or "").strip()
    if not name:
        raise ValueError("缺少特效方案名称")

    def effect_list(key):
        value = data.get(key) or []
        if not isinstance(value, list) or not value:
            raise ValueError(f"请至少为 {key} 选择一个特效")
        return join_effects(value)

    return {
        "name": name,
        "welcome_effects": effect_list("welcome_effects"),
        "intro_effects": effect_list("intro_effects"),
        "main_effects": effect_list("main_effects"),
        "closing_effects": effect_list("closing_effects"),
        "particle_density": float(data.get("particle_density") or 0.65),
        "motion_level": float(data.get("motion_level") or 0.55),
        "glow_intensity": float(data.get("glow_intensity") or 0.72),
        "sort": int(data.get("sort") or 0),
    }


def birthday_default_steps():
    return [
        {"step_key": "welcome", "step_order": 1, "title": "今夜为你亮灯", "body": "把日历翻到今天，连风都像替你轻声报喜。愿你推开这一页时，先被温柔接住，再被喜悦慢慢包围。"},
        {"step_key": "intro", "step_order": 2, "title": "把好时光留给你", "body": "愿你走过的每一步都算数，认真喜欢过的事情都能开花，努力熬过的夜晚都能在未来变成星光。"},
        {"step_key": "main", "step_order": 3, "title": "愿望开始靠近", "body": "愿你新一岁的生活有热烈也有安稳，有奔赴远方的勇气，也有回到日常的松弛。愿欢喜有回应，期待有着落，生日快乐。"},
        {"step_key": "closing", "step_order": 4, "title": "把祝福珍藏", "body": "把这一份偏爱好好收下吧。愿它陪你度过明亮的时刻，也陪你穿过普通的日子，提醒你一直值得被认真祝福。"},
    ]


def festival_default_steps(festival_name=""):
    festival_title = festival_name or "节日"
    return [
        {"step_key": "welcome", "step_order": 1, "title": f"{festival_title}已至", "body": "节日像一封刚拆开的信，先把热闹送到门前，再把惦念慢慢放进心里。今天这一份祝福，也专门为你而来。"},
        {"step_key": "intro", "step_order": 2, "title": "愿此刻被照亮", "body": "愿你无论身在何处，都能在这个节点里感受到陪伴、松弛和被惦记的安心，让生活暂时停下来，对你多一点温柔。"},
        {"step_key": "main", "step_order": 3, "title": "平安喜乐常在", "body": generate_festival_text(festival_name) if festival_name else "愿这个节日替你带来轻松和好消息，愿平安常在，喜乐常在，心之所向都有回音。"},
        {"step_key": "closing", "step_order": 4, "title": "心意缓缓落下", "body": "把这份节日心意留在今天，也带进之后的日子里。愿你接下来遇见的人和事，都能继续把温暖递给你。"},
    ]


def default_content(mode, festival_name=""):
    steps = birthday_default_steps() if mode == "birthday" else festival_default_steps(festival_name)
    return [{"mode": mode, **item} for item in steps]


def ensure_content_rows(mode, festival_name=""):
    rows = blessing_db.get_content_configs(mode)
    if rows and len(rows) == 4:
        return rows
    blessing_db.upsert_content_configs(mode, default_content(mode, festival_name))
    return blessing_db.get_content_configs(mode)


def content_payload(mode, festival_name=""):
    rows = ensure_content_rows(mode, festival_name)
    source = {row["step_key"]: row for row in rows}
    fallback = {item["step_key"]: item for item in default_content(mode, festival_name)}
    payload = []
    for step_key, step_order, step_name in CONTENT_STEPS:
        row = source.get(step_key) or fallback[step_key]
        payload.append({
            "mode": mode,
            "step_key": step_key,
            "step_name": step_name,
            "step_order": step_order,
            "title": row.get("title") or fallback[step_key]["title"],
            "body": row.get("body") or fallback[step_key]["body"],
        })
    return payload


@blessing_bp.route("/api/login", methods=["POST"])
def api_login():
    try:
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip()
        if not username:
            return fail("请输入账号")

        if username == "admin":
            return success({"role": "admin", "username": "admin"})

        user = blessing_db.get_user_by_username(username)
        if not user:
            return fail("账号无效，请重新输入")

        theme = theme_payload(user)
        effect_profile = effect_profile_payload(user)
        return success({
            "role": "user",
            "username": user["username"],
            "bg_color": theme["background_color"],
            "text_color": theme["body_color"],
            "theme_id": user.get("theme_id"),
            "theme": theme,
            "effect_profile_id": user.get("effect_profile_id"),
            "effect_profile": effect_profile,
        })
    except Exception as e:
        return fail(f"登录失败: {str(e)}", 500)


@blessing_bp.route("/api/settings/get", methods=["GET"])
def api_get_settings():
    try:
        setting = blessing_db.get_setting()
        if not setting:
            birthday_steps = content_payload("birthday")
            festival_steps = content_payload("festival")
            return success({
                "global_mode": "birthday",
                "current_nearest_festival": "",
                "birthday_default_text": birthday_steps[2]["body"],
                "festival_default_text": festival_steps[2]["body"],
                "content_steps": birthday_steps,
                "birthday_content_steps": birthday_steps,
                "festival_content_steps": festival_steps,
                "update_time": "",
            })

        mode = setting["global_mode"]
        festival_name = setting["current_nearest_festival"]
        birthday_steps = content_payload("birthday", festival_name)
        festival_steps = content_payload("festival", festival_name)
        return success({
            "global_mode": mode,
            "current_nearest_festival": festival_name,
            "birthday_default_text": setting["birthday_default_text"] or birthday_steps[2]["body"],
            "festival_default_text": setting["festival_default_text"] or festival_steps[2]["body"],
            "content_steps": birthday_steps if mode == "birthday" else festival_steps,
            "birthday_content_steps": birthday_steps,
            "festival_content_steps": festival_steps,
            "update_time": str(setting["update_time"]) if setting.get("update_time") else "",
        })
    except Exception as e:
        return fail(f"获取配置失败: {str(e)}", 500)


@blessing_bp.route("/api/settings/update", methods=["POST"])
def api_update_settings():
    try:
        data = request.get_json(silent=True) or {}
        global_mode = (data.get("global_mode") or "birthday").strip()
        birthday_text = (data.get("birthday_default_text") or "").strip()
        festival_text = (data.get("festival_default_text") or "").strip()

        if global_mode not in ("birthday", "festival"):
            return fail("模式必须为 birthday 或 festival")

        festival_name = ""
        if global_mode == "festival":
            festivals = blessing_db.get_all_festivals()
            if festivals:
                festival_name = calculate_nearest_festival(festivals)

        blessing_db.update_setting(global_mode, birthday_text, festival_text, festival_name)
        return success(msg="配置更新成功")
    except Exception as e:
        return fail(f"更新配置失败: {str(e)}", 500)


@blessing_bp.route("/api/festival/nearest", methods=["GET"])
def api_refresh_festival():
    try:
        festivals = blessing_db.get_all_festivals()
        if not festivals:
            return fail("节日数据为空，请先初始化")

        festival_name = calculate_nearest_festival(festivals)
        blessing_db.update_festival_name(festival_name)
        ensure_content_rows("festival", festival_name)
        return success({"festival_name": festival_name, "festival_text": generate_festival_text(festival_name)})
    except Exception as e:
        return fail(f"刷新节日失败: {str(e)}", 500)


@blessing_bp.route("/api/user/list", methods=["GET"])
def api_user_list():
    try:
        users = blessing_db.get_all_users()
        for user in users:
            if user.get("create_time"):
                user["create_time"] = str(user["create_time"])
            user["theme"] = theme_payload(user)
            user["effect_profile"] = effect_profile_payload(user)
        return success(users)
    except Exception as e:
        return fail(f"获取用户列表失败: {str(e)}", 500)


@blessing_bp.route("/api/user/save", methods=["POST"])
def api_user_save():
    try:
        data = request.get_json(silent=True) or {}
        user_id = data.get("id")
        username = (data.get("username") or "").strip()
        theme_id = data.get("theme_id")
        effect_profile_id = data.get("effect_profile_id")

        if not username:
            return fail("请输入账号名")
        if not theme_id:
            return fail("请选择账号主题")
        if not effect_profile_id:
            return fail("请选择账号特效方案")

        theme = blessing_db.get_theme_by_id(theme_id)
        if not theme:
            return fail("主题不存在或已删除")
        effect_profile = blessing_db.get_effect_profile_by_id(effect_profile_id)
        if not effect_profile:
            return fail("特效方案不存在或已删除")

        bg_color = theme["background_color"]
        text_color = theme["body_color"]
        existing = blessing_db.get_user_by_username(username)

        if user_id:
            if existing and existing["id"] != user_id:
                return fail("账号已存在")
            blessing_db.update_user(user_id, bg_color, text_color, theme_id, effect_profile_id)
            return success(msg="账号更新成功")

        if existing:
            return fail("账号已存在")
        blessing_db.create_user(username, bg_color, text_color, theme_id, effect_profile_id)
        return success(msg="账号创建成功")
    except Exception as e:
        return fail(f"保存失败: {str(e)}", 500)


@blessing_bp.route("/api/user/delete", methods=["DELETE"])
def api_user_delete():
    try:
        data = request.get_json(silent=True) or {}
        user_id = data.get("id")
        if not user_id:
            return fail("缺少账号ID")
        blessing_db.delete_user(user_id)
        return success(msg="删除成功")
    except Exception as e:
        return fail(f"删除失败: {str(e)}", 500)


@blessing_bp.route("/api/theme/list", methods=["GET"])
def api_theme_list():
    try:
        return success(blessing_db.get_all_themes())
    except Exception as e:
        return fail(f"获取主题失败: {str(e)}", 500)


@blessing_bp.route("/api/theme/save", methods=["POST"])
def api_theme_save():
    try:
        data = request.get_json(silent=True) or {}
        theme_id = data.get("id")
        theme = normalize_theme(data)
        if theme_id:
            blessing_db.update_theme(theme_id, theme)
            return success(msg="主题更新成功")
        blessing_db.create_theme(theme)
        return success(msg="主题创建成功")
    except ValueError as e:
        return fail(str(e))
    except Exception as e:
        return fail(f"保存主题失败: {str(e)}", 500)


@blessing_bp.route("/api/theme/delete", methods=["DELETE"])
def api_theme_delete():
    try:
        data = request.get_json(silent=True) or {}
        theme_id = data.get("id")
        if not theme_id:
            return fail("缺少主题ID")
        blessing_db.delete_theme(theme_id)
        return success(msg="主题删除成功")
    except Exception as e:
        return fail(f"删除主题失败: {str(e)}", 500)


@blessing_bp.route("/api/effect/list", methods=["GET"])
def api_effect_list():
    try:
        rows = [effect_profile_payload(row) for row in blessing_db.get_all_effect_profiles()]
        return success(rows)
    except Exception as e:
        return fail(f"获取特效方案失败: {str(e)}", 500)


@blessing_bp.route("/api/effect/save", methods=["POST"])
def api_effect_save():
    try:
        data = request.get_json(silent=True) or {}
        profile_id = data.get("id")
        profile = normalize_effect_profile(data)
        if profile_id:
            blessing_db.update_effect_profile(profile_id, profile)
            return success(msg="特效方案更新成功")
        blessing_db.create_effect_profile(profile)
        return success(msg="特效方案创建成功")
    except ValueError as e:
        return fail(str(e))
    except Exception as e:
        return fail(f"保存特效方案失败: {str(e)}", 500)


@blessing_bp.route("/api/effect/delete", methods=["DELETE"])
def api_effect_delete():
    try:
        data = request.get_json(silent=True) or {}
        profile_id = data.get("id")
        if not profile_id:
            return fail("缺少特效方案ID")
        blessing_db.delete_effect_profile(profile_id)
        return success(msg="特效方案删除成功")
    except Exception as e:
        return fail(f"删除特效方案失败: {str(e)}", 500)


@blessing_bp.route("/api/content/get", methods=["GET"])
def api_content_get():
    try:
        mode = (request.args.get("mode") or "").strip()
        setting = blessing_db.get_setting() or {}
        festival_name = setting.get("current_nearest_festival") or ""

        if mode:
            if mode not in ("birthday", "festival"):
                return fail("模式必须为 birthday 或 festival")
            return success(content_payload(mode, festival_name))

        return success({
            "birthday": content_payload("birthday", festival_name),
            "festival": content_payload("festival", festival_name),
        })
    except Exception as e:
        return fail(f"获取文案配置失败: {str(e)}", 500)


@blessing_bp.route("/api/content/save", methods=["POST"])
def api_content_save():
    try:
        data = request.get_json(silent=True) or {}
        mode = (data.get("mode") or "").strip()
        steps = data.get("steps") or []

        if mode not in ("birthday", "festival"):
            return fail("模式必须为 birthday 或 festival")
        if len(steps) != 4:
            return fail("必须配置四个步骤页面")

        allowed = {key for key, _, _ in CONTENT_STEPS}
        normalized = []
        for index, item in enumerate(steps):
            step_key = item.get("step_key")
            if step_key not in allowed:
                return fail("步骤标识无效")
            title = (item.get("title") or "").strip()
            body = (item.get("body") or "").strip()
            if not title or not body:
                return fail("四个步骤的标题和正文都必须填写")
            normalized.append({
                "step_key": step_key,
                "step_order": int(item.get("step_order") or index + 1),
                "title": title,
                "body": body,
            })

        blessing_db.upsert_content_configs(mode, normalized)
        return success(msg="分步文案保存成功")
    except Exception as e:
        return fail(f"保存文案配置失败: {str(e)}", 500)
