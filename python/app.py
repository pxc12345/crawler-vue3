from flask import Flask, request, jsonify
from flask_cors import CORS
from src.auth_service import auth_service
from src.notification_db import notification_db
from src.notifications.verification_service import verification_service
import re

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})


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


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'success': True, 'message': 'Server is running'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
