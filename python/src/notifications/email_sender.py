import re
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


class EmailSender:
    def __init__(self, access_key_id: str, access_key_secret: str, region: str = 'cn-hangzhou'):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.region = region
        self.client = AcsClient(access_key_id, access_key_secret, region)

    def send_verification_code(self, to_email: str, code: str) -> dict:
        if not self._validate_email(to_email):
            return {
                "success": False,
                "message": "邮箱格式不正确"
            }

        template_code = "SMS_INVALID"
        subject = "您的验证码"

        return self._send_email(to_email, subject, code)

    def _send_email(self, to_email: str, subject: str, content: str) -> dict:
        request = CommonRequest()
        request.set_method('POST')
        request.set_domain('dm.aliyuncs.com')
        request.set_version('2017-06-06')
        request.set_action_name('SingleSendMail')

        request.add_query_param('ToAddress', to_email)
        request.add_query_param('Subject', subject)
        request.add_query_param('HtmlBody', f"""
            <html>
            <body>
                <h2>验证码</h2>
                <p>您的验证码是：<strong>{content}</strong></p>
                <p>验证码 5 分钟内有效，请勿泄露给他人。</p>
            </body>
            </html>
        """)

        try:
            response = self.client.do_action_with_exception(request)
            response_str = response.decode('utf-8')
            if 'OK' in response_str:
                return {
                    "success": True,
                    "message": "邮件发送成功",
                    "data": {"to": to_email}
                }
            else:
                return {
                    "success": False,
                    "message": f"邮件发送失败: {response_str}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"邮件发送异常: {str(e)}"
            }

    def _validate_email(self, email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
