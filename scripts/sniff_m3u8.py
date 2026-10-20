#!/usr/bin/env python3
"""用浏览器真实加载页面，抓出播放器请求的 m3u8 地址。

有些站的播放地址是 WebSocket/JS 动态下发的，静态爬页面拿不到，
只能让浏览器跑一遍 JS，监听 Network 事件看它到底请求了什么。

用法：
    python scripts/sniff_m3u8.py <url> [等待秒数]

依赖本地 Edge（Windows 自带）和 websocket-client。
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

import websocket

EDGE_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
]


def find_browser() -> str:
    for p in EDGE_CANDIDATES:
        if os.path.exists(p):
            return p
    for name in ("msedge", "chrome"):
        p = shutil.which(name)
        if p:
            return p
    raise SystemExit("没找到 Edge / Chrome")


def free_port() -> int:
    import socket
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def cdp_targets(port: int) -> list[dict]:
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5) as r:
        return json.load(r)


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 1
    url = argv[0]
    wait = float(argv[1]) if len(argv) > 1 else 25.0

    exe = find_browser()
    port = free_port()
    profile = tempfile.mkdtemp(prefix="sniff-")
    proc = subprocess.Popen(
        [exe, "--headless=new", f"--remote-debugging-port={port}",
         "--disable-gpu", "--no-first-run", "--no-default-browser-check",
         "--autoplay-policy=no-user-gesture-required",
         "--mute-audio", f"--user-data-dir={profile}", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        ws_url = None
        for _ in range(40):
            time.sleep(0.25)
            try:
                for t in cdp_targets(port):
                    if t.get("type") == "page":
                        ws_url = t["webSocketDebuggerUrl"]
                        break
            except Exception:  # noqa: BLE001
                continue
            if ws_url:
                break
        if not ws_url:
            raise SystemExit("浏览器没起来")

        ws = websocket.create_connection(ws_url, timeout=10, suppress_origin=True)
        mid = 0

        def send(method: str, params: dict | None = None) -> None:
            nonlocal mid
            mid += 1
            ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))

        send("Network.enable")
        send("Page.enable")
        send("Page.navigate", {"url": url})

        found: list[str] = []
        deadline = time.time() + wait
        ws.settimeout(1.0)
        while time.time() < deadline:
            try:
                msg = json.loads(ws.recv())
            except Exception:  # noqa: BLE001
                continue
            if msg.get("method") != "Network.requestWillBeSent":
                continue
            u = msg["params"]["request"]["url"]
            if ".m3u8" in u or "m3u8" in u:
                if u not in found:
                    found.append(u)
                    print(f"[+] {u}", flush=True)
                    if len(found) >= 5:
                        break
        ws.close()

        print()
        if found:
            print(f"[✓] 抓到 {len(found)} 条 m3u8")
        else:
            print("[X] 这段时间内没有任何 m3u8 请求（可能需要点播放按钮，或该页走的是 flv/ws）")
        return 0
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:  # noqa: BLE001
            proc.kill()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
