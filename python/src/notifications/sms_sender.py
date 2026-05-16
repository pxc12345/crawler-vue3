import re
import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


class SmsSender:
    def __init__(self, access_key_id: str, access_key_secret: str, region: str = 'cn-hangzhou'):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.region = region
        self.client = AcsClient(access_key_id, access_key_secret, region)

    def send_verification_code(self, phone_number: str, code: str, sign_name: str = "学生管理系统") -> dict:
        if not self._validate_phone(phone_number):
            return {
                "success": False,
                "message": "手机号格式不正确"
            }

        template_code = "SMS_123456789"

        return self._send_sms(phone_number, sign_name, template_code, json.dumps({"code": code}))

    def _send_sms(self, phone_number: str, sign_name: str, template_code: str, template_param: str) -> dict:
        request = CommonRequest()
        request.set_method('POST')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')

        request.add_query_param('PhoneNumbers', phone_number)
        request.add_query_param('SignName', sign_name)
        request.add_query_param('TemplateCode', template_code)
        request.add_query_param('TemplateParam', template_param)

        try:
            response = self.client.do_action_with_exception(request)
            response_str = response.decode('utf-8')
            response_data = json.loads(response_str)

            if response_data.get('Code') == 'OK':
                return {
                    "success": True,
                    "message": "短信发送成功",
                    "data": {
                        "to": phone_number,
                        "biz_id": response_data.get('BizId', '')
                    }
                }
            else:
                return {
                    "success": False,
                    "message": f"短信发送失败: {response_data.get('Message', 'Unknown error')}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"短信发送异常: {str(e)}"
            }

    def _validate_phone(self, phone: str) -> bool:
        pattern = r'^1[3-9]\d{9}$'
        return re.match(pattern, phone) is not None
