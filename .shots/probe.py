"""Probe the rendered install-box geometry + computed styles via CDP."""
import asyncio, json, sys, subprocess, time, urllib.request

import websockets  # uv run --with websockets

URL = sys.argv[1]
CHROME = subprocess.check_output(
    ["bash", "-c", "echo ~/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome"],
    text=True).strip()

JS = r"""
(() => {
  const pick = (el) => {
    if (!el) return null;
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return {
      tag: el.tagName.toLowerCase(), cls: el.className,
      rect: {x: +r.x.toFixed(1), y: +r.y.toFixed(1), w: +r.width.toFixed(1), h: +r.height.toFixed(1)},
      display: cs.display, borderRadius: cs.borderRadius,
      bg: cs.backgroundColor, border: cs.border, overflow: cs.overflow,
      color: cs.color, font: cs.fontFamily.split(",")[0] + " " + cs.fontSize,
      text: (el.textContent || "").trim().slice(0, 70),
    };
  };
  const inst = document.querySelector(".hero .install");
  return {
    installChildren: inst ? [...inst.children].map(c => c.className || c.tagName) : null,
    heroChildren: [...document.querySelector(".hero").children].map(c => c.className || c.tagName),
    install: pick(inst),
    pre: pick(inst && inst.querySelector("pre")),
    prompt: pick(inst && inst.querySelector("pre .p")),
    copyBtn: pick(inst && inst.querySelector("button.copy")),
    alt: pick(document.querySelector(".hero p.alt")),
    cta: pick(document.querySelector(".hero .cta")),
    preScroll: inst && inst.querySelector("pre") ? {
      clientW: inst.querySelector("pre").clientWidth,
      scrollW: inst.querySelector("pre").scrollWidth,
      overflowing: inst.querySelector("pre").scrollWidth > inst.querySelector("pre").clientWidth,
    } : null,
  };
})()
"""


async def main():
    proc = subprocess.Popen([
        CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
        "--hide-scrollbars", "--window-size=1280,900",
        "--remote-debugging-port=9333", "about:blank",
    ], env={"LD_LIBRARY_PATH": "/tmp/chrome-libs/extracted/usr/lib/x86_64-linux-gnu",
            "PATH": "/usr/bin:/bin", "HOME": "/home/tarek"},
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ws_url = None
        for _ in range(50):
            try:
                targets = json.load(urllib.request.urlopen("http://127.0.0.1:9333/json"))
                pages = [t for t in targets if t["type"] == "page"]
                if pages:
                    ws_url = pages[0]["webSocketDebuggerUrl"]
                    break
            except Exception:
                pass
            await asyncio.sleep(0.2)
        async with websockets.connect(ws_url, max_size=10 << 20) as ws:
            mid = 0

            async def cmd(method, **params):
                nonlocal mid
                mid += 1
                await ws.send(json.dumps({"id": mid, "method": method, "params": params}))
                while True:
                    msg = json.loads(await ws.recv())
                    if msg.get("id") == mid:
                        if "error" in msg:
                            raise RuntimeError(msg["error"])
                        return msg.get("result", {})
            await cmd("Page.enable")
            await cmd("Page.navigate", url=URL)
            await asyncio.sleep(1.5)  # load + settle
            res = await cmd("Runtime.evaluate",
                            expression=JS, returnByValue=True)
        print(json.dumps(res["result"]["value"], indent=1))
    finally:
        proc.terminate()


asyncio.run(main())
