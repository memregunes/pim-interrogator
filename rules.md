# PIM Detection Strategy & Interpretation Rules

## 1. The Hybrid Scoring System
We use a dual-layer detection method: **Surface Signals** (UI/UX) and **Plumbing Signals** (Network/API).

### Scoring Weights:
* **Plumbing (0.6 pts):** Direct detection of Enterprise PIM CDNs (Salsify, Akeneo, Inriver, etc.). This is the strongest indicator of an established system.
* **Photometrics (0.2 pts):** Presence of .IES/.LDT files mapped to products. Large-scale mapping suggests a backend database.
* **BIM Maturity (0.1 pts):** High-quality Revit/BIM assets.
* **Documentation (0.1 pts):** Dynamic spec sheet generators or SKU configurators.

---

## 2. Lead Qualification Matrix

| Score Range | Status | AI Action | Emre's Strategy |
| :--- | :--- | :--- | :--- |
| **0.7 - 1.0** | **Existing PIM** | Mark as 'Existing PIM'. | **Low Priority.** They are already "digitized." |
| **0.4 - 0.6** | **Mid-Tier/Partial** | Mark as 'Research Needed'. | **Manual Audit.** They might have a basic E-commerce PIM (like Shopify) but lack technical depth. |
| **0.0 - 0.3** | **High Potential** | **Flag as Top Lead.** | **Immediate Action.** These are the "Big Fish" with bad websites (e.g., ECLATEC, Ragni). |

---

## 3. The "Emre Override" Protocol
* **Trust the Human:** If `pim_guess_emre` is filled, it overrides the AI score.
* **Note Context:** If `emre_comment` contains "Too small" or "Distributor," the agent must skip further research regardless of the score.

## 4. Execution Guidelines
* **Batch Size:** Process in groups of 100 to ensure high-quality browser rendering.
* **User Agent:** Always mask as a desktop browser to bypass manufacturer firewalls (BEGA, iGuzzini, etc.).
* **Lead Data:** Only collect professional LinkedIn and emails.
