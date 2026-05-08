package dashboard

import "testing"

func smsFixtures() []map[string]string {
	return []map[string]string{
		{"index": "3", "__stack": "1,0,0,0,0,0", "from": "A", "content": "hi", "unread": "1"},
		{"index": "2", "__stack": "2,0,0,0,0,0", "from": "B", "content": "yo", "unread": "0"},
		{"index": "1", "__stack": "3,0,0,0,0,0", "from": "C", "content": "ok", "unread": "1"},
	}
}

func manySMS(n int) []map[string]string {
	msgs := make([]map[string]string, n)
	for i := range n {
		msgs[i] = map[string]string{
			"index": string(rune('0' + i)), "__stack": "1,0,0,0,0,0",
			"from": "X", "content": "m", "unread": "1",
		}
	}
	return msgs
}

type fakeClient struct {
	readStack   string
	deleteStack string
}

func (f *fakeClient) SetSMSRead(stack string)  { f.readStack = stack }
func (f *fakeClient) DeleteSMS(stack string)    { f.deleteStack = stack }

func TestSMSController_InitialCursor(t *testing.T) {
	c := NewSMSController(nil, 0)
	c.SetMessages(smsFixtures())
	if c.Cursor() != 0 {
		t.Errorf("cursor = %d, want 0", c.Cursor())
	}
}

func TestSMSController_MoveDown(t *testing.T) {
	c := NewSMSController(nil, 0)
	c.SetMessages(smsFixtures())
	c.MoveDown()
	if c.Cursor() != 1 {
		t.Errorf("cursor = %d, want 1", c.Cursor())
	}
}

func TestSMSController_MoveDownWraps(t *testing.T) {
	c := NewSMSController(nil, 0)
	c.SetMessages(smsFixtures())
	c.MoveDown()
	c.MoveDown()
	c.MoveDown()
	if c.Cursor() != 0 {
		t.Errorf("cursor = %d, want 0", c.Cursor())
	}
}

func TestSMSController_MoveUpWraps(t *testing.T) {
	c := NewSMSController(nil, 0)
	c.SetMessages(smsFixtures())
	c.MoveUp()
	if c.Cursor() != 2 {
		t.Errorf("cursor = %d, want 2", c.Cursor())
	}
}

func TestSMSController_EmptyNocrash(t *testing.T) {
	c := NewSMSController(nil, 0)
	c.SetMessages(nil)
	c.MoveDown()
	c.MoveUp()
	if c.Cursor() != 0 {
		t.Errorf("cursor = %d, want 0", c.Cursor())
	}
}

func TestSMSController_MarkRead(t *testing.T) {
	fc := &fakeClient{}
	c := NewSMSController(fc, 0)
	c.SetMessages(smsFixtures())
	c.MarkRead()
	if fc.readStack != "1,0,0,0,0,0" {
		t.Errorf("readStack = %q", fc.readStack)
	}
	if c.Messages()[0]["unread"] != "0" {
		t.Error("expected unread=0")
	}
}

func TestSMSController_MarkReadNoop(t *testing.T) {
	fc := &fakeClient{}
	c := NewSMSController(fc, 0)
	c.SetMessages(smsFixtures())
	c.MoveDown()
	c.MarkRead()
	if fc.readStack != "" {
		t.Error("should not call SetSMSRead on already read")
	}
}

func TestSMSController_Delete(t *testing.T) {
	fc := &fakeClient{}
	c := NewSMSController(fc, 0)
	c.SetMessages(smsFixtures())
	c.Delete()
	if fc.deleteStack != "1,0,0,0,0,0" {
		t.Errorf("deleteStack = %q", fc.deleteStack)
	}
	if len(c.Messages()) != 2 {
		t.Errorf("len = %d, want 2", len(c.Messages()))
	}
}

func TestSMSController_Viewport(t *testing.T) {
	c := NewSMSController(nil, 3)
	c.SetMessages(manySMS(10))
	if len(c.VisibleMessages()) != 3 {
		t.Errorf("visible = %d, want 3", len(c.VisibleMessages()))
	}
	for range 4 {
		c.MoveDown()
	}
	if c.ScrollOffset() < 2 {
		t.Errorf("offset = %d, want >= 2", c.ScrollOffset())
	}
}

func TestSMSController_ScrollbarInfo(t *testing.T) {
	c := NewSMSController(nil, 3)
	c.SetMessages(manySMS(10))
	pos, total := c.ScrollbarInfo()
	if total != 10 {
		t.Errorf("total = %d, want 10", total)
	}
	if pos != 0 {
		t.Errorf("pos = %d, want 0", pos)
	}
}
