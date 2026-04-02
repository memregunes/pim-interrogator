from fastapi import FastAPI, HTTPException
from playwright.async_api import async_playwright
import re

app = FastAPI(title="PIM Interrogator API")

@app.get("/scan")
async def scan_website(url: str):
    if not url.startswith("http"):
        url = "https://" + url

    evidence = []
    score = 0.0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Listen to network traffic for PIM CDNs or structural JSON
        async def handle_response(response):
            nonlocal score
            url = response.url.lower()
            if "productmarketingcloud.com" in url or "inriver" in url:
                evidence.append("inRiver CDN footprint detected in network.")
                score += 0.5
            elif "akeneo" in url:
                evidence.append("Akeneo footprint detected.")
                score += 0.5
            elif "algolia.net" in url and "products" in url:
                evidence.append("Algolia enterprise search (often fed by PIM).")
                score += 0.2

        page.on("response", handle_response)

        try:
            # Go to the site and wait for the network to settle
            await page.goto(url, wait_until="networkidle", timeout=15000)
            
            # Check the HTML structure (The "Paint")
            html = await page.content()
            html_lower = html.lower()

            if ".ies" in html_lower or ".ldt" in html_lower:
                evidence.append("Found photometric file downloads (.ies/.ldt). Highly indicative of PIM variant management.")
                score += 0.4
            
            if "bim" in html_lower or "revit" in html_lower:
                evidence.append("Found BIM/Revit references.")
                score += 0.3

            if "download data sheet" in html_lower or "spec sheet" in html_lower:
                evidence.append("Found data sheet generator buttons.")
                score += 0.2

        except Exception as e:
            await browser.close()
            raise HTTPException(status_code=500, detail=str(e))

        await browser.close()

    # Cap score at 1.0
    final_score = min(round(score, 2), 1.0)
    
    return {
        "target_url": url,
        "pim_score": final_score,
        "evidence": evidence,
        "conclusion": "High Probability" if final_score > 0.6 else "Low Probability"
    }