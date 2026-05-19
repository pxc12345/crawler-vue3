from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from src.auth_service import auth_service
from src.notification_db import notification_db
from src.notifications.verification_service import verification_service
from crawler_engine import crawler_engine
from crawler_db import crawler_db
import re
import csv
import io

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
