from tl_mr6400.sms_controller import SmsController
from tl_mr6400.dashboard import render_dashboard


class DashboardLoop:
    SMS_VIEWPORT = 5

    def __init__(self, client):
        self._client = client
        self.sms_ctrl = SmsController(client, viewport_size=self.SMS_VIEWPORT)
        self._status = {}
        self._wlan = {}
        self._lan = {}

    def tick(self, timeout: bool = False):
        if timeout:
            self._fetch()

    def _fetch(self):
        self._status = self._client.get_status()
        sms = self._client.get_sms()
        self._wlan = self._client.get_wlan()
        self._lan = self._client.get_lan()
        self._merge_sms(sms)

    def _merge_sms(self, fresh: list[dict]):
        local_read = {
            m["index"] for m in self.sms_ctrl.messages if m.get("unread") == "0"
        }
        for msg in fresh:
            if msg["index"] in local_read:
                msg["unread"] = "0"
        self.sms_ctrl.set_messages(fresh)

    def handle_key(self, action: str):
        actions = {
            "down": self.sms_ctrl.move_down,
            "up": self.sms_ctrl.move_up,
            "delete": self.sms_ctrl.delete,
            "mark_read": self.sms_ctrl.mark_read,
        }
        fn = actions.get(action)
        if fn:
            fn()

    def render(self, width: int = 80) -> list[tuple[str, str]]:
        return render_dashboard(
            self._status, self.sms_ctrl.visible_messages, self._wlan, self._lan,
            width=width,
            sms_cursor=self.sms_ctrl.cursor_in_viewport,
            sms_scrollbar=(*self.sms_ctrl.scrollbar_info, self.SMS_VIEWPORT),
        )
