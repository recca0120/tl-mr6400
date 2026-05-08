import os
from pathlib import Path
from tl_mr6400.client import TlMr6400Client


def load_dotenv(path=".env"):
    env_file = Path(path)
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


load_dotenv()

url = os.environ.get("ROUTER_URL", "http://192.168.1.1")
password = os.environ.get("ROUTER_PASSWORD", "admin")

client = TlMr6400Client(url, password)
client.login()

messages = client.get_sms()

if not messages:
    print("No SMS messages found.")
else:
    for msg in messages:
        status = "[unread]" if msg.get("unread") == "1" else "[read]"
        print(f'{status} {msg.get("receivedTime", "?")}  From: {msg.get("from", "?")}')
        print(f'  {msg.get("content", "")}')
        print()
