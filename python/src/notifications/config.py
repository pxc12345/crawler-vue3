import os


class NotificationConfig:
    ALIYUN_ACCESS_KEY_ID = os.getenv('ALIYUN_ACCESS_KEY_ID', 'your_access_key_id')
    ALIYUN_ACCESS_KEY_SECRET = os.getenv('ALIYUN_ACCESS_KEY_SECRET', 'your_access_key_secret')
    ALIYUN_REGION = os.getenv('ALIYUN_REGION', 'cn-hangzhou')

    SMS_SIGN_NAME = os.getenv('SMS_SIGN_NAME', '学生管理系统')
    SMS_TEMPLATE_CODE = os.getenv('SMS_TEMPLATE_CODE', 'SMS_123456789')

    EMAIL_ENABLED = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
    SMS_ENABLED = os.getenv('SMS_ENABLED', 'false').lower() == 'true'

    CODE_LENGTH = 6
    CODE_EXPIRE_MINUTES = 5


notification_config = NotificationConfig()
