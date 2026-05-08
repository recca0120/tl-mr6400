# TL-MR6400 CLI

[中文](README.md)

A command-line management tool for the TP-Link TL-MR6400 router, featuring SMS management and a real-time monitoring dashboard.

## Features

- **Dashboard** — lazygit-style TUI with real-time signal, network, WiFi, and LAN status
- **SMS Management** — Read, delete, mark as read with keyboard navigation and scrolling
- **Status Queries** — LTE signal, WAN connection, wireless, LAN
- **JSON Output** — All query commands support `--json` output
- **Cross-platform** — Linux, macOS, Windows (amd64/arm64)

## Installation

### Homebrew (macOS / Linux)

```bash
brew install recca0120/tap/tl-mr6400
```

### GitHub Releases

Download the binary for your platform from [Releases](https://github.com/recca0120/tl-mr6400/releases).

macOS users may need to remove the quarantine attribute:

```bash
xattr -d com.apple.quarantine tl-mr6400
```

### Build from Source

```bash
go install github.com/recca0120/tl-mr6400/cmd/tl-mr6400@latest
```

## Configuration

Create a `.env` file:

```bash
cp .env.example .env
```

```env
ROUTER_URL=http://192.168.1.1
ROUTER_PASSWORD=admin
```

Or use environment variables:

```bash
export ROUTER_URL=http://192.168.1.1
export ROUTER_PASSWORD=admin
```

## Usage

### Dashboard (default)

```bash
tl-mr6400
```

Launches the real-time monitoring dashboard:

```
┌───────────── LTE Signal ─────────────┐┌─────────── WAN Connection ───────────┐
│ Network: 4G LTE                      ││ Status: Connected                    │
│ Signal : ▰▰▰▱ 3/4                    ││ IP    : 10.2.153.186                 │
│ RSRP   : █████░░░░░ -92 dBm          ││ MAC   : B0:95:75:73:C3:AD            │
│ RSRQ   : █████░░░░░ -11 dB           ││ DNS 1 : 61.31.1.1                    │
│ SNR    : █████████░ 36 dB            ││ DNS 2 : 61.31.233.1                  │
└──────────────────────────────────────┘└──────────────────────────────────────┘
┌────────────── Wireless ──────────────┐┌──────────────── LAN ─────────────────┐
│ SSID   : TP-Link_C3AC                ││ IP  : 192.168.1.1                    │
│ Radio  : On                          ││ Mask: 255.255.255.0                  │
│ Band   : 2.4GHz                      ││ DHCP: On                             │
└──────────────────────────────────────┘└──────────────────────────────────────┘
┌──────────────────────────────────── SMS ─────────────────────────────────────┐
│ ▶● 935188       2026-05-08 12:06                                             │
│    Reminder: your 4G data plan expires on 2026/05/08                         │
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
tl-mr6400 sms                # List SMS messages
tl-mr6400 sms --page 2       # Page 2
tl-mr6400 sms --json         # JSON output
```

### Status

```bash
tl-mr6400 status              # Show all (LTE + WAN + WiFi + LAN)
tl-mr6400 status --lte        # LTE signal only
tl-mr6400 status --wlan       # Wireless only
tl-mr6400 status --lan        # LAN only
tl-mr6400 status --json       # JSON output
```

## Signal Metrics

| Metric | Full Name | Meaning | Good Range |
|--------|-----------|---------|------------|
| **RSRP** | Reference Signal Received Power | Signal strength from tower | > -80 dBm |
| **RSRQ** | Reference Signal Received Quality | Signal quality (incl. interference) | > -10 dB |
| **SNR** | Signal-to-Noise Ratio | Signal vs noise | > 20 dB |

## Architecture

```
cmd/tl-mr6400/main.go          CLI entry point
pkg/
  parser/                       RSA key, token, response parsing
  encryption/                   RSA PKCS1 v1.5 encryption
  client/                       HTTP client + router API
  dashboard/
    panel.go                    Panel box rendering (padding, scrollbar)
    smscontroller.go            SMS cursor, viewport, actions
    render.go                   Dashboard layout (responsive)
    tui.go                      Bubbletea TUI wrapper
```

## Development

```bash
# Run tests
go test ./pkg/... -count=1 -race

# Build
go build -o tl-mr6400 ./cmd/tl-mr6400/

# Local goreleaser test
goreleaser release --snapshot --clean
```

## Supported Models

- TP-Link TL-MR6400 v3 (firmware 1.3.0 0.9.1 v0001.0 Build 200402)

Other TP-Link LTE routers (MR200, MR600) may also work but are untested.

## License

MIT
