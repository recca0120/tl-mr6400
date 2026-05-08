import curses
import time
from tl_mr6400.client import TlMr6400Client
from tl_mr6400.dashboard import render_dashboard

ATTR_MAP = {
    "header": lambda: curses.color_pair(1) | curses.A_BOLD,
    "key": lambda: curses.color_pair(2),
    "normal": lambda: curses.A_NORMAL,
    "unread": lambda: curses.color_pair(3) | curses.A_BOLD,
    "read": lambda: curses.color_pair(4),
}


def _init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_WHITE, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    curses.init_pair(4, curses.COLOR_WHITE, -1)


def _fetch_data(client: TlMr6400Client):
    status = client.get_status()
    sms = client.get_sms()
    wlan = client.get_wlan()
    lan = client.get_lan()
    return status, sms, wlan, lan


def _draw(stdscr, lines):
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()
    for i, (text, attr_name) in enumerate(lines):
        if i >= max_y - 1:
            break
        attr_fn = ATTR_MAP.get(attr_name, ATTR_MAP["normal"])
        try:
            stdscr.addnstr(i, 0, text, max_x - 1, attr_fn())
        except curses.error:
            pass
    stdscr.addnstr(max_y - 1, 0, " q: quit | r: refresh ", max_x - 1, curses.A_REVERSE)
    stdscr.refresh()


def run_dashboard(client: TlMr6400Client, interval: int = 5):
    def _main(stdscr):
        _init_colors()
        curses.curs_set(0)
        stdscr.timeout(interval * 1000)

        while True:
            status, sms, wlan, lan = _fetch_data(client)
            lines = render_dashboard(status, sms, wlan, lan)
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            lines.insert(0, (f"TL-MR6400 Dashboard  (updated: {now})", "header"))
            lines.insert(1, ("", "normal"))
            _draw(stdscr, lines)

            key = stdscr.getch()
            if key in (ord("q"), ord("Q")):
                break
            if key == ord("r"):
                continue

    curses.wrapper(_main)
