class Panel:
    def __init__(self, title: str, width: int, height: int):
        self.title = title
        self.width = width
        self.height = height
        self._rows: list[tuple[str, str]] = []

    def add(self, key: str, value: str):
        self._rows.append((key, value))

    def render(self) -> list[str]:
        w = self.width
        inner = w - 2

        title_text = f" {self.title} "
        bar_len = inner - len(title_text)
        left_bar = bar_len // 2
        right_bar = bar_len - left_bar
        top = f"┌{'─' * left_bar}{title_text}{'─' * right_bar}┐"

        bottom = f"└{'─' * inner}┘"

        content_lines = []
        if self._rows:
            max_key = max(len(k) for k, _ in self._rows)
            for key, val in self._rows:
                text = f" {key.ljust(max_key)}: {val}"
                text = text[:inner]
                content_lines.append(f"│{text.ljust(inner)}│")

        content_height = self.height - 2
        while len(content_lines) < content_height:
            content_lines.append(f"│{' ' * inner}│")
        content_lines = content_lines[:content_height]

        return [top] + content_lines + [bottom]


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
