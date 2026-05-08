from tl_mr6400.sms_controller import SmsController
from tl_mr6400.dashboard import render_dashboard


class DashboardLoop:
    def __init__(self, client):
        self._client = client
        self.sms_ctrl = SmsController(client)
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
        self.sms_ctrl.set_messages(sms)

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
            self._status, self.sms_ctrl.messages, self._wlan, self._lan,
            width=width, sms_cursor=self.sms_ctrl.cursor,
        )
