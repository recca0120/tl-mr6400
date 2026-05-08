package client

import (
	"fmt"
	"strings"
	"testing"
)

const rsaResponse = `var ee="010001";
var nn="C7DC6CB6F1979B9E1008A1F09A606B03FAF8BCDA541FC9D0C4DD3A8106D23BBF8044D37992F727B10A90EE59EED852714E5217CFDC0C7E02137067B412CF9CCB9F117D3E05935BD3DFE180EE0A47DF9BD1689FBD9CDC4CE2ACCBBCEE24890E241727A7EBCDDF3BE3552CC3AC35C8DB230B8A909697C128A72F7B86F08B6CB469";
var userSetting=1;
$.ret=0;`

const tokenPage = `var token="abc123token"; some html`

const smsResponse = "[1,0,0,0,0,0]1\nindex=124\nfrom=935188\ncontent=Hello\nreceivedTime=2026-05-08 12:06:08\nunread=1\n[error]0\n"

const statusResponse = "[2,1,0,0,0,0]0\nsigLevel=2\nconnStat=4\nnetType=3\n[2,1,1,0,0,0]1\nconnectionStatus=Connected\nexternalIPAddress=10.2.153.186\n[error]0\n"

type mockHTTP struct {
	getResponses []HTTPResponse
	postResponse HTTPResponse
	getCalls     int
	postCalls    int
	lastPostURL  string
	lastPostData string
}

func (m *mockHTTP) Get(url string, headers map[string]string) HTTPResponse {
	idx := m.getCalls
	m.getCalls++
	if idx < len(m.getResponses) {
		return m.getResponses[idx]
	}
	return HTTPResponse{}
}

func (m *mockHTTP) Post(url string, data string, headers map[string]string) HTTPResponse {
	m.postCalls++
	m.lastPostURL = url
	m.lastPostData = data
	return m.postResponse
}

func TestLogin_Success(t *testing.T) {
	mock := &mockHTTP{
		getResponses: []HTTPResponse{
			{StatusCode: 200, Body: rsaResponse},
			{StatusCode: 200, Body: tokenPage},
		},
		postResponse: HTTPResponse{StatusCode: 200, Body: "$.ret=0;"},
	}
	c := New("http://192.168.1.1", "admin", WithHTTP(mock))
	err := c.Login()
	if err != nil {
		t.Fatal(err)
	}
	if c.token != "abc123token" {
		t.Errorf("token = %q, want %q", c.token, "abc123token")
	}
	if mock.getCalls != 2 {
		t.Errorf("getCalls = %d, want 2", mock.getCalls)
	}
	if mock.postCalls != 1 {
		t.Errorf("postCalls = %d, want 1", mock.postCalls)
	}
}


func TestLogin_Failure(t *testing.T) {
	mock := &mockHTTP{
		getResponses: []HTTPResponse{
			{StatusCode: 200, Body: rsaResponse},
		},
		postResponse: HTTPResponse{StatusCode: 200, Body: "$.ret=-1;"},
	}
	c := New("http://192.168.1.1", "admin", WithHTTP(mock))
	err := c.Login()
	if err == nil {
		t.Error("expected error, got nil")
	}
}

func TestLogin_MissingToken(t *testing.T) {
	mock := &mockHTTP{
		getResponses: []HTTPResponse{
			{StatusCode: 200, Body: rsaResponse},
			{StatusCode: 200, Body: "<html>no token</html>"},
		},
		postResponse: HTTPResponse{StatusCode: 200, Body: "$.ret=0;"},
	}
	c := New("http://192.168.1.1", "admin", WithHTTP(mock))
	err := c.Login()
	if err == nil {
		t.Error("expected error, got nil")
	}
}

func TestLogin_HTTPError_ShowsRealError(t *testing.T) {
	mock := &mockHTTP{
		getResponses: []HTTPResponse{
			{StatusCode: 0, Body: "", Err: fmt.Errorf("dial tcp 192.168.1.1:80: connect: no route to host")},
		},
	}
	c := New("http://192.168.1.1", "admin", WithHTTP(mock))
	err := c.Login()
	if err == nil {
		t.Fatal("expected error")
	}
	if !strings.Contains(err.Error(), "no route to host") {
		t.Errorf("error should contain real cause, got: %v", err)
	}
}

func TestLogin_403_ShowsStatusCode(t *testing.T) {
	mock := &mockHTTP{
		getResponses: []HTTPResponse{
			{StatusCode: 403, Body: "Forbidden"},
		},
	}
	c := New("http://192.168.1.1", "admin", WithHTTP(mock))
	err := c.Login()
	if err == nil {
		t.Fatal("expected error")
	}
	if !strings.Contains(err.Error(), "403") {
		t.Errorf("error should mention status code, got: %v", err)
	}
}

func TestGetSMS(t *testing.T) {
	mock := &mockHTTP{
		postResponse: HTTPResponse{StatusCode: 200, Body: smsResponse},
	}
	c := New("http://192.168.1.1", "admin", WithHTTP(mock))
	c.token = "fake"
	msgs := c.GetSMS(1)
	if len(msgs) != 1 {
		t.Fatalf("len = %d, want 1", len(msgs))
	}
	if msgs[0]["from"] != "935188" {
		t.Errorf("from = %q, want %q", msgs[0]["from"], "935188")
	}
}

func TestGetSMS_HTTPError(t *testing.T) {
	mock := &mockHTTP{
		postResponse: HTTPResponse{StatusCode: 500, Body: ""},
	}
	c := New("http://192.168.1.1", "admin", WithHTTP(mock))
	c.token = "fake"
	msgs := c.GetSMS(1)
	if len(msgs) != 0 {
		t.Errorf("len = %d, want 0", len(msgs))
	}
}

func TestGetStatus(t *testing.T) {
	mock := &mockHTTP{
		postResponse: HTTPResponse{StatusCode: 200, Body: statusResponse},
	}
	c := New("http://192.168.1.1", "admin", WithHTTP(mock))
	c.token = "fake"
	status := c.GetStatus()
	if status["sigLevel"] != "2" {
		t.Errorf("sigLevel = %q, want %q", status["sigLevel"], "2")
	}
	if status["externalIPAddress"] != "10.2.153.186" {
		t.Errorf("ip = %q, want %q", status["externalIPAddress"], "10.2.153.186")
	}
}

func TestSetSMSRead(t *testing.T) {
	mock := &mockHTTP{
		postResponse: HTTPResponse{StatusCode: 200, Body: "[error]0\n"},
	}
	c := New("http://192.168.1.1", "admin", WithHTTP(mock))
	c.token = "fake"
	c.SetSMSRead("1,0,0,0,0,0")
	if !strings.Contains(mock.lastPostURL, "cgi?2") {
		t.Errorf("url = %q, want cgi?2", mock.lastPostURL)
	}
	if !strings.Contains(mock.lastPostData, "LTE_SMS_RECVMSGENTRY") {
		t.Error("data missing LTE_SMS_RECVMSGENTRY")
	}
	if !strings.Contains(mock.lastPostData, "unread=0") {
		t.Error("data missing unread=0")
	}
}

func TestDeleteSMS(t *testing.T) {
	mock := &mockHTTP{
		postResponse: HTTPResponse{StatusCode: 200, Body: "[error]0\n"},
	}
	c := New("http://192.168.1.1", "admin", WithHTTP(mock))
	c.token = "fake"
	c.DeleteSMS("1,0,0,0,0,0")
	if !strings.Contains(mock.lastPostURL, "cgi?4") {
		t.Errorf("url = %q, want cgi?4", mock.lastPostURL)
	}
	if !strings.Contains(mock.lastPostData, "1,0,0,0,0,0") {
		t.Error("data missing stack")
	}
}

func TestGetSMS_SendsTokenHeader(t *testing.T) {
	var capturedHeaders map[string]string
	mock := &mockHTTP{
		postResponse: HTTPResponse{StatusCode: 200, Body: smsResponse},
	}
	c := New("http://192.168.1.1", "admin", WithHTTP(&headerCaptureMock{
		inner:           mock,
		capturedHeaders: &capturedHeaders,
	}))
	c.token = "my_token"
	c.GetSMS(1)
	if capturedHeaders["TokenID"] != "my_token" {
		t.Errorf("TokenID = %q, want %q", capturedHeaders["TokenID"], "my_token")
	}
}

type headerCaptureMock struct {
	inner           *mockHTTP
	capturedHeaders *map[string]string
}

func (h *headerCaptureMock) Get(url string, headers map[string]string) HTTPResponse {
	return h.inner.Get(url, headers)
}

func (h *headerCaptureMock) Post(url string, data string, headers map[string]string) HTTPResponse {
	*h.capturedHeaders = headers
	return h.inner.Post(url, data, headers)
}
