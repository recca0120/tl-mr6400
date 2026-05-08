package client

import (
	"fmt"
	"strings"

	"github.com/recca0120/tl-mr6400/pkg/encryption"
	"github.com/recca0120/tl-mr6400/pkg/parser"
)

const (
	defaultUsername   = "admin"
	contentTypePlain  = "text/plain"
	loginSuccessToken = "$.ret=0;"

	actSET    = "2"
	actDEL    = "4"
	actGL     = "5"
	actSETGL  = "2&5"
	actGLGL   = "5&5"
	actGLGET  = "5&1"
)

type HTTPResponse struct {
	StatusCode int
	Body       string
	Err        error
}

type HTTPClient interface {
	Get(url string, headers map[string]string) HTTPResponse
	Post(url string, data string, headers map[string]string) HTTPResponse
}

type Option func(*Client)

func WithHTTP(h HTTPClient) Option {
	return func(c *Client) { c.http = h }
}

type Client struct {
	url      string
	password string
	username string
	http     HTTPClient
	token    string
}

func New(url, password string, opts ...Option) *Client {
	c := &Client{
		url:      strings.TrimRight(url, "/"),
		password: password,
		username: defaultUsername,
	}
	for _, o := range opts {
		o(c)
	}
	return c
}

func (c *Client) headers() map[string]string {
	h := map[string]string{"Referer": c.url + "/"}
	if c.token != "" {
		h["TokenID"] = c.token
	}
	return h
}

func (c *Client) query(actTypes, data string) []map[string]string {
	headers := c.headers()
	headers["Content-Type"] = contentTypePlain
	r := c.http.Post(fmt.Sprintf("%s/cgi?%s", c.url, actTypes), data, headers)
	if r.StatusCode != 200 {
		return nil
	}
	return parser.ParseEntries(r.Body)
}

func (c *Client) queryMerged(actTypes, data string) map[string]string {
	entries := c.query(actTypes, data)
	if len(entries) == 0 {
		return map[string]string{}
	}
	merged := make(map[string]string)
	for _, entry := range entries {
		for k, v := range entry {
			merged[k] = v
		}
	}
	return merged
}

func (c *Client) Login() error {
	r := c.http.Get(fmt.Sprintf("%s/cgi/getParm", c.url), c.headers())
	if err := checkResponse(r, "get RSA keys"); err != nil {
		return err
	}
	ee, nn, err := parser.ParseRSAKeys(r.Body)
	if err != nil {
		return err
	}

	encUser, encPass, err := encryption.EncryptCredentials(c.username, c.password, nn, ee)
	if err != nil {
		return err
	}

	loginURL := fmt.Sprintf("%s/cgi/login?UserName=%s&Passwd=%s&Action=1&LoginStatus=0", c.url, encUser, encPass)
	r = c.http.Post(loginURL, "", c.headers())
	if err := checkResponse(r, "login"); err != nil {
		return err
	}
	if !strings.Contains(r.Body, loginSuccessToken) {
		return fmt.Errorf("login failed: %s", strings.TrimSpace(r.Body))
	}

	r = c.http.Get(c.url+"/", c.headers())
	if err := checkResponse(r, "get token"); err != nil {
		return err
	}
	token, err := parser.ParseToken(r.Body)
	if err != nil {
		return err
	}
	c.token = token
	return nil
}

func checkResponse(r HTTPResponse, context string) error {
	if r.Err != nil {
		return fmt.Errorf("%s: %w", context, r.Err)
	}
	if r.StatusCode != 200 {
		return fmt.Errorf("%s: HTTP %d", context, r.StatusCode)
	}
	return nil
}

func (c *Client) GetSMS(page int) []map[string]string {
	data := fmt.Sprintf("[LTE_SMS_RECVMSGBOX#0,0,0,0,0,0#0,0,0,0,0,0]0,1\r\nPageNumber=%d\r\n[LTE_SMS_RECVMSGENTRY#0,0,0,0,0,0#0,0,0,0,0,0]1,5\r\nindex\r\nfrom\r\ncontent\r\nreceivedTime\r\nunread\r\n", page)
	return c.query(actSETGL, data)
}

func (c *Client) GetStatus() map[string]string {
	data := "[LTE_NET_STATUS#0,0,0,0,0,0#0,0,0,0,0,0]0,0\r\n[WAN_IP_CONN#0,0,0,0,0,0#0,0,0,0,0,0]1,0\r\n"
	return c.queryMerged(actGLGL, data)
}

func (c *Client) GetWLAN() map[string]string {
	data := "[LAN_WLAN#0,0,0,0,0,0#0,0,0,0,0,0]0,0\r\n"
	return c.queryMerged(actGL, data)
}

func (c *Client) GetLAN() map[string]string {
	data := "[LAN_IP_INTF#0,0,0,0,0,0#0,0,0,0,0,0]0,0\r\n[LAN_HOST_CFG#1,0,0,0,0,0#0,0,0,0,0,0]1,0\r\n"
	return c.queryMerged(actGLGET, data)
}

func (c *Client) SetSMSRead(stack string) {
	data := fmt.Sprintf("[LTE_SMS_RECVMSGENTRY#%s#0,0,0,0,0,0]0,1\r\nunread=0\r\n", stack)
	c.query(actSET, data)
}

func (c *Client) DeleteSMS(stack string) {
	data := fmt.Sprintf("[LTE_SMS_RECVMSGENTRY#%s#0,0,0,0,0,0]0,0\r\n", stack)
	c.query(actDEL, data)
}
