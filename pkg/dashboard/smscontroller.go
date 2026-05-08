package dashboard

type SMSClient interface {
	SetSMSRead(stack string)
	DeleteSMS(stack string)
}

type SMSController struct {
	client       SMSClient
	messages     []map[string]string
	cursor       int
	scrollOffset int
	viewportSize int
}

func (s *SMSController) Messages() []map[string]string { return s.messages }
func (s *SMSController) Cursor() int                   { return s.cursor }
func (s *SMSController) ScrollOffset() int              { return s.scrollOffset }

func NewSMSController(client SMSClient, viewportSize int) *SMSController {
	return &SMSController{client: client, viewportSize: viewportSize}
}

func (s *SMSController) SetMessages(msgs []map[string]string) {
	s.messages = make([]map[string]string, len(msgs))
	for i, m := range msgs {
		cp := make(map[string]string, len(m))
		for k, v := range m {
			cp[k] = v
		}
		s.messages[i] = cp
	}
	if s.cursor >= len(s.messages) {
		s.cursor = max(0, len(s.messages)-1)
	}
	s.adjustScroll()
}

func (s *SMSController) Selected() map[string]string {
	if len(s.messages) == 0 {
		return nil
	}
	return s.messages[s.cursor]
}

func (s *SMSController) VisibleMessages() []map[string]string {
	if s.viewportSize <= 0 {
		return s.messages
	}
	end := s.scrollOffset + s.viewportSize
	if end > len(s.messages) {
		end = len(s.messages)
	}
	return s.messages[s.scrollOffset:end]
}

func (s *SMSController) CursorInViewport() int {
	return s.cursor - s.scrollOffset
}

func (s *SMSController) ScrollbarInfo() (offset, total int) {
	return s.scrollOffset, len(s.messages)
}

func (s *SMSController) MoveDown() {
	if len(s.messages) == 0 {
		return
	}
	s.cursor = (s.cursor + 1) % len(s.messages)
	if s.cursor == 0 {
		s.scrollOffset = 0
	} else {
		s.adjustScroll()
	}
}

func (s *SMSController) MoveUp() {
	if len(s.messages) == 0 {
		return
	}
	s.cursor = (s.cursor - 1 + len(s.messages)) % len(s.messages)
	if s.cursor == len(s.messages)-1 {
		s.scrollToEnd()
	} else {
		s.adjustScroll()
	}
}

func (s *SMSController) MarkRead() {
	msg := s.Selected()
	if msg == nil || msg["unread"] != unreadTrue {
		return
	}
	s.client.SetSMSRead(msg["__stack"])
	msg["unread"] = "0"
}

func (s *SMSController) Delete() {
	msg := s.Selected()
	if msg == nil {
		return
	}
	s.client.DeleteSMS(msg["__stack"])
	s.messages = append(s.messages[:s.cursor], s.messages[s.cursor+1:]...)
	if len(s.messages) > 0 {
		s.cursor = min(s.cursor, len(s.messages)-1)
	} else {
		s.cursor = 0
	}
	s.adjustScroll()
}

func (s *SMSController) adjustScroll() {
	if s.viewportSize <= 0 || len(s.messages) == 0 {
		s.scrollOffset = 0
		return
	}
	if s.cursor < s.scrollOffset {
		s.scrollOffset = s.cursor
	} else if s.cursor >= s.scrollOffset+s.viewportSize {
		s.scrollOffset = s.cursor - s.viewportSize + 1
	}
	maxOff := max(0, len(s.messages)-s.viewportSize)
	s.scrollOffset = min(s.scrollOffset, maxOff)
}

func (s *SMSController) scrollToEnd() {
	if s.viewportSize <= 0 {
		return
	}
	s.scrollOffset = max(0, len(s.messages)-s.viewportSize)
}
