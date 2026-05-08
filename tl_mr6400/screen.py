import curses
import time
from tl_mr6400.client import TlMr6400Client
from tl_mr6400.dashboard import render_dashboard

STYLE_MAP = {}


def _init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    curses.init_pair(4, curses.COLOR_WHITE, -1)
    curses.init_pair(5, curses.COLOR_RED, -1)
    curses.init_pair(6, curses.COLOR_MAGENTA, -1)

    STYLE_MAP.update({
        "title": curses.color_pair(1) | curses.A_BOLD,
        "border": curses.color_pair(2),
        "key": curses.color_pair(4),
        "value": curses.color_pair(4),
        "sms_unread": curses.color_pair(3) | curses.A_BOLD,
        "sms_read": curses.color_pair(4) | curses.A_DIM,
        "empty": curses.color_pair(2),
    })


def _fetch_data(client: TlMr6400Client):
    status = client.get_status()
    sms = client.get_sms()
    wlan = client.get_wlan()
    lan = client.get_lan()
    return status, sms, wlan, lan


def _draw(stdscr, lines):
    stdscr.erase()
    max_y, max_x = stdscr.getmaxyx()

    title = f" TL-MR6400 Dashboard  [{time.strftime('%H:%M:%S')}] "
    try:
        stdscr.addnstr(0, 0, title.center(max_x), max_x - 1, STYLE_MAP["title"])
    except curses.error:
        pass

    for i, (text, style) in enumerate(lines, start=2):
        if i >= max_y - 1:
            break
        attr = STYLE_MAP.get(style, curses.A_NORMAL)
        try:
            stdscr.addnstr(i, 0, text, max_x - 1, attr)
        except curses.error:
            pass

    status_bar = " q: quit | r: refresh "
    try:
        stdscr.addnstr(max_y - 1, 0, status_bar.ljust(max_x), max_x - 1, curses.A_REVERSE)
    except curses.error:
        pass

    stdscr.refresh()


def run_dashboard(client: TlMr6400Client, interval: int = 5):
    def _main(stdscr):
        _init_colors()
        curses.curs_set(0)
        stdscr.timeout(interval * 1000)

        while True:
            max_y, max_x = stdscr.getmaxyx()
            status, sms, wlan, lan = _fetch_data(client)
            lines = render_dashboard(status, sms, wlan, lan, width=max_x)
            _draw(stdscr, lines)

            key = stdscr.getch()
            if key in (ord("q"), ord("Q")):
                break

    curses.wrapper(_main)
