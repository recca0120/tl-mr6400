class SmsController:
    def __init__(self, client):
        self._client = client
        self.messages: list[dict] = []
        self.cursor: int = 0

    def set_messages(self, messages: list[dict]):
        self.messages = list(messages)
        self.cursor = min(self.cursor, max(0, len(self.messages) - 1))

    @property
    def selected(self) -> dict | None:
        if not self.messages:
            return None
        return self.messages[self.cursor]

    def move_down(self):
        if not self.messages:
            return
        self.cursor = (self.cursor + 1) % len(self.messages)

    def move_up(self):
        if not self.messages:
            return
        self.cursor = (self.cursor - 1) % len(self.messages)

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
