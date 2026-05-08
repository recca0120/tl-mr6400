from tl_mr6400.formatter import colorize, Table, signal_bar, level_bar


class TestColorize:
    def test_bold(self):
        result = colorize("hello", bold=True)
        assert result == "\033[1mhello\033[0m"

    def test_color(self):
        result = colorize("hello", color="green")
        assert result == "\033[32mhello\033[0m"

    def test_bold_and_color(self):
        result = colorize("hello", color="cyan", bold=True)
        assert result == "\033[1m\033[36mhello\033[0m"

    def test_no_style(self):
        assert colorize("hello") == "hello"

    def test_unknown_color_ignored(self):
        assert colorize("hello", color="pink") == "hello"


class TestTable:
    def test_renders_key_value_pairs(self):
        t = Table()
        t.add("Name", "Alice")
        t.add("Age", "30")
        output = t.render()
        lines = output.strip().split("\n")
        assert "Name" in lines[0]
        assert "Alice" in lines[0]
        assert "Age" in lines[1]
        assert "30" in lines[1]

    def test_aligns_values(self):
        import re
        strip_ansi = lambda s: re.sub(r"\033\[[0-9;]*m", "", s)
        t = Table()
        t.add("Short", "val1")
        t.add("Longer Key", "val2")
        output = t.render()
        lines = output.rstrip("\n").split("\n")
        colon_pos_0 = strip_ansi(lines[0]).index(" : ")
        colon_pos_1 = strip_ansi(lines[1]).index(" : ")
        assert colon_pos_0 == colon_pos_1

    def test_with_section_header(self):
        t = Table()
        t.section("My Section")
        t.add("Key", "Val")
        output = t.render()
        assert "My Section" in output

    def test_empty_table(self):
        t = Table()
        assert t.render() == ""


class TestSignalBar:
    def test_full(self):
        result = signal_bar(4, 4)
        assert "▰" * 4 in result
        assert "▱" not in result

    def test_empty(self):
        result = signal_bar(0, 4)
        assert "▱" * 4 in result
        assert "▰" not in result

    def test_partial(self):
        result = signal_bar(2, 4)
        assert result.count("▰") == 2
        assert result.count("▱") == 2

    def test_includes_fraction(self):
        result = signal_bar(3, 4)
        assert "3/4" in result


class TestLevelBar:
    def test_good_rsrp(self):
        result = level_bar(-70, -140, -44, width=10)
        assert "█" in result

    def test_bad_rsrp(self):
        result = level_bar(-130, -140, -44, width=10)
        filled = result.count("█")
        assert filled <= 2

    def test_includes_value(self):
        result = level_bar(-92, -140, -44, width=10)
        assert "-92" in result

    def test_clamps_above_max(self):
        result = level_bar(-30, -140, -44, width=10)
        assert "█" * 10 in result

    def test_clamps_below_min(self):
        result = level_bar(-150, -140, -44, width=10)
        assert "░" * 10 in result
