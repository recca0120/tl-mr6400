import pytest
from unittest.mock import MagicMock
from tl_mr6400.sms_controller import SmsController


SMS_DATA = [
    {"index": "124", "from": "935188", "content": "Hello", "receivedTime": "2026-05-08 12:06:08", "unread": "1"},
    {"index": "123", "from": "091234", "content": "World", "receivedTime": "2026-05-07 10:09:22", "unread": "0"},
    {"index": "122", "from": "555555", "content": "Test", "receivedTime": "2026-05-06 09:00:00", "unread": "1"},
]

MANY_SMS = [
    {"index": str(i), "from": f"0900{i:04d}", "content": f"Msg {i}", "receivedTime": f"2026-05-{i:02d} 10:00", "unread": str(i % 2)}
    for i in range(1, 11)
]


class TestCursorNavigation:
    def test_initial_cursor_is_zero(self):
        ctrl = SmsController(MagicMock())
        ctrl.set_messages(SMS_DATA)
        assert ctrl.cursor == 0

    def test_move_down(self):
        ctrl = SmsController(MagicMock())
        ctrl.set_messages(SMS_DATA)
        ctrl.move_down()
        assert ctrl.cursor == 1

    def test_move_down_wraps_at_end(self):
        ctrl = SmsController(MagicMock())
        ctrl.set_messages(SMS_DATA)
        ctrl.move_down()
        ctrl.move_down()
        ctrl.move_down()
        assert ctrl.cursor == 0

    def test_move_up(self):
        ctrl = SmsController(MagicMock())
        ctrl.set_messages(SMS_DATA)
        ctrl.move_down()
        ctrl.move_up()
        assert ctrl.cursor == 0

    def test_move_up_wraps_at_start(self):
        ctrl = SmsController(MagicMock())
        ctrl.set_messages(SMS_DATA)
        ctrl.move_up()
        assert ctrl.cursor == 2

    def test_empty_messages_no_crash(self):
        ctrl = SmsController(MagicMock())
        ctrl.set_messages([])
        ctrl.move_down()
        ctrl.move_up()
        assert ctrl.cursor == 0

    def test_selected_message(self):
        ctrl = SmsController(MagicMock())
        ctrl.set_messages(SMS_DATA)
        ctrl.move_down()
        assert ctrl.selected["index"] == "123"


class TestMarkRead:
    def test_calls_client_set_sms_read(self):
        client = MagicMock()
        ctrl = SmsController(client)
        ctrl.set_messages(SMS_DATA)
        ctrl.mark_read()
        client.set_sms_read.assert_called_once_with(124)

    def test_updates_local_state(self):
        client = MagicMock()
        ctrl = SmsController(client)
        ctrl.set_messages(SMS_DATA)
        ctrl.mark_read()
        assert ctrl.messages[0]["unread"] == "0"

    def test_noop_on_already_read(self):
        client = MagicMock()
        ctrl = SmsController(client)
        ctrl.set_messages(SMS_DATA)
        ctrl.move_down()
        ctrl.mark_read()
        client.set_sms_read.assert_not_called()

    def test_noop_on_empty(self):
        client = MagicMock()
        ctrl = SmsController(client)
        ctrl.set_messages([])
        ctrl.mark_read()
        client.set_sms_read.assert_not_called()


class TestDeleteSms:
    def test_calls_client_delete(self):
        client = MagicMock()
        ctrl = SmsController(client)
        ctrl.set_messages(SMS_DATA)
        ctrl.delete()
        client.delete_sms.assert_called_once_with(124)

    def test_removes_from_local_list(self):
        client = MagicMock()
        ctrl = SmsController(client)
        ctrl.set_messages(SMS_DATA)
        ctrl.delete()
        assert len(ctrl.messages) == 2
        assert ctrl.messages[0]["index"] == "123"

    def test_cursor_stays_in_bounds_after_delete_last(self):
        client = MagicMock()
        ctrl = SmsController(client)
        ctrl.set_messages(SMS_DATA)
        ctrl.move_down()
        ctrl.move_down()
        ctrl.delete()
        assert ctrl.cursor == 1

    def test_noop_on_empty(self):
        client = MagicMock()
        ctrl = SmsController(client)
        ctrl.set_messages([])
        ctrl.delete()
        client.delete_sms.assert_not_called()


class TestViewport:
    def test_initial_offset_is_zero(self):
        ctrl = SmsController(MagicMock(), viewport_size=3)
        ctrl.set_messages(MANY_SMS)
        assert ctrl.scroll_offset == 0

    def test_visible_messages(self):
        ctrl = SmsController(MagicMock(), viewport_size=3)
        ctrl.set_messages(MANY_SMS)
        assert len(ctrl.visible_messages) == 3
        assert ctrl.visible_messages[0]["index"] == "1"

    def test_scroll_follows_cursor_down(self):
        ctrl = SmsController(MagicMock(), viewport_size=3)
        ctrl.set_messages(MANY_SMS)
        for _ in range(4):
            ctrl.move_down()
        assert ctrl.cursor == 4
        assert ctrl.scroll_offset == 2
        assert ctrl.visible_messages[0]["index"] == "3"

    def test_scroll_follows_cursor_up(self):
        ctrl = SmsController(MagicMock(), viewport_size=3)
        ctrl.set_messages(MANY_SMS)
        for _ in range(5):
            ctrl.move_down()
        ctrl.move_up()
        ctrl.move_up()
        ctrl.move_up()
        assert ctrl.scroll_offset <= ctrl.cursor

    def test_cursor_relative_to_viewport(self):
        ctrl = SmsController(MagicMock(), viewport_size=3)
        ctrl.set_messages(MANY_SMS)
        for _ in range(4):
            ctrl.move_down()
        assert ctrl.cursor_in_viewport == 2

    def test_scrollbar_position(self):
        ctrl = SmsController(MagicMock(), viewport_size=3)
        ctrl.set_messages(MANY_SMS)
        pos, total = ctrl.scrollbar_info
        assert total == 10
        assert pos == 0

    def test_scrollbar_moves_with_scroll(self):
        ctrl = SmsController(MagicMock(), viewport_size=3)
        ctrl.set_messages(MANY_SMS)
        for _ in range(9):
            ctrl.move_down()
        pos, total = ctrl.scrollbar_info
        assert pos > 0

    def test_no_viewport_shows_all(self):
        ctrl = SmsController(MagicMock())
        ctrl.set_messages(MANY_SMS)
        assert len(ctrl.visible_messages) == 10

    def test_wrap_down_resets_scroll(self):
        ctrl = SmsController(MagicMock(), viewport_size=3)
        ctrl.set_messages(MANY_SMS)
        for _ in range(10):
            ctrl.move_down()
        assert ctrl.cursor == 0
        assert ctrl.scroll_offset == 0
