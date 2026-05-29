import random
import string
from datetime import timedelta
from src.notification_db import notification_db
from src.datetime_utils import now_utc, now_utc_str


class VerificationService:
    CODE_LENGTH = 6
    CODE_EXPIRE_MINUTES = 5

    def __init__(self, email_sender=None, sms_sender=None):
        self.email_sender = email_sender
        self.sms_sender = sms_sender
        self.db = notification_db

    def set_email_sender(self, email_sender):
        self.email_sender = email_sender

    def set_sms_sender(self, sms_sender):
        self.sms_sender = sms_sender

    def _generate_code(self) -> str:
        return ''.join(random.choices(string.digits, k=self.CODE_LENGTH))

    def send_email_code(self, email: str) -> dict:
        if not self.email_sender:
            return {
                "success": False,
                "message": "邮件发送服务未配置"
            }

        user = self.db.get_user_by_email(email)
        user_id = user['id'] if user else self._create_temp_user(email=email)

        code = self._generate_code()
        expires_at = (now_utc() + timedelta(minutes=self.CODE_EXPIRE_MINUTES)).strftime("%Y-%m-%d %H:%M:%S")

        self.db.save_verification_code(user_id, code, 'email', email, expires_at)

        result = self.email_sender.send_verification_code(email, code)

        if result['success']:
            return {
                "success": True,
                "message": "验证码已发送到邮箱",
                "data": {
                    "user_id": user_id,
                    "target": email,
                    "expires_in": self.CODE_EXPIRE_MINUTES * 60
                }
            }
        return result

    def send_sms_code(self, phone: str) -> dict:
        if not self.sms_sender:
            return {
                "success": False,
                "message": "短信发送服务未配置"
            }

        user = self.db.get_user_by_phone(phone)
        user_id = user['id'] if user else self._create_temp_user(phone=phone)

        code = self._generate_code()
        expires_at = (now_utc() + timedelta(minutes=self.CODE_EXPIRE_MINUTES)).strftime("%Y-%m-%d %H:%M:%S")

        self.db.save_verification_code(user_id, code, 'sms', phone, expires_at)

        result = self.sms_sender.send_verification_code(phone, code)

        if result['success']:
            return {
                "success": True,
                "message": "验证码已发送到手机",
                "data": {
                    "user_id": user_id,
                    "target": phone,
                    "expires_in": self.CODE_EXPIRE_MINUTES * 60
                }
            }
        return result

    def verify_code(self, user_id: int, code: str, code_type: str, target: str) -> dict:
        db_code = self.db.get_valid_code(user_id, code, code_type, target)

        if not db_code:
            return {
                "success": False,
                "message": "验证码无效或已过期"
            }

        self.db.mark_code_used(db_code['id'])

        return {
            "success": True,
            "message": "验证成功",
            "data": {
                "user_id": user_id,
                "verified": True
            }
        }

    def _create_temp_user(self, email: str = None, phone: str = None) -> int:
        return self.db.create_user(email=email, phone=phone, password_hash=None)


verification_service = VerificationService()
