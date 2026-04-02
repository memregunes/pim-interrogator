import sys
import asyncio
import re
from playwright.async_api import async_playwright

async def scan_website(url):
    if not url.startswith("http"):
        url = "https://" + url

    # We preserve the original categories but expand the 'evidence'
    evidence = set()
    score = 0.0

    async with async_playwright() as p:
        # Step 1: Improved Browser Setup (Bypass enterprise firewalls)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = await context.new_page()

        # STRENGTH 1: Network Sniffing (From the newer Interrogator logic)
        async def handle_response(response):
            req_url = response.url.lower()
            # Detects Salsify, Akeneo, Inriver, etc.
            pim_sigs = ["akeneo", "salsify", "inriver", "productmarketingcloud", "pimcore", "perfion"]
            for sig in pim_sigs:
                if sig in req_url:
                    evidence.add(f"Enterprise PIM Engine Trace: {sig}")

        page.on("response", handle_response)

        try:
            # Step 2: Realistic Loading (Crucial for BEGA/iGuzzini)
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            await page.wait_for_timeout(5000) # Wait for background 'logic' to trigger

            html = await page.content()
            html_lower = html.lower()

            # STRENGTH 2: Keyword & Asset Scanning (Your Original 'Scout' logic)
            # Photometrics (.ies/.ldt) - The Lighting Industry 'Gold Standard'
            if ".ies" in html_lower or ".ldt" in html_lower:
                evidence.add("Technical Asset Mapping (Photometric .ies/.ldt)")

            # BIM/Revit - Specifier readiness
            if any(x in html_lower for x in ["revit", "bim", "archicad", "rfa file"]):
                evidence.add("BIM/Architectural Data Hosting")

            # Documentation Logic - Sign of a Single Source of Truth
            if any(x in html_lower for x in ["spec sheet", "datasheet", "configurator", "submittal"]):
                evidence.add("Dynamic Documentation/Configurator Logic")

        except Exception as e:
            return {"url": url, "error": str(e)}
        finally:
            await browser.close()

    # THE HYBRID SCORING ENGINE (Combines both strengths)
    for item in evidence:
        if "Enterprise PIM" in item: score += 0.6   # Hard evidence (Signature)
        if "Photometric" in item: score += 0.2     # Soft evidence (Capability)
        if "BIM" in item: score += 0.1             # Soft evidence (Capability)
        if "Documentation" in item: score += 0.2   # Soft evidence (Capability)

    # FINAL AUDIT: If a site has Photometrics + BIM + Configurator,
    # it gets a High Score even if we don't know the PIM's brand name.
    final_score = min(round(score, 2), 1.0)

    return {
        "url": url,
        "pim_score": final_score,
        "evidence": list(evidence),
        "is_high_potential": "No" if final_score >= 0.7 else "Yes"
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(asyncio.run(scan_website(sys.argv[1])))
