from tl_mr6400.panel import Panel, PanelGrid, display_width


class TestDisplayWidth:
    def test_ascii(self):
        assert display_width("hello") == 5

    def test_chinese(self):
        assert display_width("你好") == 4

    def test_mixed(self):
        assert display_width("hi你好") == 6

    def test_empty(self):
        assert display_width("") == 0

    def test_box_chars(self):
        assert display_width("┌─┐") == 3


class TestPanel:
    def test_renders_box_with_title(self):
        p = Panel("Signal", width=20, height=5)
        p.add("RSRP", "-92 dBm")
        lines = p.render()
        assert len(lines) == 5
        assert "Signal" in lines[0][0]
        assert "┌" in lines[0][0]
        assert "┐" in lines[0][0]
        assert "└" in lines[-1][0]

    def test_renders_key_value_inside(self):
        p = Panel("Test", width=25, height=5)
        p.add("Key", "Val")
        lines = p.render()
        content = "".join(t for t, _ in lines)
        assert "Key" in content
        assert "Val" in content

    def test_truncates_long_values(self):
        p = Panel("T", width=20, height=5)
        p.add("K", "A" * 50)
        lines = p.render()
        for text, _ in lines:
            assert display_width(text) == 20

    def test_add_raw_renders_freeform_text(self):
        p = Panel("T", width=30, height=5)
        p.add_raw("  hello world")
        lines = p.render()
        content = "".join(t for t, _ in lines)
        assert "hello world" in content

    def test_truncates_chinese_by_display_width(self):
        p = Panel("T", width=20, height=4)
        p.add_raw("你好世界測試中文字串超長文字")
        lines = p.render()
        for text, _ in lines:
            assert display_width(text) == 20

    def test_pads_chinese_content_correctly(self):
        p = Panel("T", width=20, height=4)
        p.add_raw("你好")
        lines = p.render()
        for text, _ in lines:
            assert display_width(text) == 20

    def test_pads_empty_rows(self):
        p = Panel("T", width=20, height=6)
        p.add("A", "1")
        lines = p.render()
        assert len(lines) == 6
        for text, _ in lines:
            assert text.startswith("│") or text.startswith("┌") or text.startswith("└")

    def test_returns_tuples_with_styles(self):
        p = Panel("T", width=20, height=4)
        p.add("K", "V", style="key")
        lines = p.render()
        assert lines[0][1] == "title"
        assert lines[1][1] == "key"
        assert lines[-1][1] == "border"

    def test_custom_raw_style(self):
        p = Panel("T", width=20, height=4)
        p.add_raw("text", style="sms_unread")
        lines = p.render()
        assert lines[1][1] == "sms_unread"


class TestPanelGrid:
    def test_side_by_side(self):
        p1 = Panel("Left", width=15, height=4)
        p1.add("A", "1")
        p2 = Panel("Right", width=15, height=4)
        p2.add("B", "2")
        lines = PanelGrid.horizontal([p1, p2])
        assert len(lines) == 4
        for text, _ in lines:
            assert len(text) == 30

    def test_vertical_stack(self):
        p1 = Panel("Top", width=20, height=3)
        p2 = Panel("Bot", width=20, height=3)
        lines = PanelGrid.vertical([p1, p2])
        assert len(lines) == 6

    def test_horizontal_different_heights_pads(self):
        p1 = Panel("Tall", width=15, height=5)
        p1.add("A", "1")
        p1.add("B", "2")
        p2 = Panel("Short", width=15, height=3)
        p2.add("C", "3")
        lines = PanelGrid.horizontal([p1, p2])
        assert len(lines) == 5
        for text, _ in lines:
            assert len(text) == 30

    def test_returns_styled_tuples(self):
        p1 = Panel("L", width=10, height=3)
        p2 = Panel("R", width=10, height=3)
        lines = PanelGrid.horizontal([p1, p2])
        for text, style in lines:
            assert isinstance(style, str)
