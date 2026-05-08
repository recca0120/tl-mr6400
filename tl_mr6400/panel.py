class Panel:
    def __init__(self, title: str, width: int, height: int):
        self.title = title
        self.width = width
        self.height = height
        self._rows: list[tuple[str, str] | str] = []

    def add(self, key: str, value: str):
        self._rows.append((key, value))

    def add_raw(self, text: str):
        self._rows.append(text)

    def render(self) -> list[str]:
        w = self.width
        inner = w - 2

        title_text = f" {self.title} "
        bar_len = inner - len(title_text)
        left_bar = bar_len // 2
        right_bar = bar_len - left_bar
        top = f"┌{'─' * left_bar}{title_text}{'─' * right_bar}┐"
        bottom = f"└{'─' * inner}┘"

        content_lines = self._render_rows(inner)

        content_height = self.height - 2
        while len(content_lines) < content_height:
            content_lines.append(f"│{' ' * inner}│")
        content_lines = content_lines[:content_height]

        return [top] + content_lines + [bottom]

    def _render_rows(self, inner: int) -> list[str]:
        max_key = max(
            (len(row[0]) for row in self._rows if isinstance(row, tuple)),
            default=0,
        )

        lines = []
        for row in self._rows:
            if isinstance(row, str):
                text = row[:inner]
            else:
                key, val = row
                text = f" {key.ljust(max_key)}: {val}"
                text = text[:inner]
            lines.append(f"│{text.ljust(inner)}│")
        return lines


class PanelGrid:
    @staticmethod
    def horizontal(panels: list[Panel]) -> list[str]:
        rendered = [p.render() for p in panels]
        max_h = max(len(r) for r in rendered)

        for i, r in enumerate(rendered):
            w = panels[i].width
            while len(r) < max_h:
                r.append(f"│{' ' * (w - 2)}│")

        lines = []
        for row_idx in range(max_h):
            line = "".join(r[row_idx] for r in rendered)
            lines.append(line)
        return lines

    @staticmethod
    def vertical(panels: list[Panel]) -> list[str]:
        lines = []
        for p in panels:
            lines.extend(p.render())
        return lines
