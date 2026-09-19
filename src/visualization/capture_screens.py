#!/usr/bin/env python3
"""Capture full-app screenshots with real data for the README showcase."""
import asyncio, time
from pathlib import Path
from playwright.async_api import async_playwright

OUT = Path("/home/user/tetra-shield-ai/assets/screenshots")
OUT.mkdir(parents=True, exist_ok=True)
BASE = "http://localhost:8000"

VIEWS = [
    ("01_home", "v-home", None, 3.0),
    ("02_contaminant", "v-contaminant", None, 3.0),
    ("03_discovery", "v-discover", None, 2.0),
    ("04_candidate_detail", "v-candidate", "S.curCand='TETX2-BT';refreshCandidate()", 3.5),
    ("05_candidate_laccase", "v-candidate", "S.curCand='LAC-TV';refreshCandidate()", 3.5),
    ("06_safety_pathways", "v-safety", None, 2.5),
    ("07_amr_shield", "v-amr", None, 2.0),
    ("08_circular_cassava", "v-circular", None, 2.0),
    ("09_decision_engine", "v-decision", None, 4.0),
    ("10_compare", "v-compare", None, 2.5),
    ("11_report", "v-report", None, 2.5),
    ("12_about", "v-about", None, 1.5),
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--enable-webgl", "--use-angle=swiftshader", "--enable-unsafe-swiftshader",
            "--ignore-gpu-blocklist"])
        page = await browser.new_page(viewport={"width": 1600, "height": 900}, device_scale_factor=1.5)
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(BASE, wait_until="networkidle")
        await page.wait_for_timeout(4000)

        for name, view, pre, wait in VIEWS:
            if pre:
                await page.evaluate(pre)
            await page.evaluate(f"go('{view}')")
            await page.wait_for_timeout(int(wait * 1000))
            await page.wait_for_timeout(1000)
            await page.screenshot(path=str(OUT / f"{name}.png"))
            print("shot:", name)

        # WHY panel open on decision
        await page.evaluate("go('v-decision')")
        await page.wait_for_timeout(2500)
        await page.evaluate("toggleWhy('TETX2-BT')")
        await page.wait_for_timeout(800)
        await page.screenshot(path=str(OUT / "13_why_explained.png"))
        print("shot: 13_why_explained")

        # WHAT-IF AMR conservative recalc
        await page.evaluate("pickPreset('AMR_CONSERVATIVE','presetRow')")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=str(OUT / "14_whatif_amr.png"))
        print("shot: 14_whatif_amr")

        # ANALYZE overlay — mid-flow and complete
        await page.evaluate("go('v-home')"); await page.wait_for_timeout(800)
        await page.evaluate("startAnalysis()")
        await page.wait_for_timeout(3200)
        await page.screenshot(path=str(OUT / "15_analyze_running.png"))
        print("shot: 15_analyze_running")
        await page.wait_for_timeout(7000)
        await page.screenshot(path=str(OUT / "16_analyze_complete.png"))
        print("shot: 16_analyze_complete")

        print("JS page errors:", errors[:5] if errors else "none")
        await browser.close()

asyncio.run(main())
