import json, sys, time
from playwright.sync_api import sync_playwright

URL = "file:///home/claude/boss-rush-game/index.html"
results = {}
console_errors = []

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/opt/pw-browsers/chromium/chrome-linux/chrome" if False else None)
        browser = p.chromium.launch()
        for vw, vh, label in [(1366,768,"1366x768"), (1920,1080,"1920x1080")]:
            ctx = browser.new_context(viewport={"width":vw,"height":vh})
            page = ctx.new_page()
            errs = []
            page.on("console", lambda msg: errs.append(msg.text) if msg.type=="error" else None)
            page.on("pageerror", lambda exc: errs.append(str(exc)))
            page.goto(URL)
            page.wait_for_timeout(300)

            # check horizontal overflow / clipping of the game area
            overflow = page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
            wrap_box = page.eval_on_selector("#canvas-wrap", "el => el.getBoundingClientRect()")
            info_box = page.eval_on_selector(".info-panel", "el => el.getBoundingClientRect()")
            ctrl_box = page.eval_on_selector(".controls-panel", "el => el.getBoundingClientRect()")
            within_viewport = (wrap_box["right"] <= vw+1 and wrap_box["left"] >= -1 and
                                info_box["right"] <= vw+1 and ctrl_box["right"] <= vw+1)

            results[label] = {
                "horizontal_overflow": overflow,
                "canvas_wrap_box": wrap_box,
                "within_viewport": within_viewport,
                "console_errors_after_load": list(errs),
            }
            ctx.close()

        # ---- functional test in one long-lived context ----
        ctx = browser.new_context(viewport={"width":1366,"height":768})
        page = ctx.new_page()
        errs = []
        page.on("console", lambda msg: errs.append(msg.text) if msg.type=="error" else None)
        page.on("pageerror", lambda exc: errs.append(str(exc)))
        page.goto(URL)
        page.wait_for_timeout(200)

        # start game
        page.click("#btn-start")
        page.wait_for_timeout(200)
        phase1 = page.evaluate("window.__debug.phase")

        # simulate rapid movement input: 10 keydown/up pairs within ~1s, check pressed state toggles cleanly
        page.keyboard.down("ArrowRight")
        page.wait_for_timeout(50)
        pressed_after_down = page.evaluate("window.__debug.pressed.right")
        page.keyboard.up("ArrowRight")
        page.wait_for_timeout(50)
        pressed_after_up = page.evaluate("window.__debug.pressed.right")

        # rapid alternating presses x10 within 1 second
        import time as _t
        t0=_t.time()
        for i in range(10):
            page.keyboard.press("ArrowLeft")
        t1=_t.time()
        rapid_press_duration = t1-t0
        pressed_after_rapid = page.evaluate("window.__debug.pressed.left")  # should be false (press = down+up)

        # let it play a bit
        page.wait_for_timeout(1500)
        player_moved = page.evaluate("window.__debug.player.x")

        # test pause via P key
        page.keyboard.press("p")
        page.wait_for_timeout(100)
        phase_paused = page.evaluate("window.__debug.phase")
        elapsed_at_pause = page.evaluate("window.__debug.elapsed")
        page.wait_for_timeout(500)
        elapsed_after_wait = page.evaluate("window.__debug.elapsed")

        page.keyboard.press("p")
        page.wait_for_timeout(100)
        phase_resumed = page.evaluate("window.__debug.phase")

        # test resize does not reset state
        kills_before_resize = page.evaluate("window.__debug.kills")
        elapsed_before_resize = page.evaluate("window.__debug.elapsed")
        page.set_viewport_size({"width":1920,"height":1080})
        page.wait_for_timeout(200)
        kills_after_resize = page.evaluate("window.__debug.kills")
        elapsed_after_resize = page.evaluate("window.__debug.elapsed")
        phase_after_resize = page.evaluate("window.__debug.phase")

        # test blur auto-pause
        page.evaluate("window.dispatchEvent(new Event('blur'))")
        page.wait_for_timeout(100)
        phase_after_blur = page.evaluate("window.__debug.phase")

        results["functional"] = {
            "phase_after_start": phase1,
            "pressed_after_down": pressed_after_down,
            "pressed_after_up": pressed_after_up,
            "rapid_press_duration_s": rapid_press_duration,
            "pressed_after_rapid": pressed_after_rapid,
            "player_x_after_move": player_moved,
            "phase_paused": phase_paused,
            "elapsed_frozen_during_pause": elapsed_at_pause == elapsed_after_wait,
            "phase_resumed": phase_resumed,
            "kills_before_resize": kills_before_resize, "kills_after_resize": kills_after_resize,
            "elapsed_before_resize": elapsed_before_resize, "elapsed_after_resize": elapsed_after_resize,
            "state_not_reset_after_resize": kills_after_resize>=kills_before_resize and elapsed_after_resize>=elapsed_before_resize and elapsed_after_resize < 5,
            "phase_after_resize": phase_after_resize,
            "phase_after_blur": phase_after_blur,
            "console_errors": list(errs),
        }

        # ---- localStorage corruption / empty tests ----
        page.evaluate("localStorage.removeItem('bossRushSave_v1')")
        empty_load = page.evaluate("JSON.stringify(window.__debug.loadSave())")
        page.evaluate("localStorage.setItem('bossRushSave_v1', '{ not valid json')")
        corrupt_load = page.evaluate("JSON.stringify(window.__debug.loadSave())")
        results["storage"] = {"empty_load": empty_load, "corrupt_load": corrupt_load}

        # ---- run simulator batches (10+10, real difficulty values) ----
        page.evaluate("window.__debug.runSimBatch('A(1400ms)', 1400, 10)")
        page.evaluate("window.__debug.runSimBatch('B(1000ms)', 1000, 10)")
        full_log = page.evaluate("window.__debug.simLog")
        results["simulator_full"] = full_log

        ctx.close()
        browser.close()

    print(json.dumps(results, indent=2, ensure_ascii=False))

run()
