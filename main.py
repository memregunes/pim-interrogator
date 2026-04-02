import sys
import asyncio
from playwright.async_api import async_playwright

async def scan_website(url):
    if not url.startswith("http"):
        url = "https://" + url

    evidence = set()
    score = 0.0

    async with async_playwright() as p:
        # Launching with a user-agent to avoid being blocked by enterprise firewalls
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        page = await context.new_page()

        # Listen for background "Data Plumbings"
        async def handle_response(response):
            req_url = response.url.lower()
            # Detection for Akeneo, Salsify, Inriver, and Enterprise CDNs
            if any(term in req_url for term in ["akeneo", "salsify", "inriver", "productmarketingcloud", "pimcore"]):
                evidence.add(f"Enterprise PIM Network Trace: {req_url.split('/')[2]}")

        page.on("response", handle_response)

        try:
            # Extended timeout for heavy manufacturer sites like BEGA
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            await page.wait_for_timeout(5000) # Wait for background lazy-loading

            html = await page.content()
            html_lower = html.lower()

            # Lighting Industry Specific Footprints
            if ".ies" in html_lower or ".ldt" in html_lower:
                evidence.add("Photometric Data Management (.ies/.ldt)")
            if any(term in html_lower for term in ["revit", "bim object", "archicad"]):
                evidence.add("BIM/Architectural Asset hosting")
            if "spec sheet" in html_lower or "datasheet" in html_lower:
                evidence.add("Dynamic Spec Sheet Generator")
            if "configurator" in html_lower or "product-selector" in html_lower:
                evidence.add("Complex Product Configurator (Logic-driven)")

        except Exception as e:
            return {"url": url, "error": str(e)}
        finally:
            await browser.close()

    # Scoring Logic
    for item in evidence:
        if "Enterprise PIM" in item: score += 0.7
        elif "Photometric" in item: score += 0.3
        elif "BIM" in item: score += 0.2
        elif "Spec Sheet" in item: score += 0.2
        elif "Configurator" in item: score += 0.3

    final_score = min(round(score, 2), 1.0)
    return {
        "url": url,
        "pim_score": final_score,
        "evidence": list(evidence),
        "status": "High Probability" if final_score >= 0.6 else "Medium/Low"
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
        result = asyncio.run(scan_website(target))
        print(result)
    else:
        print("Please provide a URL: python main.py https://example.com")
