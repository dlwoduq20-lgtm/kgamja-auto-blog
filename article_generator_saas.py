'''
US/Global B2B SaaS Article Generator using Gemini API with 7 Dynamic Narrative Formats.
Eliminates rigid repetitive templates and introduces full architectural diversification.
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
    "gemini-3.8-flash"
]

EXPANDED_FORMATS_SAAS = [
    # 0. Head-to-Head Showdown
    {
        "id": "head_to_head_showdown",
        "title": "Head-to-Head Showdown & Category Battle",
        "keywords": ["vs", "versus", "comparison", "alternative", "showdown", "battle", "competitor"],
        "instruction": (
            "【FORMAT: Head-to-Head Showdown & Category Battle】\n"
            "Deliver an unsparing, engineering-level showdown between leading platforms in this category.\n"
            "1. Executive Dilemma: The exact architectural tipping point where teams migrate from Tool A to Tool B.\n"
            "2. Head-to-Head Feature Scorecard HTML <table> (Feature, Tool A Rating, Tool B Rating, Critical Limitation).\n"
            "3. Deep Feature Teardown: Testing API sync latency, webhook reliability, and edge-case failures.\n"
            "4. Transparent Pricing Audit: Volume-based tier increases, seat expansion costs, and hidden contract minimums.\n"
            "5. Final Procurement Verdict: Exact decision criteria for when to choose each tool."
        )
    },
    # 1. Total Cost of Ownership (TCO) & Pricing Teardown
    {
        "id": "tco_pricing_breakdown",
        "title": "Total Cost of Ownership (TCO) & Pricing Audit",
        "keywords": ["pricing", "cost", "cheap", "free", "enterprise", "tco", "budget", "billing"],
        "instruction": (
            "【FORMAT: Total Cost of Ownership (TCO) & Pricing Audit】\n"
            "Audit the true annual economics of deploying these platforms beyond advertised sticker prices.\n"
            "1. The Sticker Price Illusion: How seat licensing, monthly usage overages, and add-on modules double bills.\n"
            "2. 3-Year TCO Simulation Model HTML <table> (Platform, 10-Seat Annual Cost, 50-Seat Cost, API Overage Traps).\n"
            "3. Contract Negotiation Levers: 3 clauses IT procurement teams must negotiate before signing.\n"
            "4. Platform-by-Platform Cost-Efficiency Breakdowns for early-stage SMBs vs scaling growth teams.\n"
            "5. ROI Breakeven Timeline & Unit Economics Analysis."
        )
    },
    # 2. 30-Day Implementation & Migration Blueprint
    {
        "id": "implementation_roadmap",
        "title": "30-Day Implementation & Migration Blueprint",
        "keywords": ["setup", "guide", "implementation", "migration", "switch", "deployment", "integration", "how to"],
        "instruction": (
            "【FORMAT: 30-Day Implementation & Migration Blueprint】\n"
            "Structure as an operational deployment runbook for engineering and operations managers.\n"
            "1. Week 1: Data extraction, schema mapping, and API authentication setup.\n"
            "2. Week 2: Parallel run verification and webhook payload error handling.\n"
            "3. Week 3: End-user onboarding, RBAC permission tiers, and legacy system cutover.\n"
            "4. Tool Migration Friction Comparison HTML <table> (Tool, Average Setup Days, Engineering Lift, Rollback Risk).\n"
            "5. Post-Launch Health Checks & Day-30 Audit Checklist."
        )
    },
    # 3. Underdog Disruptors & Lean Challenger Guide
    {
        "id": "underdog_challengers",
        "title": "Underdog Disruptors & Modern Challenger Guide",
        "keywords": ["best", "tools", "software", "top", "review", "apps", "platforms"],
        "instruction": (
            "【FORMAT: Underdog Disruptors & Modern Challenger Guide】\n"
            "Focus on lean, modern, high-velocity challenger tools disrupting bloated legacy incumbents.\n"
            "1. Why Legacy Giants Are Losing Modern Engineering Teams (feature bloat, slow UX, predatory pricing).\n"
            "2. The 5 Top Disruptive Contenders: In-depth evaluations of speed, modern API design, and developer ergonomics.\n"
            "3. Comprehensive Feature & Price Parity HTML <table>.\n"
            "4. Migration Feasibility: Exporting data from incumbents without workflow disruption.\n"
            "5. Decision Framework: When to stay with legacy safety vs when to switch to agile disruptors."
        )
    },
    # 4. Feature Friction & Stress-Test Benchmarks
    {
        "id": "stress_test_benchmarks",
        "title": "Feature Friction & High-Scale Stress Test",
        "keywords": ["enterprise", "scale", "performance", "api", "security", "infrastructure"],
        "instruction": (
            "【FORMAT: Feature Friction & High-Scale Stress Test】\n"
            "Analyze how platforms perform under extreme transactional volume and concurrency.\n"
            "1. What Breaks at 10x Scale: Rate limit throttling, database locking, and delayed reporting.\n"
            "2. Platform Concurrency & Rate Limit Benchmark HTML <table> (Tool, API Limit/sec, SSO Enforcement, SLA Guarantee).\n"
            "3. Security & Governance Audit: SOC2 Type II, HIPAA compliance, audit logging, and RBAC granularities.\n"
            "4. Operational Edge Cases: How each tool handles failed webhook retries and silent data drops.\n"
            "5. Enterprise Procurement Checklist: Non-negotiable contract riders."
        )
    }
]


def select_format_saas(topic: str) -> dict:
    topic_lower = topic.lower()
    scored = []
    for fmt in EXPANDED_FORMATS_SAAS:
        score = sum(1 for kw in fmt["keywords"] if kw.lower() in topic_lower)
        if score > 0:
            scored.append((score, fmt))
    if scored:
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]
    h_idx = sum(ord(c) for c in topic) % len(EXPANDED_FORMATS_SAAS)
    return EXPANDED_FORMATS_SAAS[h_idx]


def generate_article_saas(keyword: str, topic: str = "", related_articles: list = None) -> dict:
    '''
    Generate an in-depth B2B SaaS evaluation article with dynamic review formats,
    zero boilerplate, and deep empirical rigor.
    '''
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")

    full_subject = f"{keyword}: {topic}" if topic else keyword
    selected_format = select_format_saas(full_subject)
    print(f"📖 [Selected Format (SaaS)] '{selected_format['title']}' (ID: {selected_format['id']})")

    client = genai.Client(api_key=GEMINI_API_KEY)

    links_text = ""
    if related_articles:
        links_text = "\n[Contextual Internal Linking Candidates]\n" + "\n".join(
            [f"- Guide: '{a.get('title')}' -> URL: {a.get('url')}" for a in related_articles[:3]]
        ) + "\nNaturally link to 1-2 candidate articles where contextually relevant.\n"

    user_prompt = (
        f"Write an authoritative B2B SaaS evaluation guide for StackPilot targeting:\n"
        f"Subject: {full_subject}\n\n"
        f"【ASSIGNED REVIEW FORMAT】\n"
        f"{selected_format['instruction']}\n\n"
        f"CORE REQUIREMENTS:\n"
        f"1. Zero generic marketing clichés (no 'game-changer', 'revolutionize', 'fast-paced world').\n"
        f"2. 🚫 NO mechanical fixed methodology badges or boilerplate grey sources boxes. Integrate verified vendor pricing and API specs organically into the text.\n"
        f"3. Must include at least 1 comprehensive responsive HTML <table>.\n"
        f"4. Length: Comprehensive, deep operational teardown (2,000+ words).{links_text}"
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
                except Exception:
                    json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                    if json_match:
                        data = json.loads(json_match.group(0))
                    else:
                        raise ValueError("Invalid JSON response from model")

                data["format_id"] = selected_format["id"]
                return data

            except Exception as e:
                last_error = e
                print(f"⚠️ {model_name} (Attempt {attempt+1}) error: {e}. Retrying...")
                time.sleep(2)

    raise RuntimeError(f"All models failed to generate SaaS article: {last_error}")
