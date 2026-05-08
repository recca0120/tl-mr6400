package dashboard

import (
	"strings"

	"github.com/mattn/go-runewidth"
)

type panelRow struct {
	key, val string
	raw      bool
}

type Panel struct {
	title        string
	width        int
	height       int
	padding      int
	scrollOffset int
	rows         []panelRow
}

func NewPanel(title string, width, height int) *Panel {
	return &Panel{title: title, width: width, height: height}
}

func (p *Panel) SetPadding(n int)      { p.padding = n }
func (p *Panel) SetScrollOffset(n int) { p.scrollOffset = n }

func (p *Panel) AddKV(key, val string) {
	p.rows = append(p.rows, panelRow{key: key, val: val})
}

func (p *Panel) AddRaw(text string) {
	p.rows = append(p.rows, panelRow{val: text, raw: true})
}

func (p *Panel) Render() []string {
	inner := p.width - 2

	titleText := " " + p.title + " "
	barLen := inner - runewidth.StringWidth(titleText)
	left := barLen / 2
	right := barLen - left
	top := "┌" + strings.Repeat("─", left) + titleText + strings.Repeat("─", right) + "┐"
	bottom := "└" + strings.Repeat("─", inner) + "┘"

	allContent := p.renderRows(inner)
	contentH := p.height - 2
	needScroll := len(allContent) > contentH

	visible := allContent
	if needScroll {
		end := p.scrollOffset + contentH
		if end > len(allContent) {
			end = len(allContent)
		}
		visible = allContent[p.scrollOffset:end]
	}

	empty := "│" + strings.Repeat(" ", inner) + "│"
	for len(visible) < contentH {
		visible = append(visible, empty)
	}

	if needScroll {
		visible = applyScrollbar(visible, p.scrollOffset, len(allContent), contentH)
	}

	lines := make([]string, 0, p.height)
	lines = append(lines, top)
	lines = append(lines, visible...)
	lines = append(lines, bottom)
	return lines
}

func (p *Panel) renderRows(inner int) []string {
	pad := p.padding
	contentW := inner - pad*2

	maxKey := 0
	for _, r := range p.rows {
		if !r.raw && runewidth.StringWidth(r.key) > maxKey {
			maxKey = runewidth.StringWidth(r.key)
		}
	}

	var lines []string
	for _, r := range p.rows {
		var text string
		if r.raw {
			text = truncatePad(r.val, contentW)
		} else {
			prefix := " " + padRight(r.key, maxKey) + ": "
			remaining := contentW - runewidth.StringWidth(prefix)
			text = prefix + truncatePad(r.val, remaining)
		}
		padStr := strings.Repeat(" ", pad)
		lines = append(lines, "│"+padStr+text+padStr+"│")
	}
	return lines
}

func applyScrollbar(lines []string, offset, total, trackH int) []string {
	if total <= trackH {
		return lines
	}
	thumbSize := max(1, trackH*trackH/total)
	thumbPos := trackH * offset / total
	thumbPos = min(thumbPos, trackH-thumbSize)

	result := make([]string, len(lines))
	for i, line := range lines {
		ch := "│"
		if i >= thumbPos && i < thumbPos+thumbSize {
			ch = "┃"
		}
		runes := []rune(line)
		if len(runes) > 0 {
			runes[len(runes)-1] = []rune(ch)[0]
		}
		result[i] = string(runes)
	}
	return result
}

func truncatePad(s string, width int) string {
	s = truncate(s, width)
	return padRight(s, width)
}

func truncate(s string, width int) string {
	w := 0
	for i, ch := range s {
		cw := runewidth.RuneWidth(ch)
		if w+cw > width {
			return s[:i] + strings.Repeat(" ", width-w)
		}
		w += cw
	}
	return s
}

func padRight(s string, width int) string {
	w := runewidth.StringWidth(s)
	if w >= width {
		return s
	}
	return s + strings.Repeat(" ", width-w)
}
