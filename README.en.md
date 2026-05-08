# TL-MR6400 CLI (Python)

[中文](README.md) | [Go Version](https://github.com/recca0120/tl-mr6400)

A Python command-line management tool for the TP-Link TL-MR6400 router, featuring SMS management and a real-time monitoring dashboard.

> **Note**: This is the Python version. For the Go version (single binary, more polished TUI), see the [main branch](https://github.com/recca0120/tl-mr6400).

## Features

- **Dashboard** — curses TUI with real-time signal, network, WiFi, LAN, and SMS display
- **SMS Management** — Read, delete, mark as read with keyboard navigation and scrolling
- **Status Queries** — LTE signal, WAN connection, wireless, LAN
- **JSON Output** — All query commands support `--json` output
- **Zero Dependencies** — Uses only Python standard library (except pytest)

## Requirements

- Python 3.12+
- No third-party packages required

## Installation

```bash
git clone -b python https://github.com/recca0120/tl-mr6400.git
cd tl-mr6400
```

## Configuration

```bash
cp .env.example .env
```

```env
ROUTER_URL=http://192.168.1.1
ROUTER_PASSWORD=admin
```

## Usage

### Dashboard (default)

```bash
python main.py
```

Launches the real-time monitoring dashboard:

```
┌───────────── LTE Signal ─────────────┐┌─────────── WAN Connection ───────────┐
│ Network: 4G LTE                      ││ Status: Connected                    │
│ Signal : ▰▰▰▱ 3/4                    ││ IP    : 10.2.153.186                 │
│ RSRP   : █████░░░░░ -92 dBm          ││ DNS 1 : 61.31.1.1                    │
└──────────────────────────────────────┘└──────────────────────────────────────┘
┌──────────────────────────────────── SMS ─────────────────────────────────────┐
│ ● 935188       2026-05-08 12:06                                              │
│   Reminder: your 4G data plan expires on 2026/05/08                          │
└──────────────────────────────────────────────────────────────────────────────┘
 q:quit  r:refresh  ↑↓/jk:select  d:delete  m:mark read
```

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `↑` / `k` | Move selection up |
| `↓` / `j` | Move selection down |
| `d` | Delete selected SMS |
| `m` | Mark as read |
| `r` | Manual refresh |
| `q` | Quit |

### SMS

```bash
python main.py sms                # List SMS messages
python main.py sms --page 2       # Page 2
python main.py --json sms         # JSON output
```

### Status

```bash
python main.py status              # Show all (LTE + WAN + WiFi + LAN)
python main.py status --lte        # LTE signal only
python main.py status --wlan       # Wireless only
python main.py status --lan        # LAN only
python main.py --json status       # JSON output
```

## Signal Metrics

| Metric | Full Name | Meaning | Good Range |
|--------|-----------|---------|------------|
| **RSRP** | Reference Signal Received Power | Signal strength from tower | > -80 dBm |
| **RSRQ** | Reference Signal Received Quality | Signal quality (incl. interference) | > -10 dB |
| **SNR** | Signal-to-Noise Ratio | Signal vs noise | > 20 dB |

## Architecture

```
main.py                     CLI entry point
tl_mr6400/
  parser.py                 RSA key, token, response parsing
  encryption.py             RSA PKCS1 v1.5 encryption (pure Python)
  http.py                   urllib-based HTTP session
  client.py                 Router API client
  formatter.py              ANSI colors + Table formatting
  panel.py                  Panel box rendering (CJK width, scrollbar)
  dashboard.py              Dashboard layout (responsive)
  sms_controller.py         SMS cursor, viewport, actions
  screen_logic.py           Dashboard loop logic (fetch/key separation)
  screen.py                 Curses TUI
```

## Development

```bash
# Run tests
python -m pytest tests/ -v

# Run (requires router connection)
python main.py
```

## Supported Models

- TP-Link TL-MR6400 v3 (firmware 1.3.0 0.9.1 v0001.0 Build 200402)

## License

MIT
