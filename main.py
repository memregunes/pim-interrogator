import sys
import asyncio
from playwright.async_api import async_playwright

async def scan_website(url):
    if not url.startswith("http"): url = "https://" + url
    evidence = set()
    score = 0.0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Using a highly standard User-Agent to bypass basic bot walls
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = await context.new_page()

        # 1. THE PLUMBING: Listen for JSON payloads and PIM CDNs
        async def handle_request(request):
            req_url = request.url.lower()
            if "api/" in req_url or ".json" in req_url or "graphql" in req_url:
                evidence.add("Headless PIM/API Data Architecture")
            if any(s in req_url for s in ["akeneo", "salsify", "inriver", "pimcore", "perfion"]):
                evidence.add(f"Enterprise PIM Trace: {req_url.split('/')[2]}")

        page.on("request", handle_request)

        try:
            # 2. THE FRONT DOOR: Load the site and simulate a human looking for specs
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.mouse.wheel(0, 1500) # Scroll to trigger lazy-loaded elements
            await page.wait_for_timeout(4000)

            html = (await page.content()).lower()

            if any(x in html for x in [".ies", ".ldt", "photometric", "eulumdat"]):
                evidence.add("Technical Asset Mapping (IES/LDT)")
            if any(x in html for x in ["revit", "bim", "rfa", "archicad"]):
                evidence.add("BIM/Architectural Assets")
            if any(x in html for x in ["configurator", "spec sheet", "datasheet"]):
                evidence.add("Dynamic Documentation Logic")

            # 3. THE BACK DOOR: The Sitemap Sniffer
            # We use the browser's API context to request the sitemap silently
            sitemap_url = url.rstrip('/') + "/sitemap.xml"
            sitemap_response = await context.request.get(sitemap_url, timeout=15000)

            if sitemap_response.ok:
                sitemap_text = await sitemap_response.text()
                url_count = sitemap_text.count("<loc>")
                sitemap_lower = sitemap_text.lower()

                if url_count > 500 and "product" in sitemap_lower:
                    evidence.add(f"Automated Product Sitemap (> {url_count} URLs)")
                elif url_count > 2000:
                    evidence.add(f"Massive Enterprise XML Feed (> {url_count} URLs)")

        except Exception as e:
            return {"url": url, "error": str(e)}
        finally:
            await browser.close()

    # THE MASTER SCORING ENGINE
    for item in evidence:
        if "Enterprise PIM" in item: score += 0.6
        if "Headless" in item: score += 0.3
        if "IES/LDT" in item: score += 0.2
        if "BIM" in item: score += 0.1
        if "Logic" in item: score += 0.2
        if "Sitemap" in item or "XML Feed" in item: score += 0.2

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
