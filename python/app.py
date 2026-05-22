from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from src.auth_service import auth_service
from src.notification_db import notification_db
from src.notifications.verification_service import verification_service
from crawler_engine import crawler_engine
from crawler_db import crawler_db
from task_db import task_db
from alert_db import alert_db
from proxy_db import proxy_db
from system_db import system_db
import re
import csv
import io
import json
import psutil

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:5173", "http://127.0.0.1:5173",
            "http://localhost:3000", "http://127.0.0.1:3000"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

crawler_db.connect()
task_db.connect()
alert_db.connect()
proxy_db.connect()
system_db.connect()


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
            notification_db.add_audit_log(
                user_id=result['data']['user']['id'],
                action='LOGIN',
                ip_address=get_client_ip(),
                user_agent=request.headers.get('User-Agent'),
                details=f'用户 {identifier} 登录成功'
            )
        
        return jsonify(result), 200 if result['success'] else 401

    except Exception as e:
        return jsonify({'success': False, 'message': '登录失败', 'code': 'LOGIN_FAILED', 'error': str(e)}), 500


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
                'last_login_at': user['last_login_at'],
                'created_at': user['created_at']
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': '获取用户信息失败', 'code': 'GET_PROFILE_FAILED', 'error': str(e)}), 500


def _save_crawled_data(items):
    """爬虫数据保存回调函数，供爬虫引擎调用"""
    return crawler_db.save_batch(items)


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

        success, message = crawler_engine.start(
            target_url, total_pages, int(interval_seconds), _save_crawled_data, crawl_mode
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
    return jsonify({'success': True, 'message': 'Server is running'}), 200


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
            return jsonify({
                'success': False, 'message': '请选择任务类型', 'code': 'MISSING_TYPE'
            }), 400

        task_id = task_db.create(
            user_id=request.user_id,
            name=name,
            task_type=task_type,
            config=config,
            description=description,
            template_id=template_id
        )

        return jsonify({
            'success': True, 'message': '创建任务成功', 'data': {'task_id': task_id}
        }), 201

    except Exception as e:
        return jsonify({
            'success': False, 'message': '创建任务失败', 'code': 'TASK_CREATE_FAILED', 'error': str(e)
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
        task_type = data.get('task_type')
        config = data.get('config')
        description = data.get('description')

        task_db.update(
            task_id=task_id,
            name=name,
            task_type=task_type,
            config=config,
            description=description,
            user_id=request.user_id
        )

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
    try:
        task = task_db.get_by_id(task_id, user_id=request.user_id)
        if not task:
            return jsonify({
                'success': False, 'message': '任务不存在', 'code': 'TASK_NOT_FOUND'
            }), 404

        success, message = task_db.start_task(task_id, user_id=request.user_id)

        return jsonify({'success': success, 'message': message}), 200 if success else 400

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

        success, message = task_db.stop_task(task_id, user_id=request.user_id)

        return jsonify({'success': success, 'message': message}), 200 if success else 400

    except Exception as e:
        return jsonify({
            'success': False, 'message': '停止任务失败', 'code': 'TASK_STOP_FAILED', 'error': str(e)
        }), 500


@app.route('/api/tasks/templates', methods=['GET'])
@auth_service.login_required
def task_template_list():
    try:
        templates = task_db.get_templates(user_id=request.user_id)

        return jsonify({'success': True, 'data': templates}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取模板列表失败', 'code': 'TEMPLATE_LIST_FAILED', 'error': str(e)
        }), 500


@app.route('/api/tasks/templates', methods=['POST'])
@auth_service.login_required
def task_template_create():
    try:
        data = request.get_json()
        name = (data.get('name') or '').strip()
        task_type = (data.get('task_type') or '').strip()
        config = data.get('config', {})
        description = (data.get('description') or '').strip()

        if not name:
            return jsonify({
                'success': False, 'message': '请输入模板名称', 'code': 'MISSING_NAME'
            }), 400

        template_id = task_db.create_template(
            user_id=request.user_id,
            name=name,
            task_type=task_type,
            config=config,
            description=description
        )

        return jsonify({
            'success': True, 'message': '创建模板成功', 'data': {'template_id': template_id}
        }), 201

    except Exception as e:
        return jsonify({
            'success': False, 'message': '创建模板失败', 'code': 'TEMPLATE_CREATE_FAILED', 'error': str(e)
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

        return jsonify({'success': True, 'data': template}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取模板详情失败', 'code': 'TEMPLATE_DETAIL_FAILED', 'error': str(e)
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

        task_db.delete_template(template_id, user_id=request.user_id)

        return jsonify({'success': True, 'message': '删除模板成功'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '删除模板失败', 'code': 'TEMPLATE_DELETE_FAILED', 'error': str(e)
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

        task_db.add_favorite(task_id, user_id=request.user_id)

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

        task_db.remove_favorite(task_id, user_id=request.user_id)

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


@app.route('/api/data/clean', methods=['POST'])
@auth_service.login_required
def data_clean():
    try:
        data = request.get_json()
        items = data.get('data', [])
        operations = data.get('operations', [])

        if not items or not isinstance(items, list):
            return jsonify({
                'success': False, 'message': '请提供有效的数据', 'code': 'INVALID_DATA'
            }), 400

        cleaned = list(items)

        for op in operations:
            if op == 'deduplicate':
                seen = set()
                unique = []
                for item in cleaned:
                    item_key = json.dumps(item, sort_keys=True, ensure_ascii=False)
                    if item_key not in seen:
                        seen.add(item_key)
                        unique.append(item)
                cleaned = unique
            elif op == 'filter_empty':
                cleaned = [
                    item for item in cleaned
                    if item and any(v for v in item.values() if v)
                ]
            elif op == 'format_fields':
                cleaned = [
                    {k: (v.strip() if isinstance(v, str) else v) for k, v in item.items()}
                    if isinstance(item, dict) else item
                    for item in cleaned
                ]

        return jsonify({
            'success': True,
            'message': '数据清洗完成',
            'data': {
                'original_count': len(items),
                'cleaned_count': len(cleaned),
                'items': cleaned
            }
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

        items = crawler_db.get_all()

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


@app.route('/api/data/auto-write-config', methods=['POST'])
@auth_service.login_required
def data_auto_write_config():
    try:
        data = request.get_json()
        target_type = data.get('target_type')
        target_config = data.get('target_config', {})

        if not target_type:
            return jsonify({
                'success': False, 'message': '请选择写入目标类型', 'code': 'MISSING_TARGET_TYPE'
            }), 400

        crawler_db.save_auto_write_config(
            user_id=request.user_id,
            target_type=target_type,
            target_config=target_config
        )

        return jsonify({'success': True, 'message': '自动写入配置保存成功'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '保存配置失败', 'code': 'AUTO_WRITE_CONFIG_FAILED', 'error': str(e)
        }), 500


@app.route('/api/data/push-config', methods=['POST'])
@auth_service.login_required
def data_push_config():
    try:
        data = request.get_json()
        push_type = data.get('push_type')
        push_config = data.get('push_config', {})

        if not push_type:
            return jsonify({
                'success': False, 'message': '请选择推送类型', 'code': 'MISSING_PUSH_TYPE'
            }), 400

        crawler_db.save_push_config(
            user_id=request.user_id,
            push_type=push_type,
            push_config=push_config
        )

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
        proxies = proxy_db.get_list(user_id=request.user_id)

        return jsonify({'success': True, 'data': proxies}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取代理列表失败', 'code': 'PROXY_LIST_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/add', methods=['POST'])
@auth_service.login_required
def proxy_add():
    try:
        data = request.get_json()
        host = (data.get('host') or '').strip()
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

        proxy_id = proxy_db.add(
            user_id=request.user_id,
            host=host,
            port=port,
            protocol=protocol,
            username=username,
            password=password
        )

        return jsonify({
            'success': True, 'message': '添加代理成功', 'data': {'proxy_id': proxy_id}
        }), 201

    except Exception as e:
        return jsonify({
            'success': False, 'message': '添加代理失败', 'code': 'PROXY_ADD_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/<proxy_id>', methods=['DELETE'])
@auth_service.login_required
def proxy_delete(proxy_id):
    try:
        proxy_db.delete(proxy_id, user_id=request.user_id)

        return jsonify({'success': True, 'message': '删除代理成功'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '删除代理失败', 'code': 'PROXY_DELETE_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/<proxy_id>/refresh', methods=['POST'])
@auth_service.login_required
def proxy_refresh(proxy_id):
    try:
        success, message = proxy_db.refresh(proxy_id, user_id=request.user_id)

        return jsonify({'success': success, 'message': message}), 200 if success else 400

    except Exception as e:
        return jsonify({
            'success': False, 'message': '刷新代理失败', 'code': 'PROXY_REFRESH_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/groups', methods=['GET'])
@auth_service.login_required
def proxy_groups():
    try:
        groups = proxy_db.get_groups(user_id=request.user_id)

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

        group_id = proxy_db.create_group(
            user_id=request.user_id,
            name=name,
            description=description
        )

        return jsonify({
            'success': True, 'message': '创建代理组成功', 'data': {'group_id': group_id}
        }), 201

    except Exception as e:
        return jsonify({
            'success': False, 'message': '创建代理组失败', 'code': 'PROXY_GROUP_CREATE_FAILED', 'error': str(e)
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

        proxy_db.assign_to_group(proxy_id, group_id, user_id=request.user_id)

        return jsonify({'success': True, 'message': '代理分配成功'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '代理分配失败', 'code': 'PROXY_ASSIGN_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/blacklist', methods=['GET'])
@auth_service.login_required
def proxy_blacklist():
    try:
        items = proxy_db.get_blacklist(user_id=request.user_id)

        return jsonify({'success': True, 'data': items}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取黑名单失败', 'code': 'BLACKLIST_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/blacklist', methods=['POST'])
@auth_service.login_required
def proxy_blacklist_add():
    try:
        data = request.get_json()
        target = (data.get('target') or '').strip()
        reason = (data.get('reason') or '').strip()

        if not target:
            return jsonify({
                'success': False, 'message': '请输入黑名单目标', 'code': 'MISSING_TARGET'
            }), 400

        item_id = proxy_db.add_blacklist(
            user_id=request.user_id,
            target=target,
            reason=reason
        )

        return jsonify({
            'success': True, 'message': '已加入黑名单', 'data': {'item_id': item_id}
        }), 201

    except Exception as e:
        return jsonify({
            'success': False, 'message': '加入黑名单失败', 'code': 'BLACKLIST_ADD_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/blacklist/<item_id>', methods=['DELETE'])
@auth_service.login_required
def proxy_blacklist_remove(item_id):
    try:
        proxy_db.remove_blacklist(item_id, user_id=request.user_id)

        return jsonify({'success': True, 'message': '已从黑名单移除'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '移除黑名单失败', 'code': 'BLACKLIST_REMOVE_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/whitelist', methods=['GET'])
@auth_service.login_required
def proxy_whitelist():
    try:
        items = proxy_db.get_whitelist(user_id=request.user_id)

        return jsonify({'success': True, 'data': items}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取白名单失败', 'code': 'WHITELIST_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/whitelist', methods=['POST'])
@auth_service.login_required
def proxy_whitelist_add():
    try:
        data = request.get_json()
        target = (data.get('target') or '').strip()
        reason = (data.get('reason') or '').strip()

        if not target:
            return jsonify({
                'success': False, 'message': '请输入白名单目标', 'code': 'MISSING_TARGET'
            }), 400

        item_id = proxy_db.add_whitelist(
            user_id=request.user_id,
            target=target,
            reason=reason
        )

        return jsonify({
            'success': True, 'message': '已加入白名单', 'data': {'item_id': item_id}
        }), 201

    except Exception as e:
        return jsonify({
            'success': False, 'message': '加入白名单失败', 'code': 'WHITELIST_ADD_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/whitelist/<item_id>', methods=['DELETE'])
@auth_service.login_required
def proxy_whitelist_remove(item_id):
    try:
        proxy_db.remove_whitelist(item_id, user_id=request.user_id)

        return jsonify({'success': True, 'message': '已从白名单移除'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '移除白名单失败', 'code': 'WHITELIST_REMOVE_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/rate-limits', methods=['GET'])
@auth_service.login_required
def proxy_rate_limits():
    try:
        limits = proxy_db.get_rate_limits(user_id=request.user_id)

        return jsonify({'success': True, 'data': limits}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取速率限制失败', 'code': 'RATE_LIMIT_FAILED', 'error': str(e)
        }), 500


@app.route('/api/proxy/rate-limits', methods=['POST'])
@auth_service.login_required
def proxy_rate_limit_set():
    try:
        data = request.get_json()
        max_requests = data.get('max_requests')
        time_window = data.get('time_window')
        target_id = data.get('target_id')

        if not max_requests or not time_window:
            return jsonify({
                'success': False, 'message': '请设置最大请求数和时间窗口', 'code': 'MISSING_PARAMS'
            }), 400

        proxy_db.set_rate_limit(
            user_id=request.user_id,
            target_id=target_id,
            max_requests=max_requests,
            time_window=time_window
        )

        return jsonify({'success': True, 'message': '速率限制设置成功'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '设置速率限制失败', 'code': 'RATE_LIMIT_SET_FAILED', 'error': str(e)
        }), 500


# ==================== System Routes ====================

@app.route('/api/system/resources', methods=['GET'])
@auth_service.login_required
def system_resources():
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        return jsonify({
            'success': True,
            'data': {
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


@app.route('/api/system/logs', methods=['GET'])
@auth_service.login_required
def system_logs():
    try:
        level = request.args.get('level', '', type=str)
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)

        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        logs, total = system_db.get_logs(
            user_id=request.user_id,
            level=level,
            page=page,
            page_size=page_size
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
        data = request.get_json()
        days = data.get('days', 30)

        if not isinstance(days, int) or days < 1:
            return jsonify({
                'success': False, 'message': '请提供有效的天数（大于0的整数）', 'code': 'INVALID_DAYS'
            }), 400

        system_db.clear_logs(days=days, user_id=request.user_id)

        return jsonify({'success': True, 'message': f'已清理 {days} 天前的日志'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '清理日志失败', 'code': 'LOGS_CLEAR_FAILED', 'error': str(e)
        }), 500


@app.route('/api/system/settings', methods=['GET'])
@auth_service.login_required
def system_settings():
    try:
        settings = system_db.get_settings(user_id=request.user_id)

        return jsonify({'success': True, 'data': settings}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '获取系统设置失败', 'code': 'SETTINGS_FAILED', 'error': str(e)
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

        system_db.update_setting(key=key, value=value, user_id=request.user_id)

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

        system_db.save_user_preferences(user_id=request.user_id, preferences=data)

        return jsonify({'success': True, 'message': '偏好设置保存成功'}), 200

    except Exception as e:
        return jsonify({
            'success': False, 'message': '保存偏好设置失败', 'code': 'PREFERENCES_SAVE_FAILED', 'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
