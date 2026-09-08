import json, time, random, sys
from playwright.sync_api import sync_playwright

URL = "file:///home/claude/boss-rush-game/index.html"
DURATION_S = int(sys.argv[1]) if len(sys.argv) > 1 else 585  # keep under 600s tool timeout with margin

def run():
    console_errors = []
    snapshots = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width":1366,"height":768})
        page = ctx.new_page()
        page.on("console", lambda msg: console_errors.append({"t":time.time(),"text":msg.text}) if msg.type=="error" else None)
        page.on("pageerror", lambda exc: console_errors.append({"t":time.time(),"text":str(exc)}))
        page.goto(URL)
        page.wait_for_timeout(300)
        page.click("#btn-start")

        keys = ["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"]
        start = time.time()
        last_snapshot = 0
        while time.time() - start < DURATION_S:
            k = random.choice(keys)
            page.keyboard.down(k)
            page.wait_for_timeout(random.randint(150,400))
            page.keyboard.up(k)

            phase = page.evaluate("window.__debug.phase")
            if phase in ("success","fail"):
                page.click("#btn-restart", timeout=2000)
                page.wait_for_timeout(100)
            elif phase == "paused":
                # random blur simulation may have paused it; resume via button if visible, else P key
                try:
                    page.click("#btn-resume", timeout=500)
                except Exception:
                    page.keyboard.press("p")
                page.wait_for_timeout(100)

            elapsed_wall = time.time() - start
            if elapsed_wall - last_snapshot >= 20:
                last_snapshot = elapsed_wall
                snap = page.evaluate("""() => ({
                    phase: window.__debug.phase,
                    mobs: window.__debug.mobsCount,
                    particles: window.__debug.particlesCount,
                })""")
                snapshots.append({"t": round(elapsed_wall,1), **snap})

        final_errors = console_errors
        summary = {
            "duration_s": round(time.time()-start,1),
            "console_error_count": len(final_errors),
            "console_errors_sample": final_errors[:10],
            "snapshots": snapshots,
            "final_phase": page.evaluate("window.__debug.phase"),
        }
        ctx.close()
        browser.close()
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run()
