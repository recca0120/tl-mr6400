import pytest
from unittest.mock import MagicMock
from tl_mr6400.sms_controller import SmsController


SMS_DATA = [
    {"index": "124", "from": "935188", "content": "Hello", "receivedTime": "2026-05-08 12:06:08", "unread": "1"},
    {"index": "123", "from": "091234", "content": "World", "receivedTime": "2026-05-07 10:09:22", "unread": "0"},
    {"index": "122", "from": "555555", "content": "Test", "receivedTime": "2026-05-06 09:00:00", "unread": "1"},
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
