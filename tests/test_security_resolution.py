import socket

import pytest

from andrew_ai_navigator.security import UnsafeTarget, resolve_public_http_target


@pytest.mark.parametrize('url', [
    'http://100.64.0.1/', 'http://[::ffff:100.64.0.1]/',
    'http://[::ffff:127.0.0.1]/', 'http://224.0.0.1/',
    'http://[ff02::1]/', 'http://[fe80::1%25eth0]/',
    'https://8.8.8.8:0/', 'https://8.8.8.8:65536/',
    'https://[::1', 'https://@example.com/', 'https://:@example.com/',
    'https://./', 'https://example.com\\@example.org/',
    'https://exa\nmple.com/', ' https://example.com/',
])
def test_denied_before_dns(monkeypatch, url):
    def unexpected(*args, **kwargs):
        pytest.fail('DNS called for forbidden URL')
    monkeypatch.setattr(socket, 'getaddrinfo', unexpected)
    with pytest.raises(UnsafeTarget):
        resolve_public_http_target(url)


@pytest.mark.parametrize('url,port', [
    ('http://example.com/', 80), ('https://example.com/', 443),
    ('http://example.com:8080/', 8080), ('https://example.com:8443/', 8443),
])
def test_dns_uses_requested_port(monkeypatch, url, port):
    def lookup(host, service, **kwargs):
        assert host == 'example.com'
        assert service == port
        assert kwargs['type'] == socket.SOCK_STREAM
        return [(socket.AF_INET, socket.SOCK_STREAM, 0, '', ('8.8.8.8', service))]
    monkeypatch.setattr(socket, 'getaddrinfo', lookup)
    assert resolve_public_http_target(url).addresses == ('8.8.8.8',)


@pytest.mark.parametrize('bad', ['100.64.0.1', '127.0.0.1', '::ffff:10.0.0.1', 'invalid'])
def test_mixed_dns_answers_fail_closed(monkeypatch, bad):
    monkeypatch.setattr(socket, 'getaddrinfo', lambda *a, **k: [
        (socket.AF_INET, socket.SOCK_STREAM, 0, '', ('8.8.8.8', 443)),
        (socket.AF_INET6, socket.SOCK_STREAM, 0, '', (bad, 443, 0, 0)),
    ])
    with pytest.raises(UnsafeTarget):
        resolve_public_http_target('https://example.com/')


@pytest.mark.parametrize('url,address', [
    ('https://8.8.8.8/', '8.8.8.8'),
    ('https://[2606:4700:4700::1111]/', '2606:4700:4700::1111'),
])
def test_public_literals(monkeypatch, url, address):
    monkeypatch.setattr(socket, 'getaddrinfo', lambda *a, **k: pytest.fail('unexpected DNS'))
    assert resolve_public_http_target(url).addresses == (address,)


def test_no_dns_answers(monkeypatch):
    monkeypatch.setattr(socket, 'getaddrinfo', lambda *a, **k: [])
    with pytest.raises(UnsafeTarget):
        resolve_public_http_target('https://example.com/')


def test_dns_error(monkeypatch):
    def fail(*args, **kwargs):
        raise socket.gaierror('synthetic error')
    monkeypatch.setattr(socket, 'getaddrinfo', fail)
    with pytest.raises(UnsafeTarget):
        resolve_public_http_target('https://example.com/')
