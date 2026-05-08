COLORS = {
    "red": "31",
    "green": "32",
    "yellow": "33",
    "blue": "34",
    "magenta": "35",
    "cyan": "36",
    "white": "37",
}

RESET = "\033[0m"
BOLD = "\033[1m"


def colorize(text: str, color: str = None, bold: bool = False) -> str:
    codes = []
    if bold:
        codes.append(BOLD)
    if color and color in COLORS:
        codes.append(f"\033[{COLORS[color]}m")
    if not codes:
        return text
    return "".join(codes) + text + RESET


class Table:
    def __init__(self):
        self._rows: list[tuple[str, str] | str] = []

    def section(self, title: str):
        self._rows.append(title)

    def add(self, key: str, value: str):
        self._rows.append((key, value))

    def render(self) -> str:
        if not self._rows:
            return ""

        max_key = 0
        for row in self._rows:
            if isinstance(row, tuple):
                max_key = max(max_key, len(row[0]))

        lines = []
        for row in self._rows:
            if isinstance(row, str):
                lines.append(colorize(f"=== {row} ===", color="cyan", bold=True))
            else:
                key, value = row
                padded_key = key + " " * (max_key - len(key))
                lines.append(f"  {colorize(padded_key, color='white', bold=True)} : {value}")

        return "\n".join(lines) + "\n"
