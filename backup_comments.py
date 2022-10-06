import json
import os
from pathlib import Path
import requests

WALINE_BACKUP_API = "https://waline-comment.thiscute.world/db?lang=zh-CN"
COMMENTS_JSON_PATH = Path(__file__).parent / "data/waline_comments.json"


def main():
    # waline 的 jwt token 使用 HS256 计算，并且未设置任何过期时间（永远有效！）
    #   优先使用环境变量 JWT_TOKEN 的值作为对称密钥
    #   如果未设置 JWT_TOKEN 则使用对应后端的 PASSWORD 或者 KEY 作为对称密钥
    #   比如 LEAN_KEY、MONGO_PASSWORD、PG_PASSWORD 等
    #   所以上述信息绝对不能泄漏也不能使用弱密码！否则 JWT 将可以被伪造。
    waline_jwt = os.getenv("WALINE_JWT")
    authorization = f"Bearer {waline_jwt}"

    session = requests.Session()
    session.headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0",
        "Referer": "https://waline-comment.thiscute.world/ui/migration",
        "Authorization": authorization,
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    resp = session.get(WALINE_BACKUP_API)
    resp_json = resp.json()
    if resp.status_code != 200 or resp_json["errno"] != 0:
        print(f"backup failed! error: {resp_json}")
        return

    COMMENTS_JSON_PATH.write_text(
        json.dumps(resp_json["data"], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print("backup finished!")


if __name__ == "__main__":
    main()
