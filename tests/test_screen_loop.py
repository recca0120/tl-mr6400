from unittest.mock import MagicMock, call
from tl_mr6400.screen_logic import DashboardLoop


def _make_client():
    client = MagicMock()
    client.get_status.return_value = {"sigLevel": "3", "netType": "3"}
    client.get_sms.return_value = [
        {"index": "1", "from": "A", "content": "hi", "receivedTime": "2026-01-01", "unread": "1"},
        {"index": "2", "from": "B", "content": "yo", "receivedTime": "2026-01-02", "unread": "0"},
    ]
    client.get_wlan.return_value = {}
    client.get_lan.return_value = {}
    return client


class TestFetchOnlyOnRefresh:
    def test_initial_tick_fetches(self):
        client = _make_client()
        loop = DashboardLoop(client)
        loop.tick(timeout=True)
        assert client.get_status.call_count == 1
        assert client.get_sms.call_count == 1

    def test_keypress_does_not_fetch(self):
        client = _make_client()
        loop = DashboardLoop(client)
        loop.tick(timeout=True)
        client.reset_mock()
        loop.handle_key("down")
        assert client.get_status.call_count == 0
        assert client.get_sms.call_count == 0

    def test_refresh_key_fetches(self):
        client = _make_client()
        loop = DashboardLoop(client)
        loop.tick(timeout=True)
        client.reset_mock()
        loop.tick(timeout=True)
        assert client.get_status.call_count == 1

    def test_navigation_updates_cursor(self):
        client = _make_client()
        loop = DashboardLoop(client)
        loop.tick(timeout=True)
        loop.handle_key("down")
        assert loop.sms_ctrl.cursor == 1

    def test_delete_updates_local_state(self):
        client = _make_client()
        loop = DashboardLoop(client)
        loop.tick(timeout=True)
        loop.handle_key("delete")
        assert len(loop.sms_ctrl.messages) == 1
        client.delete_sms.assert_called_once_with(1)

    def test_mark_read_updates_local_state(self):
        client = _make_client()
        loop = DashboardLoop(client)
        loop.tick(timeout=True)
        loop.handle_key("mark_read")
        assert loop.sms_ctrl.messages[0]["unread"] == "0"
        client.set_sms_read.assert_called_once_with(1)

    def test_render_returns_styled_lines(self):
        client = _make_client()
        loop = DashboardLoop(client)
        loop.tick(timeout=True)
        lines = loop.render(width=80)
        assert isinstance(lines, list)
        assert all(isinstance(t, str) and isinstance(s, str) for t, s in lines)
