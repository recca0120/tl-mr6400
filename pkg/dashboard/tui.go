package dashboard

import (
	"fmt"
	"time"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"github.com/recca0120/tl-mr6400/pkg/client"
)

type tickMsg time.Time

type Model struct {
	client   *client.Client
	smsCtrl  *SMSController
	status   map[string]string
	wlan     map[string]string
	lan      map[string]string
	width    int
	height   int
	interval time.Duration
	quitting bool
}

func NewModel(c *client.Client, interval time.Duration) *Model {
	return &Model{
		client:   c,
		smsCtrl:  NewSMSController(c, smsViewportSize),
		interval: interval,
		width:    80,
		height:   24,
	}
}

func (m *Model) Init() tea.Cmd {
	return tea.Batch(m.fetchData, m.tick())
}

func (m *Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "q", "ctrl+c":
			m.quitting = true
			return m, tea.Quit
		case "j", "down":
			m.smsCtrl.MoveDown()
		case "k", "up":
			m.smsCtrl.MoveUp()
		case "d":
			m.smsCtrl.Delete()
		case "m":
			m.smsCtrl.MarkRead()
		case "r":
			return m, m.fetchData
		}
	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
	case fetchResultMsg:
		m.status = msg.status
		m.wlan = msg.wlan
		m.lan = msg.lan
		m.mergeAndSetSMS(msg.sms)
	case tickMsg:
		return m, tea.Batch(m.fetchData, m.tick())
	}
	return m, nil
}

func (m *Model) View() string {
	if m.quitting {
		return ""
	}
	titleStyle := lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("14"))
	title := titleStyle.Render(fmt.Sprintf(" TL-MR6400 Dashboard  [%s] ", time.Now().Format("15:04:05")))

	body := RenderDashboard(m.status, m.smsCtrl.Messages(), m.wlan, m.lan, m.width, m.smsCtrl.Cursor(), m.smsCtrl.ScrollOffset())

	statusBar := lipgloss.NewStyle().Reverse(true).Width(m.width).Render(
		" q:quit  r:refresh  ↑↓/jk:select  d:delete  m:mark read ",
	)

	return title + "\n\n" + body + "\n" + statusBar
}

func (m *Model) mergeAndSetSMS(fresh []map[string]string) {
	localRead := make(map[string]bool)
	for _, msg := range m.smsCtrl.Messages() {
		if msg["unread"] != unreadTrue {
			localRead[msg["__stack"]] = true
		}
	}
	for _, msg := range fresh {
		if localRead[msg["__stack"]] {
			msg["unread"] = "0"
		}
	}
	m.smsCtrl.SetMessages(fresh)
}

type fetchResultMsg struct {
	status, wlan, lan map[string]string
	sms               []map[string]string
}

func (m *Model) fetchData() tea.Msg {
	return fetchResultMsg{
		status: m.client.GetStatus(),
		wlan:   m.client.GetWLAN(),
		lan:    m.client.GetLAN(),
		sms:    m.client.GetSMS(1),
	}
}

func (m *Model) tick() tea.Cmd {
	return tea.Tick(m.interval, func(t time.Time) tea.Msg {
		return tickMsg(t)
	})
}

func RunDashboard(c *client.Client, interval time.Duration) error {
	p := tea.NewProgram(NewModel(c, interval), tea.WithAltScreen())
	_, err := p.Run()
	return err
}
