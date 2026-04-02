import sys
import asyncio
from playwright.async_api import async_playwright

async def scan_website(url):
    if not url.startswith("http"):
        url = "https://" + url

    evidence = set()
    score = 0.0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Use a real User-Agent to avoid being blocked by BEGA/iGuzzini firewalls
        context = await browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)")
        page = await context.new_page()

        # STRENGTH 1: Network Interception (The "Plumbing")
        async def handle_response(response):
            req_url = response.url.lower()
            pim_sigs = ["akeneo", "salsify", "inriver", "productmarketingcloud", "pimcore", "perfion"]
            for sig in pim_sigs:
                if sig in req_url:
                    evidence.add(f"Detected Enterprise PIM Engine: {sig}")

        page.on("response", handle_response)

        try:
            # Wait for DOM to be ready, then a 5s grace period for background scripts
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            await page.wait_for_timeout(5000)

            html = await page.content()
            html_lower = html.lower()

            # STRENGTH 2: Keyword & Asset Scanning (The "Surface")
            # Photometrics
            if ".ies" in html_lower or ".ldt" in html_lower:
                evidence.add("Photometric Asset Mapping (.ies/.ldt)")

            # BIM/Revit
            if any(x in html_lower for x in ["revit", "bim", "archicad", "rfa file"]):
                evidence.add("BIM/Architectural Assets")

            # Documentation Logic
            if any(x in html_lower for x in ["spec sheet", "datasheet", "configurator", "submittal"]):
                evidence.add("Dynamic Documentation/Configurator Logic")

        except Exception as e:
            return {"url": url, "error": str(e)}
        finally:
            await browser.close()

    # Hybrid Scoring Logic
    for item in evidence:
        if "PIM Engine" in item: score += 0.6  # Heavy weight for network hits
        if "Photometric" in item: score += 0.2
        if "BIM" in item: score += 0.1
        if "Documentation" in item: score += 0.1

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
