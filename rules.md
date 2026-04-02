# PIM Detection & Strategy Rules (V2 - Hybrid)

## 1. The Core Philosophy
A PIM is defined by **functionality**, not just **signatures**. If a company manages thousands of technical variants and files seamlessly, they have a PIM (custom or off-the-shelf).

## 2. Updated Scoring Weights (Hybrid Logic)

### Level 1: Hard Signatures (0.6 pts)
* **Rule:** If the network sniff detects Salsify, Akeneo, Inriver, Perfion, or Pimcore.
* **Reason:** These are direct enterprise software footprints.

### Level 2: Technical Capabilities (0.2 - 0.3 pts each)
* **Photometric Asset Mapping (0.3 pts):** Large-scale .IES/.LDT file hosting linked to specific product pages.
* **BIM/Revit Maturity (0.1 pts):** High-quality architectural data hosting (Revit, ArchiCAD).
* **Dynamic Documentation (0.2 pts):** Automated PDF generation, SKU configurators, or "Submittal" builders.

---

## 3. Interpreting the Hybrid Score

| Total Score | Classification | Sales Action |
| :--- | :--- | :--- |
| **0.8 - 1.0** | **Enterprise Maturity** | **Do Not Target.** They have solved the data problem (e.g., BEGA). |
| **0.4 - 0.7** | **Partial/Custom PIM** | **Secondary Target.** They might have a basic system but struggle with technical scaling. |
| **0.1 - 0.3** | **High Potential** | **Primary Target.** They have high revenue but low digital automation (The "Manual Data" trap). |

---

## 4. Operational Instructions for Agents
1. **User Agent:** Always use a modern desktop user-agent to avoid "Bot Blocking" from enterprise sites.
2. **Timeout:** Set to 45s minimum. Lightning sites (BEGA, ERCO) are asset-heavy.
3. **Data Integrity:** If a site fails to load after 3 attempts, mark status as 'Check Manually'.
4. **Lead Data:** Priority 1 is Marketing Director, Priority 2 is Managing Director. **LinkedIn only.**
