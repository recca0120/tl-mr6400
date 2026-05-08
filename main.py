import argparse
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


def create_client():
    load_dotenv()
    url = os.environ.get("ROUTER_URL", "http://192.168.1.1")
    password = os.environ.get("ROUTER_PASSWORD", "admin")
    client = TlMr6400Client(url, password)
    client.login()
    return client


def cmd_sms(args):
    client = create_client()
    messages = client.get_sms(page=args.page)
    if not messages:
        print("No SMS messages found.")
        return
    for msg in messages:
        status = "[unread]" if msg.get("unread") == "1" else "[read]"
        print(f'{status} {msg.get("receivedTime", "?")}  From: {msg.get("from", "?")}')
        print(f'  {msg.get("content", "")}')
        print()


def cmd_status(args):
    NET_TYPES = {"0": "No Service", "1": "2G", "2": "3G", "3": "4G"}
    CONN_STATS = {"0": "Disconnected", "1": "Connecting", "2": "Connected", "3": "Disconnecting", "4": "Connected"}

    client = create_client()
    status = client.get_status()
    if not status:
        print("Failed to get status.")
        return

    print("=== LTE Signal ===")
    print(f'  Network Type : {NET_TYPES.get(status.get("netType", ""), status.get("netType", "?"))}')
    print(f'  Signal Level : {status.get("sigLevel", "?")}/4')
    print(f'  RSSI         : {status.get("rfInfoRssi", "?")} dBm')
    print(f'  RSRP         : {status.get("rfInfoRsrp", "?")} dBm')
    print(f'  RSRQ         : {status.get("rfInfoRsrq", "?")} dB')
    print(f'  SNR          : {status.get("rfInfoSnr", "?")} dB')
    print()
    print("=== WAN Connection ===")
    print(f'  Status       : {status.get("connectionStatus", "?")}')
    print(f'  IP Address   : {status.get("externalIPAddress", "?")}')
    print(f'  Gateway      : {status.get("defaultGateway", "?")}')
    print(f'  DNS          : {status.get("DNSServers", "?")}')


def main():
    parser = argparse.ArgumentParser(description="TL-MR6400 CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sms_parser = subparsers.add_parser("sms", help="Read SMS messages")
    sms_parser.add_argument("--page", type=int, default=1, help="Page number")

    subparsers.add_parser("status", help="Show LTE signal and WAN IP status")

    args = parser.parse_args()
    commands = {"sms": cmd_sms, "status": cmd_status}
    commands[args.command](args)


if __name__ == "__main__":
    main()
