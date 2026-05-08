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
    NET_TYPES = {"0": "No Service", "1": "2G", "2": "3G", "3": "4G LTE"}

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
    print(f'  Band         : {status.get("rfInfoBand", "?")}')
    print()
    print("=== WAN Connection ===")
    print(f'  Status       : {status.get("connectionStatus", "?")}')
    print(f'  IP Address   : {status.get("externalIPAddress", "?")}')
    print(f'  Gateway      : {status.get("defaultGateway", "?")}')
    dns = status.get("DNSServers", "")
    parts = dns.split(",") if dns else []
    print(f'  Primary DNS  : {parts[0] if parts else "?"}')
    print(f'  Secondary DNS: {parts[1] if len(parts) > 1 else "?"}')
    print(f'  MAC Address  : {status.get("MACAddress", "?")}')


def cmd_wlan(args):
    client = create_client()
    wlan = client.get_wlan()
    if not wlan:
        print("Failed to get WLAN info.")
        return

    enabled = "Enabled" if wlan.get("enable") == "1" else "Disabled"
    hidden = "On" if wlan.get("SSIDAdvertisementEnabled") == "0" else "Off"

    print("=== Wireless ===")
    print(f'  SSID         : {wlan.get("SSID", "?")}')
    print(f'  Radio        : {enabled}')
    print(f'  Band         : {wlan.get("X_TP_Band", "?")}')
    print(f'  Channel      : {wlan.get("channel", "?")}')
    print(f'  Bandwidth    : {wlan.get("X_TP_Bandwidth", "?")}')
    print(f'  Hide SSID    : {hidden}')
    print(f'  TX Power     : {wlan.get("transmitPower", "?")}%')
    print(f'  Clients      : {wlan.get("totalAssociations", "?")}')


def cmd_lan(args):
    client = create_client()
    lan = client.get_lan()
    if not lan:
        print("Failed to get LAN info.")
        return

    dhcp = "On" if lan.get("DHCPServerEnable") == "1" else "Off"

    print("=== LAN ===")
    print(f'  IP Address   : {lan.get("IPInterfaceIPAddress", "?")}')
    print(f'  Subnet Mask  : {lan.get("IPInterfaceSubnetMask", "?")}')
    print(f'  MAC Address  : {lan.get("X_TP_MACAddress", "?")}')
    print(f'  DHCP         : {dhcp}')
    if dhcp == "On":
        print(f'  DHCP Range   : {lan.get("minAddress", "?")} - {lan.get("maxAddress", "?")}')


def main():
    parser = argparse.ArgumentParser(description="TL-MR6400 CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sms_parser = subparsers.add_parser("sms", help="Read SMS messages")
    sms_parser.add_argument("--page", type=int, default=1, help="Page number")

    subparsers.add_parser("status", help="Show LTE signal and WAN IP status")
    subparsers.add_parser("wlan", help="Show wireless info")
    subparsers.add_parser("lan", help="Show LAN info")

    args = parser.parse_args()
    commands = {"sms": cmd_sms, "status": cmd_status, "wlan": cmd_wlan, "lan": cmd_lan}
    commands[args.command](args)


if __name__ == "__main__":
    main()
