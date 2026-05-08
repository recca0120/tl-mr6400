from tl_mr6400.formatter import colorize, Table


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
