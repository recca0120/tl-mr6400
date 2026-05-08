import argparse
import json as json_mod
import os
from pathlib import Path
from tl_mr6400.client import TlMr6400Client
from tl_mr6400.formatter import Table


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


NET_TYPES = {"0": "No Service", "1": "2G", "2": "3G", "3": "4G LTE"}


def cmd_sms(args):
    client = create_client()
    messages = client.get_sms(page=args.page)
    if args.json:
        print(json_mod.dumps(messages, ensure_ascii=False, indent=2))
        return
    if not messages:
        print("No SMS messages found.")
        return
    for msg in messages:
        status = "[unread]" if msg.get("unread") == "1" else "[read]"
        print(f'{status} {msg.get("receivedTime", "?")}  From: {msg.get("from", "?")}')
        print(f'  {msg.get("content", "")}')
        print()


def _render_lte(t, status):
    dns = status.get("DNSServers", "")
    parts = dns.split(",") if dns else []

    t.section("LTE Signal")
    t.add("Network Type", NET_TYPES.get(status.get("netType", ""), status.get("netType", "?")))
    t.add("Signal Level", f'{status.get("sigLevel", "?")}/4')
    t.add("RSSI", f'{status.get("rfInfoRssi", "?")} dBm')
    t.add("RSRP", f'{status.get("rfInfoRsrp", "?")} dBm')
    t.add("RSRQ", f'{status.get("rfInfoRsrq", "?")} dB')
    t.add("SNR", f'{status.get("rfInfoSnr", "?")} dB')
    t.add("Band", status.get("rfInfoBand", "?"))
    t.section("WAN Connection")
    t.add("Status", status.get("connectionStatus", "?"))
    t.add("IP Address", status.get("externalIPAddress", "?"))
    t.add("Gateway", status.get("defaultGateway", "?"))
    t.add("Primary DNS", parts[0] if parts else "?")
    t.add("Secondary DNS", parts[1] if len(parts) > 1 else "?")
    t.add("MAC Address", status.get("MACAddress", "?"))


def _render_wlan(t, wlan):
    enabled = "Enabled" if wlan.get("enable") == "1" else "Disabled"
    hidden = "On" if wlan.get("SSIDAdvertisementEnabled") == "0" else "Off"

    t.section("Wireless")
    t.add("SSID", wlan.get("SSID", "?"))
    t.add("Radio", enabled)
    t.add("Band", wlan.get("X_TP_Band", "?"))
    t.add("Channel", wlan.get("channel", "?"))
    t.add("Bandwidth", wlan.get("X_TP_Bandwidth", "?"))
    t.add("Hide SSID", hidden)
    t.add("TX Power", f'{wlan.get("transmitPower", "?")}%')
    t.add("Clients", wlan.get("totalAssociations", "?"))


def _render_lan(t, lan):
    dhcp = "On" if lan.get("DHCPServerEnable") == "1" else "Off"

    t.section("LAN")
    t.add("IP Address", lan.get("IPInterfaceIPAddress", "?"))
    t.add("Subnet Mask", lan.get("IPInterfaceSubnetMask", "?"))
    t.add("MAC Address", lan.get("X_TP_MACAddress", "?"))
    t.add("DHCP", dhcp)
    if dhcp == "On":
        t.add("DHCP Range", f'{lan.get("minAddress", "?")} - {lan.get("maxAddress", "?")}')


def cmd_status(args):
    client = create_client()
    show_all = not (args.lte or args.wlan or args.lan)

    if args.json:
        data = {}
        if show_all:
            data["lte"] = client.get_status()
            data["wlan"] = client.get_wlan()
            data["lan"] = client.get_lan()
        elif args.lte:
            data = client.get_status()
        elif args.wlan:
            data = client.get_wlan()
        elif args.lan:
            data = client.get_lan()
        print(json_mod.dumps(data, ensure_ascii=False, indent=2))
        return

    t = Table()

    if show_all or args.lte:
        status = client.get_status()
        if not status:
            print("Failed to get status.")
            return
        _render_lte(t, status)

    if show_all or args.wlan:
        wlan = client.get_wlan()
        if wlan:
            _render_wlan(t, wlan)

    if show_all or args.lan:
        lan = client.get_lan()
        if lan:
            _render_lan(t, lan)

    print(t.render(), end="")


def cmd_dashboard(args):
    from tl_mr6400.screen import run_dashboard
    client = create_client()
    run_dashboard(client, interval=args.interval)


def main():
    parser = argparse.ArgumentParser(description="TL-MR6400 CLI")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sms_parser = subparsers.add_parser("sms", help="Read SMS messages")
    sms_parser.add_argument("--page", type=int, default=1, help="Page number")

    status_parser = subparsers.add_parser("status", help="Show router status")
    status_parser.add_argument("--lte", action="store_true", help="Show LTE signal and WAN only")
    status_parser.add_argument("--wlan", action="store_true", help="Show wireless only")
    status_parser.add_argument("--lan", action="store_true", help="Show LAN only")

    dash_parser = subparsers.add_parser("dashboard", help="Live dashboard (htop-style)")
    dash_parser.add_argument("--interval", type=int, default=5, help="Refresh interval in seconds")

    args = parser.parse_args()
    commands = {"sms": cmd_sms, "status": cmd_status, "dashboard": cmd_dashboard}
    commands[args.command](args)


if __name__ == "__main__":
    main()
