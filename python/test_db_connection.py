"""测试 TiDB Cloud 连接。

用法:
  python test_db_connection.py              # 使用 .env 中的密码
  python test_db_connection.py 你的新密码    # 临时测试（不写入 .env）
"""
import os
import sys

_BASE = os.path.dirname(os.path.abspath(__file__))
_ENV_FILE = os.path.join(_BASE, ".env")


def _connect(password: str):
    from dotenv import load_dotenv
    import pymysql

    load_dotenv(_ENV_FILE, override=True)
    os.environ["DB_PASSWORD"] = password.strip().strip('"').strip("'")

    # 重新加载配置（使用新密码）
    import importlib
    import db_settings
    importlib.reload(db_settings)

    cfg = dict(db_settings.PYMYSQL_CONFIG)
    conn = pymysql.connect(**cfg)
    with conn.cursor() as cur:
        cur.execute("SELECT VERSION()")
        version = cur.fetchone()
    conn.close()
    return version[0]


def main():
    from dotenv import load_dotenv

    load_dotenv(_ENV_FILE, override=True)

    if len(sys.argv) > 1:
        password = sys.argv[1]
        source = "命令行参数（临时测试）"
    else:
        password = os.environ.get("DB_PASSWORD", "").strip().strip('"').strip("'")
        source = _ENV_FILE

    user = os.environ.get("DB_USER", "2TWCEXrYi7VBhDT.root").strip()
    host = os.environ.get("DB_HOST", "gateway01.ap-southeast-1.prod.aws.tidbcloud.com").strip()

    print(f"配置来源: {source}")
    print(f"Host:     {host}")
    print(f"User:     {user}")
    print(f"Password: {'*' * len(password)} (长度 {len(password)})")

    if not password:
        print("\n错误: 未设置密码。")
        print("请在 .env 中设置 DB_PASSWORD，或运行:")
        print("  python test_db_connection.py 你从TiDB复制的密码")
        sys.exit(1)

    print("正在连接...")
    try:
        version = _connect(password)
        print("连接成功! TiDB 版本:", version)
        if len(sys.argv) > 1:
            print("\n请把该密码写入 .env:")
            print(f"  DB_PASSWORD={password}")
    except Exception as e:
        err = str(e)
        print("连接失败:", e)
        if "1045" in err or "Access denied" in err:
            print(
                "\n【密码错误】用户名已正确，但密码不被 TiDB 接受。\n"
                "请按顺序操作:\n"
                "  1. TiDB Cloud → 集群 fengxi → Connect → Reset password\n"
                "  2. 立刻复制新密码（只显示一次）\n"
                "  3. 运行: python test_db_connection.py 粘贴的新密码\n"
                "  4. 看到「连接成功」后，再把同一密码写入 .env 的 DB_PASSWORD\n"
                "\n注意: 每次 Reset 后，旧密码立即失效，.env 里必须是最后一次重置的密码。"
            )
        sys.exit(1)


if __name__ == "__main__":
    main()
