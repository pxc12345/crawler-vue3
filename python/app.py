import os
from urllib.parse import quote_plus

from db_settings import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
    DB_CHARSET,
    PYMYSQL_CONFIG,
)

os.environ.setdefault("DB_HOST", DB_HOST)
os.environ.setdefault("DB_PORT", str(DB_PORT))
os.environ.setdefault("DB_USER", DB_USER)
os.environ.setdefault("DB_PASSWORD", DB_PASSWORD)
os.environ.setdefault("DB_NAME", DB_NAME)

SQLALCHEMY_DATABASE_URI = (
    "mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    "?charset=utf8mb4&ssl_verify_cert=true&ssl_verify_identity=true"
).format(
    user=quote_plus(DB_USER),
    password=quote_plus(DB_PASSWORD),
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

from flask import Flask, request, jsonify, Response, send_from_directory
from werkzeug.utils import secure_filename
import uuid
from flask_cors import CORS, cross_origin
from src.auth_service import auth_service
from src.notification_db import notification_db
from src.notifications.verification_service import verification_service
from src.datetime_utils import (
    format_api_datetime,
    format_config_for_api,
    format_row_datetimes,
    format_rows_datetimes,
    format_task_for_api,
    format_template_for_api,
    now_utc_str,
    setup_timezone_middleware,
    TIMEZONE_HEADER,
    get_request_timezone,
    get_effective_timezone,
    build_local_hour_labels,
    parse_to_utc_naive,
    API_DATETIME_FORMAT,
    now_utc,
)
from crawler_engine import crawler_engine, get_engine_info, ENGINE_VERSION
from crawler_db import crawler_db
from task_db import task_db
from alert_db import alert_db
from proxy_db import proxy_db
from system_db import system_db
from blessing_api import blessing_bp
from blessing_db import blessing_db
import re
import csv
import io
import json
import psutil
import pymysql
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
setup_timezone_middleware(app)

# notification_db 模块内为硬编码配置，导入后切换为线上库并重连
notification_db.db_config = dict(PYMYSQL_CONFIG)
notification_db.connection = None
try:
    notification_db._connect()
except Exception as e:
    print(f"[app] notification_db 连接警告: {e}")

def _cors_origins():
    default = (
        "https://crawler-pro.onrender.com,"
        "https://crawler-vue3.onrender.com,"
        "https://birth-project.onrender.com,"
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:3000,http://127.0.0.1:3000"
    )
    raw = os.getenv("CORS_ORIGINS", default)
    return [o.strip() for o in raw.split(",") if o.strip()]


_CORS_ORIGINS = _cors_origins()

_CORS_ALLOW_HEADERS = ["Content-Type", "Authorization", "X-Timezone"]

CORS(
    app,
    resources={
        r"/api/.*": {
            "origins": _CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": _CORS_ALLOW_HEADERS,
            "supports_credentials": True,
            "expose_headers": ["Content-Type", "Authorization"],
            "max_age": 86400,
        }
    },
    allow_headers=_CORS_ALLOW_HEADERS,
    supports_credentials=True,
)

crawler_db.connect()
task_db.connect()
alert_db.connect()
proxy_db.connect()
system_db.connect()
notification_db._init_db()

blessing_db.init_tables()
app.register_blueprint(blessing_bp)

_crawler_boot = get_engine_info()
print(
    "[app] CrawlerEngine version={version}, curl_cffi={curl_cffi}, cloudscraper={cloudscraper}".format(
        **_crawler_boot
    )
)
if ENGINE_VERSION != "v3-curl-multi":
    print("[app] WARNING: unexpected crawler engine version")


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_phone(phone):
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None


def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr


@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')

        if not username or len(username) < 3:
            return jsonify({'success': False, 'message': '用户名至少3个字符', 'code': 'INVALID_USERNAME'}), 400
        
        if not password or len(password) < 6:
            return jsonify({'success': False, 'message': '密码至少6个字符', 'code': 'INVALID_PASSWORD'}), 400

        if notification_db.get_user_by_username(username):
            return jsonify({'success': False, 'message': '用户名已存在', 'code': 'USERNAME_EXISTS'}), 400

        if email and notification_db.get_user_by_email(email):
            return jsonify({'success': False, 'message': '邮箱已被注册', 'code': 'EMAIL_EXISTS'}), 400

        if phone and notification_db.get_user_by_phone(phone):
            return jsonify({'success': False, 'message': '手机号已被注册', 'code': 'PHONE_EXISTS'}), 400

        password_hash = auth_service.hash_password(password)
        user_id = notification_db.create_user_with_username(
            username=username,
            email=email,
            phone=phone,
            password_hash=password_hash
        )

        notification_db.add_audit_log(
            user_id=user_id,
            action='REGISTER',
            ip_address=get_client_ip(),
            user_agent=request.headers.get('User-Agent'),
            details=f'用户 {username} 注册成功'
        )

        return jsonify({'success': True, 'message': '注册成功', 'data': {'user_id': user_id}}), 201

    except Exception as e:
        return jsonify({'success': False, 'message': '注册失败', 'code': 'REGISTER_FAILED', 'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        identifier = data.get('identifier')
        password = data.get('password')

        if not identifier or not password:
            return jsonify({'success': False, 'message': '请输入账号和密码', 'code': 'MISSING_CREDENTIALS'}), 400

        result = auth_service.authenticate_user(identifier, password)

        if result['success']:
            try:
                notification_db.add_audit_log(
                    user_id=result['data']['user']['id'],
                    action='LOGIN',
                    ip_address=get_client_ip(),
                    user_agent=request.headers.get('User-Agent'),
                    details=f'用户 {identifier} 登录成功'
                )
            except Exception as audit_err:
                print(f"[login] audit log failed (login still ok): {audit_err}")

        return jsonify(result), 200 if result['success'] else 401

    except Exception as e:
        print(f"[login] error: {e}")
        return jsonify({
            'success': False,
            'message': '登录失败，请检查服务端数据库与日志配置',
            'code': 'LOGIN_FAILED',
            'error': str(e)
        }), 500


@app.route('/api/auth/refresh', methods=['POST'])
def refresh_token():
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token')

        if not refresh_token:
            return jsonify({'success': False, 'message': '缺少Refresh Token', 'code': 'MISSING_TOKEN'}), 400

        result = auth_service.refresh_access_token(refresh_token)
        return jsonify(result), 200 if result['success'] else 401

    except Exception as e:
        return jsonify({'success': False, 'message': '刷新Token失败', 'code': 'REFRESH_FAILED', 'error': str(e)}), 500


@app.route('/api/auth/logout', methods=['POST'])
@auth_service.login_required
def logout():
    try:
        auth_header = request.headers.get('Authorization')
        _, access_token = auth_header.split()
        
        data = request.get_json()
        refresh_token = data.get('refresh_token')

        auth_service.blacklist_token(access_token)
        if refresh_token:
            auth_service.blacklist_token(refresh_token)

        notification_db.add_audit_log(
            user_id=request.user_id,
            action='LOGOUT',
            ip_address=get_client_ip(),
            user_agent=request.headers.get('User-Agent'),
            details=f'用户 {request.username} 登出成功'
        )

        return jsonify({'success': True, 'message': '登出成功'}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': '登出失败', 'code': 'LOGOUT_FAILED', 'error': str(e)}), 500


@app.route('/api/auth/forgot-password/send-code', methods=['POST'])
def send_forgot_password_code():
    try:
        data = request.get_json()
        target = data.get('target')

        if not target:
            return jsonify({'success': False, 'message': '请输入邮箱或手机号', 'code': 'MISSING_TARGET'}), 400

        if is_valid_email(target):
            result = verification_service.send_email_code(target)
        elif is_valid_phone(target):
            result = verification_service.send_sms_code(target)
        else:
            return jsonify({'success': False, 'message': '请输入有效的邮箱或手机号', 'code': 'INVALID_TARGET'}), 400

        return jsonify(result), 200 if result['success'] else 400

    except Exception as e:
        return jsonify({'success': False, 'message': '发送验证码失败', 'code': 'SEND_CODE_FAILED', 'error': str(e)}), 500


@app.route('/api/auth/forgot-password/verify-code', methods=['POST'])
def verify_forgot_password_code():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        code = data.get('code')
        target = data.get('target')

        if not all([user_id, code, target]):
            return jsonify({'success': False, 'message': '缺少必要参数', 'code': 'MISSING_PARAMS'}), 400

        code_type = 'email' if is_valid_email(target) else 'sms'
        result = verification_service.verify_code(user_id, code, code_type, target)

        return jsonify(result), 200 if result['success'] else 400

    except Exception as e:
        return jsonify({'success': False, 'message': '验证失败', 'code': 'VERIFY_FAILED', 'error': str(e)}), 500


@app.route('/api/auth/forgot-password/reset', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        new_password = data.get('new_password')

        if not user_id or not new_password:
            return jsonify({'success': False, 'message': '缺少必要参数', 'code': 'MISSING_PARAMS'}), 400

        if len(new_password) < 6:
            return jsonify({'success': False, 'message': '密码至少6个字符', 'code': 'INVALID_PASSWORD'}), 400

        result = auth_service.reset_password(user_id, new_password, check_history=True)
        
        if result['success']:
            notification_db.add_audit_log(
                user_id=user_id,
                action='RESET_PASSWORD',
                ip_address=get_client_ip(),
                user_agent=request.headers.get('User-Agent'),
                details='用户通过忘记密码流程重置密码'
            )

        return jsonify(result), 200 if result['success'] else 400

    except Exception as e:
        return jsonify({'success': False, 'message': '重置密码失败', 'code': 'RESET_FAILED', 'error': str(e)}), 500


@app.route('/api/auth/change-password', methods=['POST'])
@auth_service.login_required
def change_password():
    try:
        data = request.get_json()
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if not old_password or not new_password:
            return jsonify({'success': False, 'message': '缺少必要参数', 'code': 'MISSING_PARAMS'}), 400

        if len(new_password) < 6:
            return jsonify({'success': False, 'message': '新密码至少6个字符', 'code': 'INVALID_PASSWORD'}), 400

        user = notification_db.get_user_by_id(request.user_id)
        if not auth_service.verify_password(old_password, user['password_hash']):
            return jsonify({'success': False, 'message': '原密码错误', 'code': 'INVALID_OLD_PASSWORD'}), 400

        result = auth_service.reset_password(request.user_id, new_password, check_history=True)
        
        if result['success']:
            notification_db.add_audit_log(
                user_id=request.user_id,
                action='CHANGE_PASSWORD',
                ip_address=get_client_ip(),
                user_agent=request.headers.get('User-Agent'),
                details='用户修改密码'
            )

        return jsonify(result), 200 if result['success'] else 400

    except Exception as e:
        return jsonify({'success': False, 'message': '修改密码失败', 'code': 'CHANGE_FAILED', 'error': str(e)}), 500


@app.route('/api/user/profile', methods=['GET'])
@auth_service.login_required
def get_profile():
    try:
        user = notification_db.get_user_by_id(request.user_id)
        if not user:
            return jsonify({'success': False, 'message': '用户不存在', 'code': 'USER_NOT_FOUND'}), 404

        return jsonify({
            'success': True,
            'data': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'phone': user['phone'],
                'nickname': user.get('nickname', ''),
                'avatar_url': user.get('avatar_url', ''),
                'bio': user.get('bio', ''),
                'last_login_at': format_api_datetime(user['last_login_at']),
                'created_at': format_api_datetime(user['created_at'])
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': '获取用户信息失败', 'code': 'GET_PROFILE_FAILED', 'error': str(e)}), 500


@app.route('/api/user/profile', methods=['PUT'])
@auth_service.login_required
def update_profile():
    try:
        data = request.get_json()
        nickname = data.get('nickname')
        avatar_url = data.get('avatar_url')
        bio = data.get('bio')

        success, msg = notification_db.update_user_profile(
            user_id=request.user_id,
            nickname=nickname,
            avatar_url=avatar_url,
            bio=bio
        )

        if not success:
            return jsonify({'success': False, 'message': msg, 'code': 'PROFILE_UPDATE_FAILED'}), 400

        return jsonify({'success': True, 'message': '个人资料更新成功'}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': '更新个人资料失败', 'code': 'PROFILE_UPDATE_FAILED', 'error': str(e)}), 500


@app.route('/api/user/avatar', methods=['POST'])
@auth_service.login_required
def upload_user_avatar():
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False, 'message': '请选择头像文件', 'code': 'MISSING_FILE'
            }), 400
        file = request.files['file']
        if not file.filename:
            return jsonify({
                'success': False, 'message': '无效的文件', 'code': 'INVALID_FILE'
            }), 400
        ext = os.path.splitext(secure_filename(file.filename))[1].lower()
        if ext not in ('.jpg', '.jpeg', '.png', '.gif', '.webp'):
            return jsonify({
                'success': False, 'message': '仅支持 jpg/png/gif/webp', 'code': 'INVALID_FORMAT'
            }), 400
        filename = f"avatar_{request.user_id}_{uuid.uuid4().hex[:8]}{ext}"
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        avatar_url = f"/api/uploads/{filename}"
        notification_db.update_user_profile(
            user_id=request.user_id, avatar_url=avatar_url
        )
        return jsonify({
            'success': True,
            'message': '头像上传成功',
            'data': {'avatar_url': avatar_url}
        }), 200
    except Exception as e:
        return jsonify({
            'success': False, 'message': '头像上传失败', 'code': 'AVATAR_UPLOAD_FAILED', 'error': str(e)
        }), 500


@app.route('/api/uploads/<filename>', methods=['GET'])
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/user/recent-tasks', methods=['GET'])
@auth_service.login_required
def user_recent_tasks():
    try:
        limit = request.args.get('limit', 10, type=int)
        rows = task_db.get_recent_tasks(request.user_id, limit=limit)
        for row in rows:
            format_task_for_api(row)
        return jsonify({'success': True, 'data': rows}), 200
    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取最近任务失败', 'code': 'RECENT_TASKS_FAILED', 'error': str(e)
        }), 500


def _save_crawled_data(items):
    """爬虫数据保存回调函数，供爬虫引擎调用"""
    # 如果是完成回调消息
    if isinstance(items, dict) and items.get('type') == 'complete':
        task_id = items.get('task_id')
        status = items.get('status', 'completed').upper()
        if status == 'ERROR':
            status = 'FAILED'
        if task_id:
            # 优先使用爬虫线程完成时附带的快照，避免引擎单例被重置后读到 0
            engine_status = crawler_engine.get_status()
            execution_time = items.get('execution_time')
            if execution_time is None:
                execution_time = engine_status.get('elapsed_seconds', 0)
            data_count = items.get('collected_count')
            if data_count is None:
                data_count = engine_status.get('collected_count', 0)
            error_message = items.get('error_message')
            if error_message is None:
                error_message = engine_status.get('error_message', '')

            total_pages = items.get('total_pages') or engine_status.get('total_pages', 1)
            succeeded_pages = items.get('succeeded_pages')
            if succeeded_pages is None:
                succeeded_pages = engine_status.get('succeeded_pages', 0)
            success_rate = items.get('success_rate')
            if success_rate is None:
                success_rate = min(
                    100.0,
                    round((succeeded_pages / max(1, total_pages)) * 100, 2),
                )
            
            # 更新任务统计信息（包含错误消息）
            task_db.update_task_stats(task_id, execution_time, data_count, success_rate, error_message)
            # 更新任务状态
            task_db.update_task_status(task_id, status)
            
            # 创建执行版本记录
            task = task_db.get_by_id(task_id)
            if task:
                config = task.get('config', {})
                if isinstance(config, str):
                    try:
                        import json
                        config = json.loads(config)
                    except:
                        config = {}
                # 添加执行结果到配置中
                config['_last_execution'] = {
                    'status': status,
                    'execution_time': execution_time,
                    'data_count': data_count,
                    'success_rate': success_rate,
                    'error_message': error_message
                }
                task_db.save_execution_record(task_id, config, status, data_count)

                if status == 'COMPLETED':
                    system_db.add_log(level='INFO', source='crawler',
                        message=f'任务[{task_id}] 执行完成: 耗时{execution_time}s, 采集{data_count}条数据, 成功率{success_rate}%',
                        task_id=task_id)
                elif status in ('ERROR', 'FAILED'):
                    system_db.add_log(level='ERROR', source='crawler',
                        message=f'任务[{task_id}] 执行失败: {error_message[:200] if error_message else "未知错误"}',
                        task_id=task_id)
                elif status == 'STOPPED':
                    system_db.add_log(level='WARNING', source='crawler',
                        message=f'任务[{task_id}] 手动停止: 耗时{execution_time}s, 已采集{data_count}条',
                        task_id=task_id)
                else:
                    system_db.add_log(level='INFO', source='crawler',
                        message=f'任务[{task_id}] 状态更新: {status}, 耗时{execution_time}s, 数据{data_count}条',
                        task_id=task_id)

            print(f"[Task] Task {task_id} completed: time={execution_time}s, data={data_count}, rate={success_rate}%, error={error_message[:50] if error_message else 'none'}")
        return
    # 执行过程日志（由爬虫引擎推送）
    if isinstance(items, dict) and items.get('type') == 'log':
        task_id = items.get('task_id')
        if task_id:
            system_db.add_log(
                level=items.get('level', 'INFO'),
                source='crawler',
                message=items.get('message', ''),
                task_id=task_id
            )
        return 0

    # 普通数据保存 - 从爬虫引擎获取当前 task_id
    task_id = crawler_engine._task_id if hasattr(crawler_engine, '_task_id') else None
    saved_count = crawler_db.save_batch(items, task_id=task_id)
    if task_id and isinstance(items, list) and items:
        try:
            task_row = task_db.get_by_id(task_id)
            uid = task_row.get('user_id') if task_row else None
            if uid:
                crawler_db.sync_auto_write_for_user(uid, items)
        except Exception as sync_err:
            print(f"[auto_write] sync skip: {sync_err}")
    if task_id and isinstance(items, list) and items:
        page_no = items[0].get('page_number', '?')
        system_db.add_log(
            level='INFO', source='crawler',
            message=f'任务[{task_id}] 第{page_no}页完成: 解析{len(items)}条, 入库{saved_count}条',
            task_id=task_id
        )
    return saved_count


@app.route('/api/crawler/start', methods=['POST'])
def crawler_start():
    """启动爬虫任务"""
    try:
        data = request.get_json()
        target_url = (data.get('target_url') or '').strip()
        total_pages = data.get('total_pages', 1)
        interval_seconds = data.get('interval_seconds', 3)
        crawl_mode = (data.get('crawl_mode') or 'link').strip().lower()

        if not target_url:
            return jsonify({
                'success': False, 'message': '请输入目标网址', 'code': 'MISSING_URL'
            }), 400

        if not target_url.startswith(('http://', 'https://')):
            return jsonify({
                'success': False, 'message': '请输入有效的网址（以 http:// 或 https:// 开头）', 'code': 'INVALID_URL'
            }), 400

        if not isinstance(total_pages, int) or total_pages < 1 or total_pages > 100:
            return jsonify({
                'success': False, 'message': '爬取页数需在 1-100 之间', 'code': 'INVALID_PAGES'
            }), 400

        if not isinstance(interval_seconds, (int, float)) or interval_seconds < 1 or interval_seconds > 60:
            return jsonify({
                'success': False, 'message': '请求间隔需在 1-60 秒之间', 'code': 'INVALID_INTERVAL'
            }), 400

        # 验证爬取模式
        valid_modes = ['link', 'image', 'mixed']
        if crawl_mode not in valid_modes:
            return jsonify({
                'success': False, 'message': f'爬取模式必须是 {", ".join(valid_modes)} 之一', 'code': 'INVALID_MODE'
            }), 400

        crawl_options = _build_crawl_options(data or {})
        success, message = crawler_engine.start(
            target_url,
            total_pages,
            int(interval_seconds),
            _save_crawled_data,
            crawl_mode,
            crawl_options=crawl_options,
        )
        return jsonify({'success': success, 'message': message}), 200 if success else 400

    except Exception as e:
        return jsonify({
            'success': False, 'message': '启动爬虫失败', 'code': 'START_FAILED', 'error': str(e)
        }), 500


@app.route('/api/crawler/stop', methods=['POST'])
def crawler_stop():
    """停止爬虫任务"""
    try:
        success, message = crawler_engine.stop()
        if not success:
            crawler_engine.reset()
        return jsonify({'success': success, 'message': message}), 200 if success else 400

    except Exception as e:
        return jsonify({
            'success': False, 'message': '停止爬虫失败', 'code': 'STOP_FAILED', 'error': str(e)
        }), 500


@app.route('/api/crawler/status', methods=['GET'])
def crawler_status():
    """获取爬虫运行状态"""
    try:
        status = crawler_engine.get_status()
        return jsonify({'success': True, 'data': status}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取状态失败', 'code': 'STATUS_FAILED', 'error': str(e)
        }), 500


@app.route('/api/crawler/data', methods=['GET'])
def crawler_data_list():
    """分页查询爬取数据列表"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        keyword = request.args.get('keyword', '', type=str)

        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        rows, total = crawler_db.get_list(page=page, page_size=page_size, keyword=keyword)

        return jsonify({
            'success': True,
            'data': {
                'list': rows,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '查询数据失败', 'code': 'QUERY_FAILED', 'error': str(e)
        }), 500


@app.route('/api/crawler/data', methods=['DELETE'])
def crawler_data_clear():
    """清空所有爬取数据"""
    try:
        success, message = crawler_db.clear_all()
        crawler_engine.reset()
        return jsonify({'success': success, 'message': message}), 200 if success else 500

    except Exception as e:
        return jsonify({
            'success': False, 'message': '清空数据失败', 'code': 'CLEAR_FAILED', 'error': str(e)
        }), 500


@app.route('/api/crawler/export', methods=['GET'])
def crawler_data_export():
    """导出爬取数据为 CSV 文件"""
    try:
        rows = crawler_db.get_all()

        if not rows:
            return jsonify({
                'success': False, 'message': '暂无数据可导出', 'code': 'NO_DATA'
            }), 400

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', '标题', '链接', '内容摘要', '来源网址', '页码', '采集时间'])
        for row in rows:
            writer.writerow([
                row.get('id', ''),
                row.get('title', ''),
                row.get('link', ''),
                row.get('content', ''),
                row.get('source_url', ''),
                row.get('page_number', ''),
                row.get('collected_at', '')
            ])

        output.seek(0)
        return Response(
            output.getvalue().encode('utf-8-sig'),
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=crawler_data_export.csv',
                'Content-Type': 'text/csv; charset=utf-8-sig'
            }
        )

    except Exception as e:
        return jsonify({
            'success': False, 'message': '导出数据失败', 'code': 'EXPORT_FAILED', 'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    crawler_info = get_engine_info()
    return jsonify({
        'success': True,
        'message': 'Server is running',
        'template_api': 'v2',
        'template_features': ['PUT', 'use', 'favorite', 'category', 'full_config'],
        'data_api': 'v2',
        'data_features': ['delete', 'batch_delete', 'filter', 'sort'],
        'crawler': crawler_info,
        'crawler_ready': crawler_info.get('curl_cffi') is True,
    }), 200


# ==================== Task Management Routes ====================

@app.route('/api/tasks', methods=['GET'])
@auth_service.login_required
def task_list():
    try:
        status = request.args.get('status', '', type=str)
        keyword = request.args.get('keyword', '', type=str)
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)

        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        tasks, total = task_db.get_list(
            user_id=request.user_id,
            status=status,
            keyword=keyword,
            page=page,
            page_size=page_size
        )

        # 仅对当前引擎正在执行的任务附加实时状态
        engine_status = crawler_engine.get_status()
        engine_task_id = engine_status.get('task_id')
        for task in tasks:
            format_task_for_api(task)
            if engine_task_id and str(task.get('id')) == str(engine_task_id):
                task['crawler_status'] = engine_status
            else:
                task['crawler_status'] = {}

        return jsonify({
            'success': True,
            'data': {
                'list': tasks,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取任务列表失败', 'code': 'TASK_LIST_FAILED', 'error': str(e)
        }), 500


@app.route('/api/tasks', methods=['POST'])
@auth_service.login_required
def task_create():
    try:
        data = request.get_json()
        name = (data.get('name') or '').strip()
        task_type = (data.get('task_type') or '').strip()
        config = data.get('config', {})
        description = (data.get('description') or '').strip()
        template_id = data.get('template_id')

        if not name:
            return jsonify({
                'success': False, 'message': '请输入任务名称', 'code': 'MISSING_NAME'
            }), 400

        if not task_type:
            if isinstance(config, dict):
                task_type = (config.get('task_type') or 'crawler').strip()
            else:
                task_type = 'crawler'

        normalized_config = _normalize_template_config(config if isinstance(config, dict) else {})

        task_id = task_db.create(
            user_id=request.user_id,
            name=name,
            task_type=task_type,
            config=normalized_config,
            description=description,
            template_id=template_id
        )

        if task_id:
            task_db.update_task(task_id, **_sync_task_columns_from_config(normalized_config))

        return jsonify({
            'success': True, 'message': '创建任务成功', 'data': {'task_id': task_id}
        }), 201

    except Exception as e:
        return jsonify({
            'success': False, 'message': '创建任务失败', 'code': 'TASK_CREATE_FAILED', 'error': str(e)
        }), 500


def _sync_task_columns_from_config(normalized):
    """将规范化 config 同步到任务表顶层字段，便于列表展示与查询。"""
    if not isinstance(normalized, dict):
        return {}
    return {
        'target_url': normalized.get('target_url', ''),
        'cron_expr': normalized.get('cron_expr', ''),
        'concurrency': int(normalized.get('concurrency') or 1),
        'interval_seconds': int(normalized.get('interval_seconds') or 3),
        'retry_count': int(normalized.get('max_retries') or 0),
        'retry_interval': int(normalized.get('retry_interval') or 60),
        'proxy_group': normalized.get('proxy_group') or '',
    }


def _normalize_template_config(config):
    """合并并规范化模板配置字段"""
    if not isinstance(config, dict):
        config = {}
    interval_seconds = config.get('interval_seconds')
    if interval_seconds is None and config.get('interval') is not None:
        raw = config.get('interval')
        interval_seconds = int(raw / 1000) if raw and raw > 60 else raw
    max_retries = config.get('max_retries')
    if max_retries is None:
        max_retries = config.get('maxRetries', 6)
    return {
        'target_url': (config.get('target_url') or '').strip(),
        'cron_expr': config.get('cron_expr') or '*/30 * * * *',
        'interval_seconds': int(interval_seconds or 3),
        'concurrency': int(config.get('concurrency') or 1),
        'max_retries': int(max_retries or 6),
        'maxRetries': int(max_retries or 6),
        'retry_interval': int(config.get('retry_interval') or 3),
        'crawl_mode': (config.get('crawl_mode') or 'link').strip().lower(),
        'total_pages': int(config.get('total_pages') or 1),
        'headers': config.get('headers') or {},
        'proxy_group': (config.get('proxy_group') or '').strip(),
        'task_type': (config.get('task_type') or 'crawler').strip(),
    }


def _build_crawl_options(config):
    """从任务/模板配置构建爬虫引擎选项"""
    if not isinstance(config, dict):
        config = {}
    max_retries = config.get('max_retries')
    if max_retries is None:
        max_retries = config.get('maxRetries', 6)
    max_retries = int(max_retries or 6)
    if max_retries < 1:
        max_retries = 6
    retry_interval = int(config.get('retry_interval') or 3)
    if retry_interval < 1:
        retry_interval = 3
    return {
        'max_retries': max_retries,
        'retry_interval': retry_interval,
        'timeout': int(config.get('timeout') or 22),
        'headers': config.get('headers') or {},
        'proxy_group': (config.get('proxy_group') or '').strip(),
        'continue_on_error': True,
        'validate_images': bool(config.get('validate_images', False)),
        'use_curl_cffi': True,
        'use_cloudscraper': True,
    }


# ==================== Task Template Routes（须在 /api/tasks/<task_id> 之前注册）====================

@app.route('/api/tasks/templates', methods=['GET'])
@auth_service.login_required
def task_template_list():
    try:
        category = request.args.get('category', '', type=str)
        favorite_only = request.args.get('favorite_only', '0') in ('1', 'true', 'True')
        templates = task_db.get_templates(
            user_id=request.user_id,
            category=category.strip(),
            favorite_only=favorite_only
        )
        for template in templates:
            format_template_for_api(template)

        return jsonify({'success': True, 'data': templates}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取模板列表失败', 'code': 'TEMPLATE_LIST_FAILED', 'error': str(e)
        }), 500


@app.route('/api/tasks/templates', methods=['POST'])
@auth_service.login_required
def task_template_create():
    try:
        data = request.get_json() or {}
        name = (data.get('name') or '').strip()
        description = (data.get('description') or '').strip()
        category = (data.get('category') or 'general').strip()
        is_favorite = bool(data.get('is_favorite'))
        config = _normalize_template_config(data.get('config') or {})

        if not name:
            return jsonify({
                'success': False, 'message': '请输入模板名称', 'code': 'MISSING_NAME'
            }), 400

        template_id, err = task_db.create_template(
            name=name,
            description=description,
            config=config,
            user_id=request.user_id,
            category=category,
            is_favorite=is_favorite
        )
        if err:
            return jsonify({
                'success': False, 'message': err, 'code': 'TEMPLATE_CREATE_FAILED'
            }), 400

        return jsonify({
            'success': True, 'message': '创建模板成功', 'data': {'template_id': template_id}
        }), 201

    except Exception as e:
        return jsonify({
            'success': False, 'message': '创建模板失败', 'code': 'TEMPLATE_CREATE_FAILED', 'error': str(e)
        }), 500


@app.route('/api/tasks/templates/<template_id>/use', methods=['POST'])
@auth_service.login_required
def task_template_use(template_id):
    try:
        template = task_db.get_template_by_id(template_id, user_id=request.user_id)
        if not template:
            return jsonify({
                'success': False, 'message': '模板不存在', 'code': 'TEMPLATE_NOT_FOUND'
            }), 404

        task_db.increment_template_use_count(template_id, user_id=request.user_id)
        template = task_db.get_template_by_id(template_id, user_id=request.user_id)
        format_template_for_api(template)
        return jsonify({
            'success': True, 'message': '已应用模板', 'data': template
        }), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '应用模板失败', 'code': 'TEMPLATE_USE_FAILED', 'error': str(e)
        }), 500


@app.route('/api/tasks/templates/<template_id>/favorite', methods=['POST'])
@auth_service.login_required
def task_template_toggle_favorite(template_id):
    try:
        template = task_db.get_template_by_id(template_id, user_id=request.user_id)
        if not template:
            return jsonify({
                'success': False, 'message': '模板不存在', 'code': 'TEMPLATE_NOT_FOUND'
            }), 404

        new_fav = not bool(template.get('is_favorite'))
        success, msg = task_db.update_template(
            template_id, user_id=request.user_id, is_favorite=new_fav
        )
        if not success:
            return jsonify({
                'success': False, 'message': msg or '操作失败', 'code': 'TEMPLATE_FAVORITE_FAILED'
            }), 400

        return jsonify({
            'success': True,
            'message': '已设为常用模板' if new_fav else '已取消常用',
            'data': {'is_favorite': new_fav}
        }), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '操作失败', 'code': 'TEMPLATE_FAVORITE_FAILED', 'error': str(e)
        }), 500


@app.route('/api/tasks/templates/<template_id>', methods=['GET'])
@auth_service.login_required
def task_template_detail(template_id):
    try:
        template = task_db.get_template_by_id(template_id, user_id=request.user_id)

        if not template:
            return jsonify({
                'success': False, 'message': '模板不存在', 'code': 'TEMPLATE_NOT_FOUND'
            }), 404

        format_template_for_api(template)
        return jsonify({'success': True, 'data': template}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取模板详情失败', 'code': 'TEMPLATE_DETAIL_FAILED', 'error': str(e)
        }), 500


@app.route('/api/tasks/templates/<template_id>', methods=['PUT'])
@auth_service.login_required
def task_template_update(template_id):
    try:
        template = task_db.get_template_by_id(template_id, user_id=request.user_id)
        if not template:
            return jsonify({
                'success': False, 'message': '模板不存在', 'code': 'TEMPLATE_NOT_FOUND'
            }), 404

        data = request.get_json() or {}
        update_fields = {}
        if 'name' in data:
            name = (data.get('name') or '').strip()
            if not name:
                return jsonify({
                    'success': False, 'message': '请输入模板名称', 'code': 'MISSING_NAME'
                }), 400
            update_fields['name'] = name
        if 'description' in data:
            update_fields['description'] = (data.get('description') or '').strip()
        if 'category' in data:
            update_fields['category'] = (data.get('category') or 'general').strip()
        if 'is_favorite' in data:
            update_fields['is_favorite'] = bool(data.get('is_favorite'))
        if 'config' in data:
            update_fields['config'] = _normalize_template_config(data.get('config') or {})

        if not update_fields:
            return jsonify({
                'success': False, 'message': '没有可更新的字段', 'code': 'TEMPLATE_NOTHING_TO_UPDATE'
            }), 400

        success, msg = task_db.update_template(template_id, user_id=request.user_id, **update_fields)
        if not success:
            return jsonify({
                'success': False, 'message': msg or '更新模板失败', 'code': 'TEMPLATE_UPDATE_FAILED'
            }), 400

        updated = task_db.get_template_by_id(template_id, user_id=request.user_id)
        format_template_for_api(updated)
        return jsonify({
            'success': True, 'message': '更新模板成功', 'data': updated
        }), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '更新模板失败', 'code': 'TEMPLATE_UPDATE_FAILED', 'error': str(e)
        }), 500


@app.route('/api/tasks/templates/<template_id>', methods=['DELETE'])
@auth_service.login_required
def task_template_delete(template_id):
    try:
        template = task_db.get_template_by_id(template_id, user_id=request.user_id)
        if not template:
            return jsonify({
                'success': False, 'message': '模板不存在', 'code': 'TEMPLATE_NOT_FOUND'
            }), 404

        success, msg = task_db.delete_template(template_id, user_id=request.user_id)
        if not success:
            return jsonify({
                'success': False, 'message': msg or '删除模板失败', 'code': 'TEMPLATE_DELETE_FAILED'
            }), 400

        return jsonify({'success': True, 'message': '删除模板成功'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '删除模板失败', 'code': 'TEMPLATE_DELETE_FAILED', 'error': str(e)
        }), 500


@app.route('/api/tasks/<task_id>', methods=['GET'])
@auth_service.login_required
def task_detail(task_id):
    try:
        task = task_db.get_by_id(task_id, user_id=request.user_id)

        if not task:
            return jsonify({
                'success': False, 'message': '任务不存在', 'code': 'TASK_NOT_FOUND'
            }), 404

        format_task_for_api(task)

        task_db.touch_recent_task(request.user_id, task_id, action='view')

        # 合并爬虫引擎的实时状态
        engine_status = crawler_engine.get_status()
        task['crawler_status'] = engine_status

        return jsonify({'success': True, 'data': task}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取任务详情失败', 'code': 'TASK_DETAIL_FAILED', 'error': str(e)
        }), 500


@app.route('/api/tasks/<task_id>', methods=['PUT'])
@auth_service.login_required
def task_update(task_id):
    try:
        task = task_db.get_by_id(task_id, user_id=request.user_id)
        if not task:
            return jsonify({
                'success': False, 'message': '任务不存在', 'code': 'TASK_NOT_FOUND'
            }), 404

        data = request.get_json()
        name = data.get('name')
        config = data.get('config')
        
        # 准备更新字段
        update_fields = {}
        if name is not None:
            update_fields['name'] = name
        if config is not None:
            existing_cfg = task.get('config') or {}
            if isinstance(existing_cfg, str):
                try:
                    existing_cfg = json.loads(existing_cfg)
                except (json.JSONDecodeError, TypeError):
                    existing_cfg = {}
            if not isinstance(config, dict):
                config = {}
            merged = {**existing_cfg, **config}
            if '_last_execution' not in config and existing_cfg.get('_last_execution'):
                merged['_last_execution'] = existing_cfg['_last_execution']
            normalized = _normalize_template_config(merged)
            update_fields['config'] = normalized
            update_fields.update(_sync_task_columns_from_config(normalized))

        # 如果有更新字段则更新（配置保存不再写入「执行记录」，避免与真实运行混淆）
        if update_fields:
            task_db.update(task_id=task_id, **update_fields)

        return jsonify({'success': True, 'message': '更新任务成功'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '更新任务失败', 'code': 'TASK_UPDATE_FAILED', 'error': str(e)
        }), 500


@app.route('/api/tasks/<task_id>', methods=['DELETE'])
@auth_service.login_required
def task_delete(task_id):
    try:
        task = task_db.get_by_id(task_id, user_id=request.user_id)
        if not task:
            return jsonify({
                'success': False, 'message': '任务不存在', 'code': 'TASK_NOT_FOUND'
            }), 404

        task_db.delete(task_id, user_id=request.user_id)

        return jsonify({'success': True, 'message': '删除任务成功'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '删除任务失败', 'code': 'TASK_DELETE_FAILED', 'error': str(e)
        }), 500


@app.route('/api/tasks/<task_id>/start', methods=['POST'])
@auth_service.login_required
def task_start(task_id):
    """直接启动指定任务（任务复制由前端完成后再调用本接口）。"""
    try:
        task = task_db.get_by_id(task_id, user_id=request.user_id)
        if not task:
            return jsonify({
                'success': False, 'message': '任务不存在', 'code': 'TASK_NOT_FOUND'
            }), 404

        source_uid = int(task.get('user_id') or 0)
        if request.user_id and source_uid not in (0, int(request.user_id)):
            return jsonify({
                'success': False, 'message': '无权操作此任务', 'code': 'TASK_FORBIDDEN'
            }), 403

        task_db.touch_recent_task(request.user_id, task_id, action='start')

        config = task.get('config', {})
        if isinstance(config, str):
            try:
                config = json.loads(config)
            except (json.JSONDecodeError, TypeError):
                config = {}
        config = dict(config) if isinstance(config, dict) else {}
        config['last_run_started_at'] = now_utc_str()
        task_db.update_task(task_id, config=config)

        target_url = (config.get('target_url') or task.get('target_url') or '').strip()
        if not target_url:
            return jsonify({
                'success': False, 'message': '任务缺少目标 URL', 'code': 'MISSING_TARGET_URL'
            }), 400

        crawl_options = _build_crawl_options(config)
        result = crawler_engine.start(
            target_url,
            config.get('total_pages', 1),
            config.get('interval_seconds', 3),
            _save_crawled_data,
            config.get('crawl_mode', 'link'),
            task_id=task_id,
            crawl_options=crawl_options,
        )

        if isinstance(result, tuple):
            start_ok = result[0]
        else:
            start_ok = result
        if not start_ok:
            err_msg = result[1] if isinstance(result, tuple) and len(result) > 1 else '启动爬虫失败'
            task_db.update_task_status(task_id, 'FAILED')
            task_db.update_task_stats(task_id, 0, 0, 0, err_msg)
            system_db.add_log(
                level='ERROR', source='crawler',
                message=f'任务[{task_id}] 启动失败: {err_msg}',
                task_id=int(task_id) if str(task_id).isdigit() else task_id
            )
            return jsonify({
                'success': False, 'message': err_msg or '启动爬虫失败',
                'code': 'CRAWLER_START_FAILED'
            }), 400

        success, message = task_db.start_task(task_id, user_id=request.user_id)

        if success:
            system_db.add_log(
                level='INFO', source='crawler',
                message=f'任务[{task_id}] 开始执行: 目标={target_url[:100]}, 页数={config.get("total_pages", 1)}',
                task_id=task_id
            )

        return jsonify({
            'success': success,
            'message': message,
            'data': {'task_id': task_id},
        }), 200 if success else 400

    except Exception as e:
        return jsonify({
            'success': False, 'message': '启动任务失败', 'code': 'TASK_START_FAILED', 'error': str(e)
        }), 500


@app.route('/api/tasks/<task_id>/stop', methods=['POST'])
@auth_service.login_required
def task_stop(task_id):
    try:
        task = task_db.get_by_id(task_id, user_id=request.user_id)
        if not task:
            return jsonify({
                'success': False, 'message': '任务不存在', 'code': 'TASK_NOT_FOUND'
            }), 404

        crawler_engine.stop()

        success, message = task_db.stop_task(task_id, user_id=request.user_id)

        return jsonify({'success': success, 'message': message}), 200 if success else 400

    except Exception as e:
        return jsonify({
            'success': False, 'message': '停止任务失败', 'code': 'TASK_STOP_FAILED', 'error': str(e)
        }), 500


@app.route('/api/tasks/<task_id>/executions', methods=['GET'])
@auth_service.login_required
def task_executions(task_id):
    """仅返回任务启动运行产生的执行记录（不含编辑配置产生的版本）"""
    try:
        task = task_db.get_by_id(task_id, user_id=request.user_id)
        if not task:
            return jsonify({
                'success': False, 'message': '任务不存在', 'code': 'TASK_NOT_FOUND'
            }), 404

        records = task_db.get_task_executions(task_id)
        format_rows_datetimes(records, 'created_at')
        return jsonify({'success': True, 'data': records}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取执行记录失败', 'code': 'TASK_EXECUTIONS_FAILED', 'error': str(e)
        }), 500


@app.route('/api/tasks/<task_id>/versions', methods=['GET'])
@auth_service.login_required
def task_versions(task_id):
    try:
        task = task_db.get_by_id(task_id, user_id=request.user_id)
        if not task:
            return jsonify({
                'success': False, 'message': '任务不存在', 'code': 'TASK_NOT_FOUND'
            }), 404

        versions = task_db.get_versions(task_id, user_id=request.user_id)
        format_rows_datetimes(versions, 'created_at')

        return jsonify({'success': True, 'data': versions}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取版本列表失败', 'code': 'VERSION_LIST_FAILED', 'error': str(e)
        }), 500


@app.route('/api/tasks/<task_id>/versions/rollback', methods=['POST'])
@auth_service.login_required
def task_rollback(task_id):
    try:
        data = request.get_json()
        version_id = data.get('version_id')

        if not version_id:
            return jsonify({
                'success': False, 'message': '请指定要回滚的版本', 'code': 'MISSING_VERSION'
            }), 400

        task = task_db.get_by_id(task_id, user_id=request.user_id)
        if not task:
            return jsonify({
                'success': False, 'message': '任务不存在', 'code': 'TASK_NOT_FOUND'
            }), 404

        success, message = task_db.rollback_version(task_id, version_id, user_id=request.user_id)

        return jsonify({'success': success, 'message': message}), 200 if success else 400

    except Exception as e:
        return jsonify({
            'success': False, 'message': '版本回滚失败', 'code': 'ROLLBACK_FAILED', 'error': str(e)
        }), 500


@app.route('/api/tasks/favorites', methods=['GET'])
@auth_service.login_required
def task_favorites():
    try:
        favorites = task_db.get_favorites(user_id=request.user_id)
        for task in favorites:
            format_task_for_api(task)

        return jsonify({'success': True, 'data': favorites}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取收藏列表失败', 'code': 'FAVORITES_FAILED', 'error': str(e)
        }), 500


@app.route('/api/tasks/<task_id>/favorite', methods=['POST'])
@auth_service.login_required
def task_add_favorite(task_id):
    try:
        task = task_db.get_by_id(task_id, user_id=request.user_id)
        if not task:
            return jsonify({
                'success': False, 'message': '任务不存在', 'code': 'TASK_NOT_FOUND'
            }), 404

        task_db.add_favorite(request.user_id, task_id)

        return jsonify({'success': True, 'message': '已加入收藏'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '收藏失败', 'code': 'FAVORITE_ADD_FAILED', 'error': str(e)
        }), 500


@app.route('/api/tasks/<task_id>/favorite', methods=['DELETE'])
@auth_service.login_required
def task_remove_favorite(task_id):
    try:
        task = task_db.get_by_id(task_id, user_id=request.user_id)
        if not task:
            return jsonify({
                'success': False, 'message': '任务不存在', 'code': 'TASK_NOT_FOUND'
            }), 404

        task_db.remove_favorite(request.user_id, task_id)

        return jsonify({'success': True, 'message': '已取消收藏'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '取消收藏失败', 'code': 'FAVORITE_REMOVE_FAILED', 'error': str(e)
        }), 500


# ==================== Alert Routes ====================

@app.route('/api/alerts/rules', methods=['GET'])
@auth_service.login_required
def alert_rule_list():
    try:
        rules = alert_db.get_rules(user_id=request.user_id)

        return jsonify({'success': True, 'data': rules}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取告警规则失败', 'code': 'ALERT_RULE_LIST_FAILED', 'error': str(e)
        }), 500


@app.route('/api/alerts/rules', methods=['POST'])
@auth_service.login_required
def alert_rule_create():
    try:
        data = request.get_json()
        name = (data.get('name') or '').strip()
        rule_type = (data.get('rule_type') or '').strip()
        condition = data.get('condition', {})
        actions = data.get('actions', [])
        is_enabled = data.get('is_enabled', True)

        if not name:
            return jsonify({
                'success': False, 'message': '请输入规则名称', 'code': 'MISSING_NAME'
            }), 400

        rule_id = alert_db.create_rule(
            user_id=request.user_id,
            name=name,
            rule_type=rule_type,
            condition=condition,
            actions=actions,
            is_enabled=is_enabled
        )

        return jsonify({
            'success': True, 'message': '创建告警规则成功', 'data': {'rule_id': rule_id}
        }), 201

    except Exception as e:
        return jsonify({
            'success': False, 'message': '创建告警规则失败', 'code': 'ALERT_RULE_CREATE_FAILED', 'error': str(e)
        }), 500


@app.route('/api/alerts/rules/<rule_id>', methods=['PUT'])
@auth_service.login_required
def alert_rule_update(rule_id):
    try:
        rule = alert_db.get_rule_by_id(rule_id, user_id=request.user_id)
        if not rule:
            return jsonify({
                'success': False, 'message': '规则不存在', 'code': 'RULE_NOT_FOUND'
            }), 404

        data = request.get_json()
        name = data.get('name')
        rule_type = data.get('rule_type')
        condition = data.get('condition')
        actions = data.get('actions')
        is_enabled = data.get('is_enabled')

        alert_db.update_rule(
            rule_id=rule_id,
            name=name,
            rule_type=rule_type,
            condition=condition,
            actions=actions,
            is_enabled=is_enabled,
            user_id=request.user_id
        )

        return jsonify({'success': True, 'message': '更新告警规则成功'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '更新告警规则失败', 'code': 'ALERT_RULE_UPDATE_FAILED', 'error': str(e)
        }), 500


@app.route('/api/alerts/rules/<rule_id>', methods=['DELETE'])
@auth_service.login_required
def alert_rule_delete(rule_id):
    try:
        rule = alert_db.get_rule_by_id(rule_id, user_id=request.user_id)
        if not rule:
            return jsonify({
                'success': False, 'message': '规则不存在', 'code': 'RULE_NOT_FOUND'
            }), 404

        alert_db.delete_rule(rule_id, user_id=request.user_id)

        return jsonify({'success': True, 'message': '删除告警规则成功'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '删除告警规则失败', 'code': 'ALERT_RULE_DELETE_FAILED', 'error': str(e)
        }), 500


@app.route('/api/alerts', methods=['GET'])
@auth_service.login_required
def alert_list():
    try:
        alert_type = request.args.get('type', '', type=str)
        is_read = request.args.get('is_read', None, type=str)
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)

        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        if is_read is not None:
            is_read = is_read.lower() == 'true'

        alerts, total = alert_db.get_list(
            user_id=request.user_id,
            alert_type=alert_type,
            is_read=is_read,
            page=page,
            page_size=page_size
        )

        return jsonify({
            'success': True,
            'data': {
                'list': alerts,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取告警列表失败', 'code': 'ALERT_LIST_FAILED', 'error': str(e)
        }), 500


@app.route('/api/alerts/<alert_id>/read', methods=['PUT'])
@auth_service.login_required
def alert_mark_read(alert_id):
    try:
        alert_db.mark_as_read(alert_id, user_id=request.user_id)

        return jsonify({'success': True, 'message': '已标记为已读'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '标记已读失败', 'code': 'ALERT_MARK_READ_FAILED', 'error': str(e)
        }), 500


@app.route('/api/alerts/read-all', methods=['PUT'])
@auth_service.login_required
def alert_mark_all_read():
    try:
        alert_db.mark_all_as_read(user_id=request.user_id)

        return jsonify({'success': True, 'message': '已全部标记为已读'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '全部标记已读失败', 'code': 'ALERT_MARK_ALL_FAILED', 'error': str(e)
        }), 500


@app.route('/api/alerts/unread-count', methods=['GET'])
@auth_service.login_required
def alert_unread_count():
    try:
        count = alert_db.get_unread_count(user_id=request.user_id)

        return jsonify({'success': True, 'data': {'count': count}}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取未读数量失败', 'code': 'UNREAD_COUNT_FAILED', 'error': str(e)
        }), 500


# ==================== Data Management Routes ====================

@app.route('/api/tasks/<task_id>/data-summary', methods=['GET'])
@auth_service.login_required
def task_data_summary(task_id):
    """获取任务的数据概览统计"""
    try:
        task = task_db.get_by_id(task_id, user_id=request.user_id)
        if not task:
            return jsonify({'success': False, 'message': '任务不存在', 'code': 'TASK_NOT_FOUND'}), 404

        config = task.get('config') or {}
        if isinstance(config, str):
            try:
                config = json.loads(config)
            except (json.JSONDecodeError, TypeError):
                config = {}

        latest_only = request.args.get('latest_only', '1') in ('1', 'true', 'True')
        since_utc = config.get('last_run_started_at') if latest_only else None

        stats = crawler_db.get_task_data_stats(task_id, since=since_utc)
        all_stats = crawler_db.get_task_data_stats(task_id, since=None) if since_utc else stats

        return jsonify({
            'success': True,
            'data': {
                'task_id': task_id,
                'task_name': task.get('name', ''),
                'total_count': stats['total_count'],
                'all_time_count': all_stats['total_count'],
                'today_count': stats['total_count'] if since_utc else stats['total_count'],
                'type_distribution': stats['type_distribution'],
                'last_collected_at': stats['last_collected_at'],
                'last_run_started_at': format_api_datetime(config.get('last_run_started_at')),
                'since': since_utc,
                'latest_only': latest_only,
                'data_count': task.get('data_count', 0),
                'execution_time': task.get('execution_time', 0),
                'success_rate': float(task.get('success_rate') or 0),
                'task_status': (task.get('status') or '').lower(),
                'error_message': task.get('error_message') or '',
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': '获取数据概览失败', 'error': str(e)}), 500


@app.route('/api/data', methods=['GET'])
@auth_service.login_required
def get_data_list():
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        keyword = request.args.get('keyword', '', type=str)
        task_id = request.args.get('task_id', '', type=str)
        data_type = request.args.get('type', '', type=str)
        date_from = request.args.get('date_from', '', type=str)
        date_to = request.args.get('date_to', '', type=str)
        sort_field = request.args.get('sort_field', '', type=str)
        sort_order = request.args.get('sort_order', 'desc', type=str)
        since = request.args.get('since', '', type=str).strip() or None
        if since:
            parsed_since = parse_to_utc_naive(since)
            if parsed_since:
                since = parsed_since.strftime(API_DATETIME_FORMAT)

        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        rows, total = crawler_db.get_list(
            page=page,
            page_size=page_size,
            keyword=keyword.strip(),
            task_id=int(task_id) if task_id else None,
            data_type=data_type.strip() if data_type else None,
            date_from=date_from.strip() if date_from else None,
            date_to=date_to.strip() if date_to else None,
            sort_field=sort_field.strip() if sort_field else None,
            sort_order=sort_order,
            since=since,
        )

        return jsonify({
            'success': True,
            'data': {
                'list': rows,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': '获取数据列表失败', 'error': str(e)}), 500


@app.route('/api/data/<int:record_id>', methods=['DELETE'])
@auth_service.login_required
def delete_data_record(record_id):
    try:
        success, msg = crawler_db.delete_by_id(record_id)
        if not success:
            return jsonify({
                'success': False, 'message': msg or '删除失败', 'code': 'DATA_DELETE_FAILED'
            }), 404
        return jsonify({'success': True, 'message': '删除成功'}), 200
    except Exception as e:
        return jsonify({
            'success': False, 'message': '删除失败', 'code': 'DATA_DELETE_FAILED', 'error': str(e)
        }), 500


@app.route('/api/data/batch-delete', methods=['POST'])
@auth_service.login_required
def batch_delete_data_records():
    try:
        data = request.get_json() or {}
        ids = data.get('ids', [])
        if not isinstance(ids, list) or not ids:
            return jsonify({
                'success': False, 'message': '请选择要删除的数据', 'code': 'MISSING_IDS'
            }), 400
        try:
            id_list = [int(i) for i in ids]
        except (TypeError, ValueError):
            return jsonify({
                'success': False, 'message': '无效的数据ID', 'code': 'INVALID_IDS'
            }), 400

        deleted, err = crawler_db.delete_by_ids(id_list)
        if err:
            return jsonify({
                'success': False, 'message': err, 'code': 'DATA_BATCH_DELETE_FAILED'
            }), 400

        return jsonify({
            'success': True,
            'message': f'已删除 {deleted} 条数据',
            'data': {'deleted': deleted}
        }), 200
    except Exception as e:
        return jsonify({
            'success': False, 'message': '批量删除失败', 'code': 'DATA_BATCH_DELETE_FAILED', 'error': str(e)
        }), 500


@app.route('/api/data/preview', methods=['GET'])
@auth_service.login_required
def data_preview():
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        keyword = request.args.get('keyword', '', type=str)

        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        rows, total = crawler_db.get_list(page=page, page_size=page_size, keyword=keyword)

        return jsonify({
            'success': True,
            'data': {
                'list': rows,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取数据预览失败', 'code': 'DATA_PREVIEW_FAILED', 'error': str(e)
        }), 500


def _normalize_clean_operations(data):
    ops = data.get('operations') or []
    if not ops and data.get('operation'):
        op = data.get('operation')
        if op == 'format_convert':
            ops = ['format_convert']
        else:
            ops = [op]
    return ops if isinstance(ops, list) else []


def _field_nonempty(item, field):
    if not isinstance(item, dict):
        return False
    val = item.get(field)
    if val is None:
        return False
    if isinstance(val, str):
        return bool(val.strip())
    return bool(val)


def _apply_format_convert(items, field, fmt):
    result = []
    for item in items:
        if not isinstance(item, dict):
            result.append(item)
            continue
        row = dict(item)
        if field and field in row:
            val = row[field]
            if fmt in ('trim', 'format_fields') and isinstance(val, str):
                row[field] = val.strip()
            elif fmt == 'lowercase' and isinstance(val, str):
                row[field] = val.lower()
            elif fmt == 'uppercase' and isinstance(val, str):
                row[field] = val.upper()
            elif fmt in ('timestamp', 'timestamp_to_date'):
                try:
                    if isinstance(val, (int, float)) or (isinstance(val, str) and val.isdigit()):
                        ts = int(float(val))
                        if ts > 1e12:
                            ts = ts // 1000
                        row[field] = datetime.utcfromtimestamp(ts).strftime(API_DATETIME_FORMAT)
                    elif isinstance(val, str) and val.strip():
                        row[field] = val.strip()
                except (ValueError, OSError):
                    pass
        elif not field:
            for k, v in row.items():
                if isinstance(v, str) and fmt in ('trim', 'format_fields'):
                    row[k] = v.strip()
        result.append(row)
    return result


@app.route('/api/data/clean', methods=['POST'])
@auth_service.login_required
def data_clean():
    try:
        data = request.get_json() or {}
        items = data.get('data', [])
        operations = _normalize_clean_operations(data)
        save_to_db = data.get('save_to_db', False)
        filter_fields = data.get('fields') or []
        format_field = data.get('field', '')
        format_type = data.get('format', 'trim')

        if not isinstance(items, list):
            return jsonify({
                'success': False, 'message': '请提供有效的数据', 'code': 'INVALID_DATA'
            }), 400

        cleaned = list(items)

        for op in operations:
            if op == 'deduplicate':
                seen = set()
                unique = []
                for item in cleaned:
                    item_key = json.dumps(item, sort_keys=True, ensure_ascii=False, default=str)
                    if item_key not in seen:
                        seen.add(item_key)
                        unique.append(item)
                cleaned = unique
            elif op == 'filter_empty':
                if filter_fields:
                    cleaned = [
                        item for item in cleaned
                        if all(_field_nonempty(item, f) for f in filter_fields)
                    ]
                else:
                    cleaned = [
                        item for item in cleaned
                        if item and any(v for v in item.values() if v not in (None, '', []))
                    ]
            elif op in ('format_fields', 'format_convert'):
                fmt = format_type
                if fmt == 'timestamp':
                    fmt = 'timestamp_to_date'
                cleaned = _apply_format_convert(cleaned, format_field, fmt)

        if save_to_db:
            has_ids = any(isinstance(i, dict) and i.get('id') for i in cleaned)
            if has_ids or not operations:
                ok, _ = crawler_db.bulk_upsert(cleaned)
                if not ok:
                    return jsonify({
                        'success': False, 'message': '保存到数据库失败', 'code': 'DATA_SAVE_FAILED'
                    }), 500
            else:
                crawler_db.replace_all(cleaned)

        payload = {
            'original_count': len(items),
            'cleaned_count': len(cleaned),
            'items': cleaned,
            'list': cleaned,
        }
        return jsonify({
            'success': True,
            'message': '数据清洗完成' + ('并已保存到数据库' if save_to_db else ''),
            'data': payload
        }), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '数据清洗失败', 'code': 'DATA_CLEAN_FAILED', 'error': str(e)
        }), 500


@app.route('/api/data/export', methods=['GET'])
@auth_service.login_required
def data_export():
    try:
        export_format = request.args.get('format', 'csv', type=str).lower()
        fields_str = request.args.get('fields', '', type=str)
        date_from = request.args.get('date_from', '', type=str) or None
        date_to = request.args.get('date_to', '', type=str) or None
        task_id = request.args.get('task_id', '', type=str)
        task_id = int(task_id) if task_id else None

        items = crawler_db.get_export_list(
            task_id=task_id, date_from=date_from, date_to=date_to
        )

        if not items:
            return jsonify({
                'success': False, 'message': '暂无数据可导出', 'code': 'NO_DATA'
            }), 400

        fields = [f.strip() for f in fields_str.split(',') if f.strip()] if fields_str else (
            ['id', 'title', 'link', 'content', 'source_url', 'page_number', 'collected_at']
        )

        if export_format == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(fields)
            for item in items:
                writer.writerow([item.get(f, '') for f in fields])
            output.seek(0)

            return Response(
                output.getvalue().encode('utf-8-sig'),
                mimetype='text/csv',
                headers={
                    'Content-Disposition': 'attachment; filename=data_export.csv',
                    'Content-Type': 'text/csv; charset=utf-8-sig'
                }
            )

        elif export_format == 'json':
            result = [{f: item.get(f, '') for f in fields} for item in items]
            output = json.dumps(result, ensure_ascii=False, indent=2)

            return Response(
                output.encode('utf-8'),
                mimetype='application/json',
                headers={
                    'Content-Disposition': 'attachment; filename=data_export.json',
                    'Content-Type': 'application/json; charset=utf-8'
                }
            )

        elif export_format == 'excel':
            try:
                from openpyxl import Workbook
                from io import BytesIO

                wb = Workbook()
                ws = wb.active
                ws.title = '爬取数据'

                if fields:
                    ws.append(fields)
                for item in items:
                    ws.append([item.get(f, '') for f in fields])

                output = BytesIO()
                wb.save(output)
                output.seek(0)

                return Response(
                    output.getvalue(),
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    headers={
                        'Content-Disposition': 'attachment; filename=data_export.xlsx',
                        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    }
                )
            except ImportError:
                return jsonify({
                    'success': False, 'message': 'Excel导出需要安装openpyxl库', 'code': 'EXCEL_NOT_SUPPORTED'
                }), 400

        else:
            return jsonify({
                'success': False, 'message': f'不支持的导出格式: {export_format}', 'code': 'INVALID_FORMAT'
            }), 400

    except Exception as e:
        return jsonify({
            'success': False, 'message': '导出数据失败', 'code': 'DATA_EXPORT_FAILED', 'error': str(e)
        }), 500


@app.route('/api/data/auto-write-config', methods=['GET', 'POST'])
@auth_service.login_required
def data_auto_write_config():
    try:
        if request.method == 'GET':
            row = crawler_db.get_auto_write_config(request.user_id)
            return jsonify({'success': True, 'data': row or {}}), 200

        data = request.get_json() or {}
        test_only = data.get('test_only', False)
        target_type = data.get('target_type') or data.get('db_type') or 'mysql'
        target_config = data.get('target_config') or {
            'db_type': data.get('db_type', target_type),
            'host': data.get('host'),
            'port': data.get('port'),
            'user': data.get('user'),
            'password': data.get('password'),
            'database': data.get('database'),
            'table': data.get('table'),
            'auto_write': data.get('auto_write'),
        }

        ok, err = crawler_db.test_external_db_connection(target_config)
        if test_only:
            if not ok:
                return jsonify({
                    'success': False, 'message': f'连接测试失败: {err}', 'code': 'DB_TEST_FAILED'
                }), 400
            return jsonify({'success': True, 'message': '数据库连接测试成功'}), 200

        if not target_config.get('host'):
            return jsonify({
                'success': False, 'message': '请填写主机地址', 'code': 'MISSING_HOST'
            }), 400

        if not ok:
            return jsonify({
                'success': False, 'message': f'连接测试失败: {err}', 'code': 'DB_TEST_FAILED'
            }), 400

        crawler_db.save_auto_write_config(
            user_id=request.user_id,
            target_type=target_type,
            target_config=target_config,
            enabled=data.get('auto_write', data.get('enabled')),
        )

        return jsonify({'success': True, 'message': '自动写入配置保存成功'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '保存配置失败', 'code': 'AUTO_WRITE_CONFIG_FAILED', 'error': str(e)
        }), 500


@app.route('/api/data/push-config', methods=['GET', 'POST'])
@auth_service.login_required
def data_push_config():
    try:
        if request.method == 'GET':
            row = crawler_db.get_push_config(request.user_id)
            return jsonify({'success': True, 'data': row or {}}), 200

        data = request.get_json() or {}
        push_types = []
        if data.get('push_email'):
            push_types.append('email')
        if data.get('push_wechat'):
            push_types.append('wechat')
        push_type = data.get('push_type') or (','.join(push_types) if push_types else 'mixed')
        push_config = data.get('push_config') or {
            'email': data.get('email_recipient', ''),
            'wechat_webhook': data.get('wechat_webhook', ''),
            'push_after_crawl': data.get('push_after_crawl', False),
            'push_daily': data.get('push_daily', False),
            'push_email': data.get('push_email', False),
            'push_wechat': data.get('push_wechat', False),
        }

        ok, err = crawler_db.save_push_config(
            user_id=request.user_id,
            push_type=push_type,
            push_config=push_config,
        )
        if not ok:
            return jsonify({
                'success': False, 'message': err or '保存失败', 'code': 'PUSH_CONFIG_FAILED'
            }), 500

        return jsonify({'success': True, 'message': '推送配置保存成功'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '保存推送配置失败', 'code': 'PUSH_CONFIG_FAILED', 'error': str(e)
        }), 500


# ==================== Proxy Routes ====================

@app.route('/api/proxy/list', methods=['GET'])
@auth_service.login_required
def proxy_list():
    try:
        proxies = proxy_db.get_proxies()

        return jsonify({'success': True, 'data': proxies, 'list': proxies}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取代理列表失败', 'code': 'PROXY_LIST_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/add', methods=['POST'])
@auth_service.login_required
def proxy_add():
    try:
        data = request.get_json() or {}
        host = (data.get('host') or data.get('ip') or '').strip()
        port = data.get('port')
        protocol = (data.get('protocol') or 'http').strip()
        username = (data.get('username') or '').strip()
        password = (data.get('password') or '').strip()

        if not host:
            return jsonify({
                'success': False, 'message': '请输入代理地址', 'code': 'MISSING_HOST'
            }), 400

        if not port:
            return jsonify({
                'success': False, 'message': '请输入代理端口', 'code': 'MISSING_PORT'
            }), 400

        proxy_id, err = proxy_db.add_proxy(
            ip=host,
            port=port,
            protocol=protocol
        )

        if err:
            return jsonify({
                'success': False, 'message': '添加代理失败', 'code': 'PROXY_ADD_FAILED', 'error': err
            }), 500

        _, probe_err, updated = proxy_db.probe_proxy(proxy_id)

        return jsonify({
            'success': True,
            'message': '添加代理成功' if not probe_err else '添加成功，但探测未通过',
            'data': {'proxy_id': proxy_id, 'proxy': updated}
        }), 201

    except Exception as e:
        return jsonify({
            'success': False, 'message': '添加代理失败', 'code': 'PROXY_ADD_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/<proxy_id>', methods=['DELETE'])
@auth_service.login_required
def proxy_delete(proxy_id):
    try:
        proxy_db.delete_proxy(proxy_id)

        return jsonify({'success': True, 'message': '删除代理成功'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '删除代理失败', 'code': 'PROXY_DELETE_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/<proxy_id>/refresh', methods=['POST'])
@auth_service.login_required
def proxy_refresh(proxy_id):
    try:
        ok, err, updated = proxy_db.probe_proxy(proxy_id)
        if not ok:
            return jsonify({
                'success': False, 'message': err or '刷新失败', 'code': 'PROXY_REFRESH_FAILED'
            }), 400
        return jsonify({
            'success': True, 'message': '代理检测完成', 'data': updated
        }), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '刷新代理失败', 'code': 'PROXY_REFRESH_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/groups', methods=['GET'])
@auth_service.login_required
def proxy_groups():
    try:
        groups = proxy_db.get_proxy_groups()

        return jsonify({'success': True, 'data': groups}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取代理组失败', 'code': 'PROXY_GROUP_LIST_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/groups', methods=['POST'])
@auth_service.login_required
def proxy_group_create():
    try:
        data = request.get_json()
        name = (data.get('name') or '').strip()
        description = (data.get('description') or '').strip()

        if not name:
            return jsonify({
                'success': False, 'message': '请输入组名称', 'code': 'MISSING_NAME'
            }), 400

        group_id, err = proxy_db.create_proxy_group(
            name=name,
            description=description
        )
        if err:
            return jsonify({
                'success': False, 'message': f'创建代理组失败: {err}', 'code': 'PROXY_GROUP_CREATE_FAILED'
            }), 500

        return jsonify({
            'success': True,
            'message': '创建代理组成功',
            'data': {'group_id': group_id, 'id': group_id}
        }), 201

    except Exception as e:
        return jsonify({
            'success': False, 'message': '创建代理组失败', 'code': 'PROXY_GROUP_CREATE_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/groups/<group_id>', methods=['DELETE'])
@auth_service.login_required
def proxy_group_delete(group_id):
    try:
        ok, err = proxy_db.delete_proxy_group(group_id)
        if not ok:
            return jsonify({
                'success': False, 'message': err or '删除失败', 'code': 'PROXY_GROUP_DELETE_FAILED'
            }), 500
        return jsonify({'success': True, 'message': '分组已删除'}), 200
    except Exception as e:
        return jsonify({
            'success': False, 'message': '删除分组失败', 'code': 'PROXY_GROUP_DELETE_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/groups/assign', methods=['POST'])
@auth_service.login_required
def proxy_group_assign():
    try:
        data = request.get_json()
        proxy_id = data.get('proxy_id')
        group_id = data.get('group_id')

        if not proxy_id or not group_id:
            return jsonify({
                'success': False, 'message': '请提供代理ID和组ID', 'code': 'MISSING_PARAMS'
            }), 400

        ok, err = proxy_db.assign_proxy_to_group(group_id, proxy_id)
        if not ok:
            return jsonify({
                'success': False, 'message': err or '代理分配失败', 'code': 'PROXY_ASSIGN_FAILED'
            }), 500

        return jsonify({'success': True, 'message': '代理分配成功'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '代理分配失败', 'code': 'PROXY_ASSIGN_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/groups/sync', methods=['POST'])
@auth_service.login_required
def proxy_group_sync_proxies_post():
    try:
        data = request.get_json() or {}
        group_id = data.get('group_id')
        proxy_ids = data.get('proxy_ids')
        if proxy_ids is None:
            proxy_ids = data.get('proxies') or []

        if not group_id:
            return jsonify({
                'success': False,
                'message': '请提供分组 ID',
                'code': 'MISSING_GROUP_ID',
            }), 400

        ok, err = proxy_db.sync_group_proxies(group_id, proxy_ids)
        if not ok:
            return jsonify({
                'success': False,
                'message': err or '同步分组代理失败',
                'code': 'PROXY_GROUP_SYNC_FAILED',
            }), 400

        group = next((g for g in proxy_db.get_proxy_groups() if str(g.get('id')) == str(group_id)), None)
        return jsonify({
            'success': True,
            'message': '分组代理已更新',
            'data': group,
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': '同步分组代理失败',
            'code': 'PROXY_GROUP_SYNC_FAILED',
            'error': str(e),
        }), 500


@app.route('/api/proxy/groups/<group_id>/proxies', methods=['PUT'])
@auth_service.login_required
def proxy_group_sync_proxies(group_id):
    try:
        data = request.get_json() or {}
        proxy_ids = data.get('proxy_ids')
        if proxy_ids is None:
            proxy_ids = data.get('proxies') or []

        ok, err = proxy_db.sync_group_proxies(group_id, proxy_ids)
        if not ok:
            return jsonify({
                'success': False,
                'message': err or '同步分组代理失败',
                'code': 'PROXY_GROUP_SYNC_FAILED',
            }), 400

        group = next((g for g in proxy_db.get_proxy_groups() if str(g.get('id')) == str(group_id)), None)
        return jsonify({
            'success': True,
            'message': '分组代理已更新',
            'data': group,
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': '同步分组代理失败',
            'code': 'PROXY_GROUP_SYNC_FAILED',
            'error': str(e),
        }), 500


@app.route('/api/proxy/blacklist', methods=['GET'])
@auth_service.login_required
def proxy_blacklist():
    try:
        items = proxy_db.get_blacklist()

        return jsonify({'success': True, 'data': items}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取黑名单失败', 'code': 'BLACKLIST_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/blacklist', methods=['POST'])
@auth_service.login_required
def proxy_blacklist_add():
    try:
        data = request.get_json() or {}
        target = (data.get('target') or data.get('url') or '').strip()
        reason = (data.get('reason') or '').strip()

        if not target:
            return jsonify({
                'success': False, 'message': '请输入黑名单目标', 'code': 'MISSING_TARGET'
            }), 400

        success, _ = proxy_db.add_blacklist(
            url=target,
            reason=reason
        )

        if not success:
            return jsonify({
                'success': False, 'message': '添加黑名单失败', 'code': 'BLACKLIST_ADD_FAILED'
            }), 500

        return jsonify({
            'success': True, 'message': '已加入黑名单'
        }), 201

    except Exception as e:
        return jsonify({
            'success': False, 'message': '加入黑名单失败', 'code': 'BLACKLIST_ADD_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/blacklist/<item_id>', methods=['DELETE'])
@auth_service.login_required
def proxy_blacklist_remove(item_id):
    try:
        proxy_db.remove_blacklist(item_id)

        return jsonify({'success': True, 'message': '已从黑名单移除'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '移除黑名单失败', 'code': 'BLACKLIST_REMOVE_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/whitelist', methods=['GET'])
@auth_service.login_required
def proxy_whitelist():
    try:
        items = proxy_db.get_whitelist()

        return jsonify({'success': True, 'data': items}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取白名单失败', 'code': 'WHITELIST_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/whitelist', methods=['POST'])
@auth_service.login_required
def proxy_whitelist_add():
    try:
        data = request.get_json() or {}
        target = (data.get('target') or data.get('url') or '').strip()
        reason = (data.get('reason') or '').strip()

        if not target:
            return jsonify({
                'success': False, 'message': '请输入白名单目标', 'code': 'MISSING_TARGET'
            }), 400

        success, _ = proxy_db.add_whitelist(
            url=target,
            reason=reason
        )
        if not success:
            return jsonify({
                'success': False, 'message': '添加白名单失败', 'code': 'WHITELIST_ADD_FAILED'
            }), 500

        return jsonify({
            'success': True, 'message': '已加入白名单'
        }), 201

    except Exception as e:
        return jsonify({
            'success': False, 'message': '加入白名单失败', 'code': 'WHITELIST_ADD_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/whitelist/<item_id>', methods=['DELETE'])
@auth_service.login_required
def proxy_whitelist_remove(item_id):
    try:
        proxy_db.remove_whitelist(item_id)

        return jsonify({'success': True, 'message': '已从白名单移除'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '移除白名单失败', 'code': 'WHITELIST_REMOVE_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/rate-limits', methods=['GET'])
@auth_service.login_required
def proxy_rate_limits():
    try:
        task_id = request.args.get('task_id', type=int)
        if task_id:
            limits = proxy_db.get_rate_limit(task_id)
            return jsonify({'success': True, 'data': limits}), 200
        limits = proxy_db.get_rate_limits_bundle()

        return jsonify({'success': True, 'data': limits}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取速率限制失败', 'code': 'RATE_LIMIT_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/rate-limits', methods=['POST'])
@auth_service.login_required
def proxy_rate_limit_set():
    try:
        data = request.get_json() or {}
        rpm = data.get('requests_per_minute') or data.get('max_requests')
        concurrent = data.get('concurrent_max') or data.get('time_window')
        task_id = data.get('task_id') or data.get('target_id')
        retry_count = data.get('retry_count', 3)

        if rpm is None or concurrent is None:
            return jsonify({
                'success': False, 'message': '请设置每分钟请求数与最大并发', 'code': 'MISSING_PARAMS'
            }), 400

        proxy_db.set_rate_limit(
            requests_per_minute=int(rpm),
            concurrent_max=int(concurrent),
            task_id=int(task_id) if task_id else None,
            retry_count=int(retry_count),
        )

        return jsonify({'success': True, 'message': '速率限制设置成功'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '设置速率限制失败', 'code': 'RATE_LIMIT_SET_FAILED', 'error': str(e)
        }), 500


# ==================== System Routes ====================

_runtime_config_cache = {'reloaded_at': None}


@app.route('/api/system/resources', methods=['GET'])
@auth_service.login_required
def system_resources():
    try:
        cpu_percent = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net_io = 0
        try:
            net = psutil.net_io_counters()
            if net:
                total = (net.bytes_sent + net.bytes_recv) or 1
                net_io = min(100, round((net.bytes_sent + net.bytes_recv) / (1024 * 1024 * 1024) * 10, 1))
        except Exception:
            net_io = 0

        return jsonify({
            'success': True,
            'data': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'network_io': net_io,
                'cpu': {
                    'percent': cpu_percent,
                    'cores': psutil.cpu_count(logical=True),
                    'physical_cores': psutil.cpu_count(logical=False)
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                    'free': memory.free
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                }
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取系统资源失败', 'code': 'RESOURCES_FAILED', 'error': str(e)
        }), 500


@app.route('/api/system/task-resources', methods=['GET'])
@auth_service.login_required
def system_task_resources():
    try:
        cpu_sys = psutil.cpu_percent(interval=0.1)
        mem_sys = psutil.virtual_memory().percent
        active_id = getattr(crawler_engine, '_task_id', None)
        rows, _ = task_db.get_task_list_with_favorites(
            user_id=request.user_id, page=1, page_size=20
        )
        result = []
        for t in rows:
            tid = t.get('id')
            status = (t.get('status') or 'idle').lower()
            if status == 'running' and tid == active_id:
                cpu = round(cpu_sys, 1)
                mem = round(mem_sys, 1)
            elif status == 'running':
                cpu = round(cpu_sys * 0.25, 1)
                mem = round(mem_sys * 0.15, 1)
            else:
                stats = crawler_db.get_task_data_stats(tid) if tid else {}
                load = min(25, int(stats.get('total_count', 0) // 50))
                cpu = load
                mem = load
            result.append({
                'id': tid,
                'name': t.get('name') or str(tid),
                'cpu': cpu,
                'mem': mem,
                'status': status,
            })
        result.sort(key=lambda x: x['cpu'], reverse=True)
        return jsonify({'success': True, 'data': result}), 200
    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取任务资源失败', 'code': 'TASK_RESOURCES_FAILED', 'error': str(e)
        }), 500


@app.route('/api/system/reload-config', methods=['POST'])
@auth_service.login_required
def system_reload_config():
    try:
        _runtime_config_cache['reloaded_at'] = format_api_datetime(now_utc())
        proxy_db.connect()
        system_db.connect()
        crawler_db.connect()
        system_db.add_log(level='INFO', source='system', message='运行时配置已从数据库重新加载')
        return jsonify({'success': True, 'message': '配置已刷新'}), 200
    except Exception as e:
        return jsonify({
            'success': False, 'message': '刷新配置失败', 'code': 'RELOAD_CONFIG_FAILED', 'error': str(e)
        }), 500


@app.route('/api/system/restart-crawlers', methods=['POST'])
@auth_service.login_required
def system_restart_crawlers():
    try:
        crawler_engine.stop()
        crawler_engine.reset()
        conn = None
        try:
            import pymysql as _pymysql
            from db_settings import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_CHARSET, DB_CA_PATH
            conn = _pymysql.connect(
                host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD,
                database=DB_NAME, charset=DB_CHARSET, ssl_ca=DB_CA_PATH,
                ssl_verify_cert=True, ssl_verify_identity=True,
            )
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE `crawler_tasks` SET `status`='STOPPED' WHERE UPPER(`status`)='RUNNING'"
                )
            conn.commit()
        except Exception as db_err:
            print(f"[restart-crawlers] DB update: {db_err}")
        finally:
            if conn:
                conn.close()
        system_db.add_log(level='WARNING', source='system', message='爬虫服务已重启（运行中任务已停止）')
        return jsonify({'success': True, 'message': '爬虫服务已重启'}), 200
    except Exception as e:
        return jsonify({
            'success': False, 'message': '重启爬虫服务失败', 'code': 'RESTART_CRAWLERS_FAILED', 'error': str(e)
        }), 500


@app.route('/api/system/logs', methods=['GET'])
@auth_service.login_required
def system_logs():
    try:
        level = request.args.get('level', '', type=str)
        task_id = request.args.get('task_id', '', type=str)
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 50, type=int)

        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 50

        keyword = request.args.get('keyword', '', type=str)
        date_from = request.args.get('date_from', '', type=str) or None
        date_to = request.args.get('date_to', '', type=str) or None

        logs, total = system_db.get_logs(
            level=level,
            task_id=int(task_id) if task_id else None,
            page=page,
            page_size=page_size,
            keyword=keyword,
            date_from=date_from,
            date_to=date_to,
        )

        return jsonify({
            'success': True,
            'data': {
                'list': logs,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取系统日志失败', 'code': 'LOGS_FAILED', 'error': str(e)
        }), 500


@app.route('/api/system/logs/clear', methods=['POST'])
@auth_service.login_required
def system_logs_clear():
    try:
        data = request.get_json(silent=True) or {}
        days = data.get('days', 30)

        if not isinstance(days, int) or days < 0:
            return jsonify({
                'success': False, 'message': '请提供有效的天数（大于等于0的整数）', 'code': 'INVALID_DAYS'
            }), 400

        success, msg = system_db.clear_logs(days)
        if not success:
            return jsonify({'success': False, 'message': '清理日志失败', 'error': msg}), 500

        return jsonify({'success': True, 'message': msg}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '清理日志失败', 'code': 'LOGS_CLEAR_FAILED', 'error': str(e)
        }), 500


@app.route('/api/system/logs/export', methods=['GET'])
@auth_service.login_required
def system_logs_export():
    try:
        logs, _ = system_db.get_logs(page=1, page_size=10000)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['时间', '级别', '来源', '消息'])
        for log in logs:
            writer.writerow([
                log.get('created_at', ''),
                log.get('level', ''),
                log.get('source', ''),
                log.get('message', '')
            ])
        output.seek(0)

        return Response(
            output.getvalue().encode('utf-8-sig'),
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=system_logs.csv',
                'Content-Type': 'text/csv; charset=utf-8-sig'
            }
        )

    except Exception as e:
        return jsonify({
            'success': False, 'message': '日志导出失败', 'code': 'LOGS_EXPORT_FAILED', 'error': str(e)
        }), 500


@app.route('/api/system/settings', methods=['GET'])
@auth_service.login_required
def system_settings():
    try:
        settings = system_db.get_all_settings()

        return jsonify({'success': True, 'data': settings}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取系统设置失败', 'code': 'SETTINGS_FAILED', 'error': str(e)
        }), 500


@app.route('/api/system/settings/batch', methods=['GET'])
@auth_service.login_required
def system_settings_batch_get():
    try:
        rows = system_db.get_all_settings()
        data = {}
        for row in rows:
            key = row['key']
            val = row['value']
            try:
                parsed = json.loads(val)
                data[key] = parsed
            except (json.JSONDecodeError, TypeError):
                data[key] = val
        return jsonify({'success': True, 'data': data}), 200
    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取批量设置失败', 'code': 'SETTINGS_BATCH_FAILED', 'error': str(e)
        }), 500


@app.route('/api/system/settings/batch', methods=['PUT'])
@auth_service.login_required
def system_settings_batch_save():
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({
                'success': False, 'message': '请提供有效的设置数据', 'code': 'INVALID_SETTINGS'
            }), 400

        success, count = system_db.save_settings_batch(data)
        if not success:
            return jsonify({'success': False, 'message': '保存设置失败', 'error': count}), 500

        return jsonify({'success': True, 'message': f'成功保存 {count} 项设置', 'data': {'count': count}}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '保存批量设置失败', 'code': 'SETTINGS_BATCH_SAVE_FAILED', 'error': str(e)
        }), 500


@app.route('/api/system/settings/<key>', methods=['PUT'])
@auth_service.login_required
def system_setting_update(key):
    try:
        data = request.get_json()
        value = data.get('value')

        if value is None:
            return jsonify({
                'success': False, 'message': '请提供设置值', 'code': 'MISSING_VALUE'
            }), 400

        system_db.set_setting(key=key, value=value)

        return jsonify({'success': True, 'message': '设置更新成功'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '更新设置失败', 'code': 'SETTING_UPDATE_FAILED', 'error': str(e)
        }), 500


@app.route('/api/system/user/preferences', methods=['GET'])
@auth_service.login_required
def user_preferences_get():
    try:
        preferences = system_db.get_user_preferences(user_id=request.user_id)
        if preferences:
            format_row_datetimes(preferences, 'created_at')

        return jsonify({'success': True, 'data': preferences}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取用户偏好失败', 'code': 'PREFERENCES_FAILED', 'error': str(e)
        }), 500


@app.route('/api/system/user/preferences', methods=['PUT'])
@auth_service.login_required
def user_preferences_save():
    try:
        data = request.get_json()

        # 将 preferences JSON 存储到数据库
        import json
        prefs_json = json.dumps(data) if data else '{}'
        system_db.save_user_preferences(
            user_id=request.user_id,
            notification_config=prefs_json
        )

        return jsonify({'success': True, 'message': '偏好设置保存成功'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '保存偏好设置失败', 'code': 'PREFERENCES_SAVE_FAILED', 'error': str(e)
        }), 500


@app.route('/api/user/theme', methods=['GET'])
@auth_service.login_required
def user_theme_get():
    try:
        theme_name = system_db.get_theme(request.user_id)
        return jsonify({'success': True, 'data': {'theme': theme_name}}), 200
    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取主题失败', 'code': 'THEME_GET_FAILED', 'error': str(e)
        }), 500


@app.route('/api/user/theme', methods=['PUT'])
@auth_service.login_required
def user_theme_save():
    try:
        data = request.get_json()
        theme_name = data.get('theme', 'default')

        valid_themes = ['pure-black', 'default', 'space-gray', 'ice-blue', 'night-green', 'purple-gold', 'cyber-aurora']
        if theme_name not in valid_themes:
            return jsonify({
                'success': False, 'message': '无效的主题名称', 'code': 'INVALID_THEME'
            }), 400

        success, msg = system_db.save_theme(request.user_id, theme_name)
        if not success:
            return jsonify({'success': False, 'message': '保存主题失败', 'error': msg}), 500

        return jsonify({'success': True, 'message': '主题已切换', 'data': {'theme': theme_name}}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '保存主题失败', 'code': 'THEME_SAVE_FAILED', 'error': str(e)
        }), 500


@app.route('/api/system/dashboard-stats', methods=['GET'])
@auth_service.login_required
def system_dashboard_stats():
    try:
        tz_name = get_effective_timezone(get_request_timezone())
        today_stats = crawler_db.get_today_stats(tz_name=tz_name)
        today_collected = today_stats.get('today_total', 0)
        today_trend = today_stats.get('hourly_breakdown', [0] * 24)

        success_tasks = task_db.get_count_by_status('completed') if hasattr(task_db, 'get_count_by_status') else 0
        failed_tasks = task_db.get_count_by_status('failed') if hasattr(task_db, 'get_count_by_status') else 0
        running_tasks = task_db.get_count_by_status('running') if hasattr(task_db, 'get_count_by_status') else 0
        pending_tasks = task_db.get_count_by_status('pending') if hasattr(task_db, 'get_count_by_status') else 0
        total_tasks = task_db.count_by_user(request.user_id) if hasattr(task_db, 'count_by_user') else 0

        return jsonify({
            'success': True,
            'data': {
                'today_collected': today_collected,
                'total_tasks': total_tasks,
                'success_tasks': success_tasks,
                'failed_tasks': failed_tasks,
                'running_tasks': running_tasks,
                'pending_tasks': pending_tasks,
                'system_status': 'normal',
                'today_trend': today_trend,
                'hour_labels': build_local_hour_labels(tz_name),
                'stats_time': format_api_datetime(now_utc()),
                'timezone': tz_name,
                'timezone_offset': today_stats.get('timezone_offset', '+08:00'),
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取仪表盘统计失败', 'code': 'DASHBOARD_FAILED', 'error': str(e)
        }), 500


@app.route('/api/tasks/restart-failed', methods=['POST'])
@auth_service.login_required
def task_restart_failed():
    try:
        affected, err = task_db.set_all_failed_to_pending()
        if err:
            return jsonify({
                'success': False, 'message': f'重启失败任务出错: {err}', 'code': 'RESTART_FAILED'
            }), 500

        return jsonify({
            'success': True,
            'message': f'已将 {affected} 个失败任务重置为待执行状态',
            'data': {'affected': affected}
        }), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '重启失败任务出错', 'code': 'RESTART_FAILED', 'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
