# TL-MR6400 CLI

[English](README.en.md)

TP-Link TL-MR6400 路由器的命令列管理工具，提供 SMS 簡訊管理和即時狀態監控 Dashboard。

## 功能

- **Dashboard** — 類似 lazygit 的 TUI 介面，即時顯示訊號、網路、WiFi、LAN 狀態
- **SMS 管理** — 讀取、刪除、標記已讀，支援鍵盤操作和捲動
- **狀態查詢** — LTE 訊號、WAN 連線、無線網路、區域網路
- **JSON 輸出** — 所有查詢指令支援 `--json` 格式輸出
- **跨平台** — 支援 Linux、macOS、Windows（amd64/arm64）

## 安裝

### Homebrew（macOS / Linux）

```bash
brew install recca0120/tap/tl-mr6400
```

### GitHub Releases

從 [Releases](https://github.com/recca0120/tl-mr6400/releases) 下載對應平台的 binary。

macOS 使用者若遇到「無法驗證開發者」提示，執行：

```bash
xattr -d com.apple.quarantine tl-mr6400
```

### 從原始碼編譯

```bash
go install github.com/recca0120/tl-mr6400/cmd/tl-mr6400@latest
```

## 設定

建立 `.env` 檔案：

```bash
cp .env.example .env
```

```env
ROUTER_URL=http://192.168.1.1
ROUTER_PASSWORD=admin
```

也可以使用環境變數：

```bash
export ROUTER_URL=http://192.168.1.1
export ROUTER_PASSWORD=admin
```

## 使用方式

### Dashboard（預設）

```bash
tl-mr6400
```

直接執行進入即時監控 Dashboard：

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
│    提醒您4G上網吃到飽將於2026/05/08結束                                      │
│                                                                              │
│    091234       2026-05-04 10:12                                             │
│    警政署提醒您防詐騙                                                        │
└──────────────────────────────────────────────────────────────────────────────┘
 q:quit  r:refresh  ↑↓/jk:select  d:delete  m:mark read
```

### 快捷鍵

| 按鍵 | 功能 |
|------|------|
| `↑` / `k` | 上移選擇 |
| `↓` / `j` | 下移選擇 |
| `d` | 刪除選中簡訊 |
| `m` | 標記已讀 |
| `r` | 手動刷新 |
| `q` | 離開 |

### SMS 簡訊

```bash
tl-mr6400 sms                # 讀取簡訊
tl-mr6400 sms --page 2       # 第二頁
tl-mr6400 sms --json         # JSON 格式輸出
```

### 狀態查詢

```bash
tl-mr6400 status              # 顯示全部（LTE + WAN + WiFi + LAN）
tl-mr6400 status --lte        # 僅 LTE 訊號
tl-mr6400 status --wlan       # 僅無線網路
tl-mr6400 status --lan        # 僅區域網路
tl-mr6400 status --json       # JSON 格式輸出
```

## 訊號指標說明

| 指標 | 全名 | 意義 | 良好範圍 |
|------|------|------|---------|
| **RSRP** | Reference Signal Received Power | 基地台訊號強度 | > -80 dBm |
| **RSRQ** | Reference Signal Received Quality | 訊號品質（含干擾） | > -10 dB |
| **SNR** | Signal-to-Noise Ratio | 訊噪比 | > 20 dB |

## 架構

```
cmd/tl-mr6400/main.go          CLI 入口
pkg/
  parser/                       RSA key、token、response 解析
  encryption/                   RSA PKCS1 v1.5 加密
  client/                       HTTP client + router API
  dashboard/
    panel.go                    Panel 框線渲染（padding、scrollbar）
    smscontroller.go            SMS 游標、viewport、操作
    render.go                   Dashboard 組版（RWD 佈局）
    tui.go                      Bubbletea TUI wrapper
```

## 開發

```bash
# 執行測試
go test ./pkg/... -count=1 -race

# 編譯
go build -o tl-mr6400 ./cmd/tl-mr6400/

# 本地測試 goreleaser
goreleaser release --snapshot --clean
```

## 支援型號

- TP-Link TL-MR6400 v3（韌體 1.3.0 0.9.1 v0001.0 Build 200402）

其他 TP-Link LTE 路由器（MR200、MR600）可能也相容，但未測試。

## 授權

MIT
