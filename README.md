# TL-MR6400 CLI (Python)

[English](README.en.md) | [Go 版本](https://github.com/recca0120/tl-mr6400)

TP-Link TL-MR6400 路由器的 Python 命令列管理工具，提供 SMS 簡訊管理和即時狀態監控 Dashboard。

> **注意**：此為 Python 版本。Go 版本（單一 binary、TUI 更完整）請見 [main 分支](https://github.com/recca0120/tl-mr6400)。

## 功能

- **Dashboard** — curses TUI 即時顯示訊號、網路、WiFi、LAN、簡訊
- **SMS 管理** — 讀取、刪除、標記已讀，支援鍵盤操作和捲動
- **狀態查詢** — LTE 訊號、WAN 連線、無線網路、區域網路
- **JSON 輸出** — 所有查詢指令支援 `--json` 格式
- **零外部依賴** — 僅使用 Python 標準庫（除 pytest）

## 環境需求

- Python 3.12+
- 無需安裝任何第三方套件

## 安裝

```bash
git clone -b python https://github.com/recca0120/tl-mr6400.git
cd tl-mr6400
```

## 設定

```bash
cp .env.example .env
```

```env
ROUTER_URL=http://192.168.1.1
ROUTER_PASSWORD=admin
```

## 使用方式

### Dashboard（預設）

```bash
python main.py
```

直接執行進入即時監控 Dashboard：

```
┌───────────── LTE Signal ─────────────┐┌─────────── WAN Connection ───────────┐
│ Network: 4G LTE                      ││ Status: Connected                    │
│ Signal : ▰▰▰▱ 3/4                    ││ IP    : 10.2.153.186                 │
│ RSRP   : █████░░░░░ -92 dBm          ││ DNS 1 : 61.31.1.1                    │
└──────────────────────────────────────┘└──────────────────────────────────────┘
┌──────────────────────────────────── SMS ─────────────────────────────────────┐
│ ● 935188       2026-05-08 12:06                                              │
│   提醒您4G上網吃到飽將於2026/05/08結束                                       │
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
python main.py sms                # 讀取簡訊
python main.py sms --page 2       # 第二頁
python main.py --json sms         # JSON 格式輸出
```

### 狀態查詢

```bash
python main.py status              # 顯示全部（LTE + WAN + WiFi + LAN）
python main.py status --lte        # 僅 LTE 訊號
python main.py status --wlan       # 僅無線網路
python main.py status --lan        # 僅區域網路
python main.py --json status       # JSON 格式輸出
```

## 訊號指標說明

| 指標 | 全名 | 意義 | 良好範圍 |
|------|------|------|---------|
| **RSRP** | Reference Signal Received Power | 基地台訊號強度 | > -80 dBm |
| **RSRQ** | Reference Signal Received Quality | 訊號品質（含干擾） | > -10 dB |
| **SNR** | Signal-to-Noise Ratio | 訊噪比 | > 20 dB |

## 架構

```
main.py                     CLI 入口
tl_mr6400/
  parser.py                 RSA key、token、response 解析
  encryption.py             RSA PKCS1 v1.5 加密（純 Python）
  http.py                   urllib 封裝的 HTTP Session
  client.py                 Router API 通訊
  formatter.py              ANSI 色碼 + Table 格式化
  panel.py                  Panel 框線渲染（CJK 寬度、scrollbar）
  dashboard.py              Dashboard 組版（RWD 佈局）
  sms_controller.py         SMS 游標、viewport、操作
  screen_logic.py           Dashboard 迴圈邏輯（fetch/key 分離）
  screen.py                 Curses TUI
```

## 開發

```bash
# 執行測試
python -m pytest tests/ -v

# 執行（需要路由器連線）
python main.py
```

## 支援型號

- TP-Link TL-MR6400 v3（韌體 1.3.0 0.9.1 v0001.0 Build 200402）

## 授權

MIT
