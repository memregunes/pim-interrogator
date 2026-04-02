from fastapi import FastAPI, HTTPException
from playwright.async_api import async_playwright

app = FastAPI(title="PIM Interrogator API")

@app.get("/scan")
async def scan_website(url: str):
    if not url.startswith("http"):
        url = "https://" + url

    evidence_set = set()
    score = 0.0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Listen to all background network traffic
        async def handle_response(response):
            req_url = response.url.lower()
            
            # 1. Inriver Footprints
            if "productmarketingcloud.com" in req_url or "inriver" in req_url:
                evidence_set.add("Inriver CDN/API footprint detected in network.")
            
            # 2. Akeneo Footprints
            elif "akeneo" in req_url:
                evidence_set.add("Akeneo CDN/API footprint detected in network.")
                    
            # 3. Salsify Footprints
            elif "salsify.com" in req_url or "salsify" in req_url:
                evidence_set.add("Salsify CDN/API footprint detected in network.")
                    
            # 4. Enterprise Search (Usually fed by PIM)
            elif "algolia.net" in req_url and "products" in req_url:
                evidence_set.add("Algolia enterprise product search detected.")

        page.on("response", handle_response)

        try:
            # Navigate to the site and wait for the dust to settle
            await page.goto(url, wait_until="networkidle", timeout=15000)
            
            html = await page.content()
            html_lower = html.lower()

            # Front-end Lighting Industry Footprints
            if ".ies" in html_lower or ".ldt" in html_lower:
                evidence_set.add("Found photometric file downloads (.ies/.ldt).")
            
            if "bim" in html_lower or "revit" in html_lower:
                evidence_set.add("Found BIM/Revit references.")

            if "download data sheet" in html_lower or "spec sheet" in html_lower:
                evidence_set.add("Found dynamic data/spec sheet generation.")

        except Exception as e:
            await browser.close()
            raise HTTPException(status_code=500, detail=str(e))

        await browser.close()

    # Calculate final score safely based on unique evidence found
    for item in evidence_set:
        if "Inriver" in item or "Akeneo" in item or "Salsify" in item:
            score += 0.7  # Major PIM detection is an almost guaranteed high score
        elif "Algolia" in item:
            score += 0.2
        elif "photometric" in item:
            score += 0.3
        elif "BIM" in item:
            score += 0.2
        elif "spec sheet" in item:
            score += 0.2

    final_score = min(round(score, 2), 1.0)
    
    return {
        "target_url": url,
        "pim_score": final_score,
        "evidence": list(evidence_set),
        "conclusion": "High Probability" if final_score >= 0.6 else "Low Probability"
    }
