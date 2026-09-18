'''
US/Global B2B SaaS Article Generator using Gemini API
Produces deep, high-converting software reviews and comparison guides.
'''
import json
import re
import time
from google import genai
from google.genai import types
from config import GEMINI_API_KEY
from prompt_template_saas import SYSTEM_PROMPT_SAAS

MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-3-flash-preview"
]


ARCHETYPES = [
    {
        "name": "decision_matrix_first",
        "instruction": (
            "STRUCTURAL ARCHETYPE A (Decision-First Flow):\n"
            "- Executive overview (<120 words) followed immediately by the StackPilot 2026 Methodology callout with 'Last Verified' date.\n"
            "- 'Quick-Match at a Glance': High-impact summary bullets matching top tools to distinct operator profiles.\n"
            "- Comprehensive responsive <table> comparing 5-7 leading tools (Platform, Best For, Starting Price, Free Tier/Trial, Standout Capability, Known Limitation).\n"
            "- In-depth H3 tool reviews (5-7 tools) with architecture, transparent pricing, genuine pros/cons, and who should buy vs pass.\n"
            "- Buyer Checklist: 5 technical non-negotiables before subscribing.\n"
            "- Scenario-Based Decision Matrix: 'Which Software Fits Your Business?' table.\n"
            "- FAQ section formatted for FAQPage schema.\n"
            "- Sources & Official Documentation section with direct vendor links."
        )
    },
    {
        "name": "tco_pricing_first",
        "instruction": (
            "STRUCTURAL ARCHETYPE B (TCO & Operational Bottlenecks Flow):\n"
            "- Operational dilemma/bottleneck intro with StackPilot 2026 Methodology callout & 'Last Verified' date.\n"
            "- 'The True Cost of Software': Deep analysis of hidden volume overages, seat pricing, and carrier discount spreads.\n"
            "- Full 5-7 tool responsive comparison table (with exact starting prices and pricing models).\n"
            "- Tool-by-tool H3 breakdowns analyzing cost-efficiency at 100, 1,000, and 10,000 monthly transactions.\n"
            "- Technical architecture pitfalls (API limits, webhooks, marketplace throttling).\n"
            "- Scenario-Based Decision Matrix: 'Which Software Fits Your Business?' table.\n"
            "- FAQ section formatted for FAQPage schema.\n"
            "- Sources & Official Documentation section with direct vendor links."
        )
    },
    {
        "name": "maturity_curve",
        "instruction": (
            "STRUCTURAL ARCHETYPE C (Business Maturity & Scale Flow):\n"
            "- Stage-based intro (Bootstrapped SMB vs Scaling Growth vs Mid-Market) with StackPilot 2026 Methodology callout & 'Last Verified' date.\n"
            "- Comprehensive 5-7 tool comparison <table>.\n"
            "- Tool-by-tool H3 evaluations categorized by business maturity level.\n"
            "- Implementation & Migration Guide: Transition timelines, database syncing, and onboarding benchmarks.\n"
            "- Scenario-Based Decision Matrix: 'Which Software Fits Your Business?' table.\n"
            "- FAQ section formatted for FAQPage schema.\n"
            "- Sources & Official Documentation section with direct vendor links."
        )
    }
]


def generate_article_saas(keyword: str, topic_angle: str = "", related_articles: list = None) -> dict:
    '''
    Generate a full SEO-optimized B2B SaaS software review and comparison guide.
    Uses dynamic archetype rotation to prevent cookie-cutter structural monotony.
    '''
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")

    import random
    archetype = random.choice(ARCHETYPES)
    client = genai.Client(api_key=GEMINI_API_KEY)
    angle_text = f"\nSpecific angle/focus: {topic_angle}" if topic_angle else ""
    
    links_text = ""
    if related_articles:
        links_text = "\n[INTERNAL LINKING CANDIDATES]\n" + "\n".join(
            [f"- Guide: '{a.get('title')}' -> URL: {a.get('url')}" for a in related_articles[:3]]
        ) + "\nSeamlessly embed 1 or 2 contextual internal links into appropriate sections using <a href='URL'>Title</a>.\n"

    user_prompt = (
        f"Write a comprehensive, authoritative B2B software buyer guide targeting the primary keyword: '{keyword}'.{angle_text}\n"
        f"Target audience: English-speaking operations leads, founders, and IT procurement managers in US/UK/CA/AU.\n"
        f"{archetype['instruction']}\n\n"
        f"CRITICAL REQUIREMENTS:\n"
        f"1. Compare 5 to 7 real leading software platforms in this exact space.\n"
        f"2. BANNED: Zero ungrounded hype phrases ('dominant force', 'industry standard for a reason', 'best UX', 'game-changer').\n"
        f"3. Must include the exact 2026 Methodology notice with 'Pricing & Feature Data Last Verified: September 18, 2026'.\n"
        f"4. Must include the scenario-based decision matrix table ('Which Software Fits Your Business?').\n"
        f"5. Must conclude with the 'Sources & Official Documentation' section citing official pricing URLs.{links_text}"
    )

    last_error = None
    for model_name in MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT_SAAS,
                        temperature=0.7,
                        response_mime_type="application/json"
                    )
                )

                raw_text = response.text.strip()
                try:
                    data = json.loads(raw_text)
                    return data
                except Exception:
                    json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group(0))
                    raise ValueError("Invalid JSON response from model")

            except Exception as e:
                last_error = e
                print(f"⚠️ {model_name} (Attempt {attempt+1}) temporary error: {e}. Retrying...")
                time.sleep(2)

    raise RuntimeError(f"All models failed to generate SaaS article: {last_error}")
