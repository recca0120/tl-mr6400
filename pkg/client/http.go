package client

import (
	"io"
	"net/http"
	"net/http/cookiejar"
	"strings"
	"time"
)

type realHTTPClient struct {
	client *http.Client
}

func NewHTTPClient() HTTPClient {
	jar, _ := cookiejar.New(nil)
	return &realHTTPClient{
		client: &http.Client{
			Jar:     jar,
			Timeout: 5 * time.Second,
		},
	}
}

func (h *realHTTPClient) Get(url string, headers map[string]string) HTTPResponse {
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return HTTPResponse{Err: err}
	}
	for k, v := range headers {
		req.Header.Set(k, v)
	}
	return h.do(req)
}

func (h *realHTTPClient) Post(url string, data string, headers map[string]string) HTTPResponse {
	var body io.Reader
	if data != "" {
		body = strings.NewReader(data)
	}
	req, err := http.NewRequest("POST", url, body)
	if err != nil {
		return HTTPResponse{Err: err}
	}
	for k, v := range headers {
		req.Header.Set(k, v)
	}
	return h.do(req)
}

func (h *realHTTPClient) do(req *http.Request) HTTPResponse {
	resp, err := h.client.Do(req)
	if err != nil {
		return HTTPResponse{Err: err}
	}
	defer resp.Body.Close()
	b, err := io.ReadAll(resp.Body)
	if err != nil {
		return HTTPResponse{StatusCode: resp.StatusCode, Err: err}
	}
	return HTTPResponse{StatusCode: resp.StatusCode, Body: string(b)}
}
