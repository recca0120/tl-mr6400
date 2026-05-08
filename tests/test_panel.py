from tl_mr6400.panel import Panel, PanelGrid


class TestPanel:
    def test_renders_box_with_title(self):
        p = Panel("Signal", width=20, height=5)
        p.add("RSRP", "-92 dBm")
        lines = p.render()
        assert len(lines) == 5
        assert "Signal" in lines[0]
        assert "┌" in lines[0]
        assert "┐" in lines[0]
        assert "└" in lines[-1]
        assert "┘" in lines[-1]

    def test_renders_key_value_inside(self):
        p = Panel("Test", width=25, height=5)
        p.add("Key", "Val")
        lines = p.render()
        content = "".join(lines)
        assert "Key" in content
        assert "Val" in content

    def test_truncates_long_values(self):
        p = Panel("T", width=20, height=5)
        p.add("K", "A" * 50)
        lines = p.render()
        for line in lines:
            assert len(line) == 20

    def test_add_raw_renders_freeform_text(self):
        p = Panel("T", width=30, height=5)
        p.add_raw("  hello world")
        lines = p.render()
        content = "".join(lines)
        assert "hello world" in content

    def test_pads_empty_rows(self):
        p = Panel("T", width=20, height=6)
        p.add("A", "1")
        lines = p.render()
        assert len(lines) == 6
        for line in lines:
            assert line.startswith("│") or line.startswith("┌") or line.startswith("└")


class TestPanelGrid:
    def test_side_by_side(self):
        p1 = Panel("Left", width=15, height=4)
        p1.add("A", "1")
        p2 = Panel("Right", width=15, height=4)
        p2.add("B", "2")
        lines = PanelGrid.horizontal([p1, p2])
        assert len(lines) == 4
        for line in lines:
            assert len(line) == 30

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
        for line in lines:
            assert len(line) == 30
