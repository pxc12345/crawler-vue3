"""TiDB Cloud / MySQL 公共连接配置（供各 db 模块复用）"""
import os

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 优先从 python/.env 加载（勿提交到 Git）
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(_BASE_DIR, ".env"), override=True)
except ImportError:
    pass

def _env(key: str, default: str = "") -> str:
    """读取环境变量并去除首尾空格、引号（避免 .env 复制时带入多余字符）"""
    value = os.environ.get(key, default)
    if value is None:
        return default
    return value.strip().strip('"').strip("'")


DB_HOST = _env("DB_HOST", "gateway01.ap-southeast-1.prod.aws.tidbcloud.com")
DB_PORT = int(_env("DB_PORT", "4000"))
DB_USER = _env("DB_USER", "2TWCEXrYi7VBhDT.root")
DB_PASSWORD = _env("DB_PASSWORD", "")
DB_NAME = _env("DB_NAME", "test")
DB_CHARSET = "utf8mb4"

DB_CA_PATH = os.environ.get(
    "DB_CA_PATH",
    os.path.join(_BASE_DIR, "certs", "isrgrootx1.pem"),
)


def _build_pymysql_config():
    if not DB_PASSWORD:
        raise RuntimeError(
            "未配置数据库密码。请在 C:\\test\\python\\.env 中设置 DB_PASSWORD，"
            "值为 TiDB Cloud 控制台 Connect → 复制密码（或 Reset password 后新密码）。"
        )
    if not os.path.isfile(DB_CA_PATH):
        raise RuntimeError(
            f"未找到 CA 证书: {DB_CA_PATH}\n"
            "请从 TiDB Cloud Connect 对话框点击「CA cert」下载，"
            "保存为 python/certs/ca.pem，或设置环境变量 DB_CA_PATH。"
        )
    return {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "database": DB_NAME,
        "charset": DB_CHARSET,
        "ssl_ca": DB_CA_PATH,
        "ssl_verify_cert": True,
        "ssl_verify_identity": True,
    }


PYMYSQL_CONFIG = _build_pymysql_config()
