import bcrypt
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from src.notification_db import notification_db
from src.datetime_utils import now_utc


class AuthService:
    SECRET_KEY = 'your-secret-key-change-in-production-12345'
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_HOURS = 24
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_MINUTES = 15

    def __init__(self, db):
        self.db = db

    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    def _token_str(self, token) -> str:
        """PyJWT 在部分环境下返回 bytes，需转为 str 才能被 jsonify 序列化。"""
        if isinstance(token, bytes):
            return token.decode('utf-8')
        return str(token)

    def create_access_token(self, user_id: int, username: str) -> str:
        expire = datetime.utcnow() + timedelta(hours=self.ACCESS_TOKEN_EXPIRE_HOURS)
        payload = {
            'sub': str(user_id),  # 转换为字符串
            'username': username,
            'type': 'access',
            'exp': expire
        }
        return self._token_str(jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM))

    def create_refresh_token(self, user_id: int, username: str) -> str:
        expire = datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            'sub': str(user_id),  # 转换为字符串
            'username': username,
            'type': 'refresh',
            'exp': expire
        }
        return self._token_str(jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM))

    def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None

    def is_token_blacklisted(self, token: str) -> bool:
        return self.db.is_token_blacklisted(token)

    def blacklist_token(self, token: str):
        payload = self.decode_token(token)
        if payload:
            expires_at = datetime.fromtimestamp(payload['exp'])
            self.db.add_token_to_blacklist(token, expires_at)

    def is_user_locked(self, user: dict) -> bool:
        if user.get('locked_until'):
            locked_until = user['locked_until']
            if isinstance(locked_until, str):
                locked_until = datetime.strptime(locked_until, '%Y-%m-%d %H:%M:%S')
            if locked_until > now_utc():
                return True
        return False

    def authenticate_user(self, identifier: str, password: str) -> dict:
        user = self.db.get_user_by_email_or_username(identifier)
        
        if not user:
            return {'success': False, 'message': '用户不存在', 'code': 'USER_NOT_FOUND'}

        if self.is_user_locked(user):
            return {'success': False, 'message': '账户已被锁定，请稍后再试', 'code': 'ACCOUNT_LOCKED'}

        if not user['password_hash']:
            return {'success': False, 'message': '请先设置密码', 'code': 'PASSWORD_NOT_SET'}

        if not self.verify_password(password, user['password_hash']):
            self.db.increment_login_attempts(user['id'])
            
            if user['login_attempts'] + 1 >= self.MAX_LOGIN_ATTEMPTS:
                lock_until = now_utc() + timedelta(minutes=self.LOCKOUT_MINUTES)
                self.db.lock_user(user['id'], lock_until)
                return {'success': False, 'message': f'登录失败次数过多，账户已锁定{self.LOCKOUT_MINUTES}分钟', 'code': 'ACCOUNT_LOCKED'}
            
            remaining = self.MAX_LOGIN_ATTEMPTS - (user['login_attempts'] + 1)
            return {'success': False, 'message': f'密码错误，还剩{remaining}次尝试机会', 'code': 'INVALID_PASSWORD'}

        self.db.reset_login_attempts(user['id'])
        self.db.update_last_login(user['id'])
        
        access_token = self.create_access_token(user['id'], user['username'])
        refresh_token = self.create_refresh_token(user['id'], user['username'])

        return {
            'success': True,
            'message': '登录成功',
            'data': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'phone': user['phone']
                }
            }
        }

    def refresh_access_token(self, refresh_token: str) -> dict:
        if self.is_token_blacklisted(refresh_token):
            return {'success': False, 'message': 'Token已失效', 'code': 'TOKEN_INVALID'}

        payload = self.decode_token(refresh_token)
        if not payload or payload.get('type') != 'refresh':
            return {'success': False, 'message': '无效的Refresh Token', 'code': 'TOKEN_INVALID'}

        user = self.db.get_user_by_id(payload['sub'])
        if not user:
            return {'success': False, 'message': '用户不存在', 'code': 'USER_NOT_FOUND'}

        new_access_token = self.create_access_token(user['id'], user['username'])
        return {
            'success': True,
            'data': {'access_token': new_access_token}
        }

    def reset_password(self, user_id: int, new_password: str, check_history: bool = True) -> dict:
        user = self.db.get_user_by_id(user_id)
        if not user:
            return {'success': False, 'message': '用户不存在', 'code': 'USER_NOT_FOUND'}

        password_hash = self.hash_password(new_password)

        if check_history:
            old_hashes = self.db.get_password_history(user_id)
            for old_hash in old_hashes:
                if self.verify_password(new_password, old_hash):
                    return {'success': False, 'message': '新密码不能与最近使用的密码相同', 'code': 'PASSWORD_REUSED'}

        if user['password_hash']:
            self.db.add_password_history(user_id, user['password_hash'])

        self.db.update_user_password(user_id, password_hash)
        
        return {'success': True, 'message': '密码重置成功'}

    def login_required(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method == 'OPTIONS':
                return '', 204
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({'success': False, 'message': '未提供认证令牌', 'code': 'TOKEN_MISSING'}), 401

            try:
                token_type, token = auth_header.split()
                if token_type.lower() != 'bearer':
                    return jsonify({'success': False, 'message': '无效的认证类型', 'code': 'TOKEN_INVALID'}), 401
            except ValueError:
                return jsonify({'success': False, 'message': '无效的认证格式', 'code': 'TOKEN_INVALID'}), 401

            if self.is_token_blacklisted(token):
                return jsonify({'success': False, 'message': 'Token已失效', 'code': 'TOKEN_INVALID'}), 401

            payload = self.decode_token(token)
            if not payload or payload.get('type') != 'access':
                return jsonify({'success': False, 'message': '无效的Token', 'code': 'TOKEN_INVALID'}), 401

            request.user_id = int(payload['sub'])
            request.username = payload['username']
            return f(*args, **kwargs)

        return decorated_function


auth_service = AuthService(notification_db)
