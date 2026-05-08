package dashboard

import (
	"strings"
	"testing"

	"github.com/mattn/go-runewidth"
)

func TestPanel_BoxBorders(t *testing.T) {
	p := NewPanel("Signal", 20, 5)
	p.AddKV("RSRP", "-92")
	lines := p.Render()
	if len(lines) != 5 {
		t.Fatalf("lines = %d, want 5", len(lines))
	}
	if !strings.Contains(lines[0], "Signal") {
		t.Error("title missing")
	}
	if !strings.HasPrefix(lines[0], "┌") || !strings.HasSuffix(lines[0], "┐") {
		t.Error("top border wrong")
	}
	if !strings.HasPrefix(lines[4], "└") || !strings.HasSuffix(lines[4], "┘") {
		t.Error("bottom border wrong")
	}
}

func TestPanel_KeyValueInside(t *testing.T) {
	p := NewPanel("T", 25, 5)
	p.AddKV("Key", "Val")
	lines := p.Render()
	joined := strings.Join(lines, "")
	if !strings.Contains(joined, "Key") || !strings.Contains(joined, "Val") {
		t.Error("key/value missing")
	}
}

func TestPanel_ConsistentWidth(t *testing.T) {
	p := NewPanel("T", 30, 5)
	p.AddKV("Short", "a")
	p.AddKV("Longer Key", "b")
	for _, line := range p.Render() {
		w := runewidth.StringWidth(line)
		if w != 30 {
			t.Errorf("width = %d, want 30: %q", w, line)
		}
	}
}

func TestPanel_AddRaw(t *testing.T) {
	p := NewPanel("T", 30, 5)
	p.AddRaw("  hello world")
	lines := p.Render()
	joined := strings.Join(lines, "")
	if !strings.Contains(joined, "hello world") {
		t.Error("raw text missing")
	}
}

func TestPanel_ChineseTruncate(t *testing.T) {
	p := NewPanel("T", 20, 4)
	p.AddRaw("你好世界測試中文字串超長")
	for _, line := range p.Render() {
		w := runewidth.StringWidth(line)
		if w != 20 {
			t.Errorf("width = %d, want 20: %q", w, line)
		}
	}
}

func TestPanel_Padding(t *testing.T) {
	p := NewPanel("T", 30, 5)
	p.SetPadding(1)
	p.AddRaw("hello")
	lines := p.Render()
	// content line should have padding space after │ and before │
	content := lines[1]
	// after │ there should be at least 1 space before content
	if !strings.HasPrefix(content, "│ ") {
		t.Errorf("missing left padding: %q", content)
	}
	// before closing │ there should be at least 1 space
	if !strings.HasSuffix(content, " │") {
		t.Errorf("missing right padding: %q", content)
	}
	// width still consistent
	w := runewidth.StringWidth(content)
	if w != 30 {
		t.Errorf("width = %d, want 30: %q", w, content)
	}
}

func TestPanel_ScrollbarWhenOverflow(t *testing.T) {
	p := NewPanel("T", 20, 6)
	for i := 0; i < 10; i++ {
		p.AddRaw("line")
	}
	lines := p.Render()
	if len(lines) != 6 {
		t.Fatalf("lines = %d, want 6", len(lines))
	}
	// should have scrollbar thumb ┃ somewhere
	joined := strings.Join(lines, "")
	if !strings.Contains(joined, "┃") {
		t.Error("missing scrollbar thumb ┃")
	}
}

func TestPanel_NoScrollbarWhenFits(t *testing.T) {
	p := NewPanel("T", 20, 6)
	p.AddRaw("line1")
	p.AddRaw("line2")
	lines := p.Render()
	joined := strings.Join(lines, "")
	if strings.Contains(joined, "┃") {
		t.Error("should not have scrollbar when content fits")
	}
}

func TestPanel_ScrollOffset(t *testing.T) {
	p := NewPanel("T", 20, 5)
	p.SetScrollOffset(2)
	for i := 0; i < 10; i++ {
		p.AddRaw(strings.Repeat(string(rune('A'+i)), 5))
	}
	lines := p.Render()
	// content should start from offset 2 (third item = "CCCCC")
	if !strings.Contains(lines[1], "CCCCC") {
		t.Errorf("expected offset content 'CCCCC' in: %q", lines[1])
	}
}

func TestPanel_PadsEmptyRows(t *testing.T) {
	p := NewPanel("T", 20, 6)
	p.AddKV("A", "1")
	lines := p.Render()
	if len(lines) != 6 {
		t.Errorf("lines = %d, want 6", len(lines))
	}
	for _, line := range lines {
		if !strings.HasPrefix(line, "│") && !strings.HasPrefix(line, "┌") && !strings.HasPrefix(line, "└") {
			t.Errorf("unexpected prefix: %q", line)
		}
	}
}
