import logging
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Set

from requests import get

from devilzero.config import PROXY_PROVIDERS
from devilzero.utils import print_warning, print_error, print_info, print_success

logger = logging.getLogger("devilzero.proxy")


class ProxyPool:
    def __init__(self):
        self._proxies = []
        self._idx = 0

    def load(self, proxy_file=None, proxy_type=0, target_url=None):
        if proxy_file and Path(proxy_file).exists():
            with open(proxy_file) as f:
                self._proxies = [line.strip() for line in f if line.strip()]
            print_info(f"Loaded {len(self._proxies)} proxies from {proxy_file}")
            return
        print_info("Downloading proxies...")
        raw = self._download(proxy_type)
        if raw:
            self._proxies = list(raw)
            print_success(f"Downloaded {len(self._proxies)} proxies")
            if proxy_file:
                with open(proxy_file, 'w') as f:
                    for p in self._proxies:
                        f.write(p + "\n")
        else:
            print_warning("No proxies downloaded")

    def _download(self, proxy_type):
        providers = [p for p in PROXY_PROVIDERS if p["type"] == proxy_type or proxy_type == 0]
        all_proxies = set()
        for prov in providers:
            try:
                resp = get(prov["url"], timeout=prov.get("timeout", 5))
                for line in resp.text.splitlines():
                    line = line.strip()
                    if line and ':' in line:
                        all_proxies.add(line)
            except Exception as e:
                print_error(f"Failed {prov['url']}: {e}")
        return all_proxies

    def get(self):
        if not self._proxies:
            return None
        self._idx = (self._idx + 1) % len(self._proxies)
        return self._proxies[self._idx]

    def random(self):
        if not self._proxies:
            return None
        return random.choice(self._proxies)

    def __len__(self):
        return len(self._proxies)