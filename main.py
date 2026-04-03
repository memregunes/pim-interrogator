import sys
import asyncio
import json
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

# Patterns that indicate a link is a "Product Detail Page"
PRODUCT_PATTERNS = ["/product", "/item", "/luminaire", "/collection", "/family", "-sku-", "/p/"]

async def scan_single_site(url, context, semaphore):
    # The Semaphore ensures we only process a maximum of 5 sites at once to save RAM
    async with semaphore:
        if not url.startswith("http"): url = "https://" + url
        evidence = set()
        score = 0.0

        page = await context.new_page()
        # UPGRADE 3: Apply Advanced Bot Stealth (Bypasses Cloudflare)
        await stealth_async(page)

        # UPGRADE 2: Strict JSON/API Sniffing
        async def handle_request(request):
            req_url = request.url.lower()
            if any(s in req_url for s in ["akeneo", "salsify", "inriver", "pimcore", "perfion"]):
                evidence.add(f"Enterprise PIM Trace: {req_url.split('/')[2]}")
            # Look specifically for PRODUCT APIs, not generic WordPress JSONs
            if any(s in req_url for s in ["api/product", "graphql", "variants.json", "catalog/api"]):
                evidence.add("Headless Product API Architecture")

        page.on("request", handle_request)

        try:
            # 1. Load Homepage
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)

            # UPGRADE 1: The Product Page Hunter
            # Extract all links on the homepage to find a real product page
            hrefs = await page.evaluate("() => Array.from(document.querySelectorAll('a[href]')).map(a => a.href)")
            product_links = [h for h in hrefs if any(p in h.lower() for p in PRODUCT_PATTERNS)]

            # If we find a product page, click into it for the deep scan
            if product_links:
                target_url = product_links[0]
                await page.goto(target_url, wait_until="domcontentloaded", timeout=45000)

            # SIMULATE HUMAN: Scroll the (Homepage or Product Page) to trigger lazy loading
            await page.mouse.wheel(0, 1500)
            await page.wait_for_timeout(4000)

            html = (await page.content()).lower()

            # THE CAPABILITY CHECK
            if any(x in html for x in [".ies", ".ldt", "photometric", "eulumdat"]):
                evidence.add("Technical Asset Mapping (IES/LDT)")
            if any(x in html for x in ["revit", "bim", "rfa", "archicad"]):
                evidence.add("BIM/Architectural Assets")
            if any(x in html for x in ["configurator", "spec sheet", "datasheet"]):
                evidence.add("Dynamic Documentation Logic")

            # THE SITEMAP SNIFFER
            sitemap_url = url.rstrip('/') + "/sitemap.xml"
            sitemap_response = await context.request.get(sitemap_url, timeout=10000)
            if sitemap_response.ok:
                text = await sitemap_response.text()
                url_count = text.count("<loc>")
                if url_count > 500 and "product" in text.lower():
                    evidence.add(f"Automated Product Sitemap (> {url_count} URLs)")

        except Exception as e:
            return {"url": url, "error": str(e)}
        finally:
            await page.close()

        # MASTER SCORING
        for item in evidence:
            if "Enterprise PIM" in item: score += 0.6
            if "Headless" in item: score += 0.3
            if "IES/LDT" in item: score += 0.2
            if "BIM" in item: score += 0.1
            if "Logic" in item: score += 0.2
            if "Sitemap" in item: score += 0.2

        final_score = min(round(score, 2), 1.0)
        return {"url": url, "pim_score": final_score, "evidence": list(evidence), "is_high_potential": "No" if final_score >= 0.7 else "Yes"}


# UPGRADE 4: Parallel Processing (Batching)
async def main(urls):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        # This controls the concurrency. 5 at a time is perfect for Mac/Zo without crashing.
        semaphore = asyncio.Semaphore(5)

        # Create a task for every URL and run them simultaneously
        tasks = [scan_single_site(url, context, semaphore) for url in urls]
        results = await asyncio.gather(*tasks)

        await browser.close()

        # Return clean JSON for Zo/Claude to read easily
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Accepts multiple URLs from the command line: python main.py url1 url2 url3
        urls = sys.argv[1:]
        asyncio.run(main(urls))
    else:
        print("Please provide URLs. Example: python main.py https://bega.com https://iguzzini.com")
