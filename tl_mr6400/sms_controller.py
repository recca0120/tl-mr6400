class SmsController:
    def __init__(self, client, viewport_size: int | None = None):
        self._client = client
        self._viewport_size = viewport_size
        self.messages: list[dict] = []
        self.cursor: int = 0
        self.scroll_offset: int = 0

    def set_messages(self, messages: list[dict]):
        self.messages = list(messages)
        self.cursor = min(self.cursor, max(0, len(self.messages) - 1))
        self._adjust_scroll()

    @property
    def selected(self) -> dict | None:
        if not self.messages:
            return None
        return self.messages[self.cursor]

    @property
    def visible_messages(self) -> list[dict]:
        if self._viewport_size is None:
            return self.messages
        end = self.scroll_offset + self._viewport_size
        return self.messages[self.scroll_offset:end]

    @property
    def cursor_in_viewport(self) -> int:
        return self.cursor - self.scroll_offset

    @property
    def scrollbar_info(self) -> tuple[int, int]:
        return self.scroll_offset, len(self.messages)

    def move_down(self):
        if not self.messages:
            return
        self.cursor = (self.cursor + 1) % len(self.messages)
        if self.cursor == 0:
            self.scroll_offset = 0
        else:
            self._adjust_scroll()

    def move_up(self):
        if not self.messages:
            return
        self.cursor = (self.cursor - 1) % len(self.messages)
        if self.cursor == len(self.messages) - 1:
            self._scroll_to_end()
        else:
            self._adjust_scroll()

    def mark_read(self):
        msg = self.selected
        if not msg or msg.get("unread") != "1":
            return
        self._client.set_sms_read(int(msg["index"]))
        msg["unread"] = "0"

    def delete(self):
        msg = self.selected
        if not msg:
            return
        self._client.delete_sms(int(msg["index"]))
        self.messages.pop(self.cursor)
        if self.messages:
            self.cursor = min(self.cursor, len(self.messages) - 1)
        else:
            self.cursor = 0
        self._adjust_scroll()

    def _adjust_scroll(self):
        if self._viewport_size is None or not self.messages:
            self.scroll_offset = 0
            return
        if self.cursor < self.scroll_offset:
            self.scroll_offset = self.cursor
        elif self.cursor >= self.scroll_offset + self._viewport_size:
            self.scroll_offset = self.cursor - self._viewport_size + 1
        max_offset = max(0, len(self.messages) - self._viewport_size)
        self.scroll_offset = min(self.scroll_offset, max_offset)

    def _scroll_to_end(self):
        if self._viewport_size is None:
            return
        max_offset = max(0, len(self.messages) - self._viewport_size)
        self.scroll_offset = max_offset
