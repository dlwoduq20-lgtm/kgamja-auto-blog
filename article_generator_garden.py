'''
Home & Garden Article Generator using Gemini API with 7 Dynamic Horticultural Formats.
Eliminates rigid repetitive boilerplates and introduces complete botanical diversification.
'''
import json
import re
import time
import random
from google import genai
from google.genai import types
from config import GEMINI_API_KEY
from prompt_template_garden import SYSTEM_PROMPT_GARDEN

MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash"
]

EXPANDED_FORMATS_GARDEN = [
    # 0. Season-by-Season Planting Calendar & Zone Almanac
    {
        "id": "zone_season_calendar",
        "title": "Zone-by-Zone Seasonal Planting Almanac",
        "keywords": ["when", "timing", "schedule", "calendar", "spring", "fall", "winter", "summer", "frost"],
        "instruction": (
            "【FORMAT: Zone-by-Zone Seasonal Planting Almanac】\n"
            "Structure as an authoritative planting schedule calibrated across climate zones.\n"
            "1. Frost Date Benchmarks & Soil Thermometer Thresholds (Zone 4 through Zone 10).\n"
            "2. Direct Sow vs Indoor Seed Starting Timeline HTML <table> (Zone, Indoor Start Date, Harden Off Window, Harvest Target).\n"
            "3. Succession Planting Rhythms: Staggering 2-week planting blocks for continuous yield.\n"
            "4. Late Season Season-Extenders: Low tunnels, floating row covers, and cold frame management.\n"
            "5. Seasonal Grower's Action Checklist for the upcoming 30 days."
        )
    },
    # 1. Plant Clinic & Diagnostic Guide
    {
        "id": "diagnostic_clinic",
        "title": "Plant Clinic & Diagnostic Pathology Guide",
        "keywords": ["yellow", "curling", "leaves", "dying", "disease", "rot", "blight", "spots", "deficiency", "wilting"],
        "instruction": (
            "【FORMAT: Plant Clinic & Diagnostic Pathology Guide】\n"
            "Structure as a clinical diagnostic teardown for troubled crops.\n"
            "1. Symptom Triage Matrix: Differentiating overwatering, nitrogen lockout, and fungal blight.\n"
            "2. Pathogen vs Nutrient Deficiency Diagnostic HTML <table> (Visual Symptom, Underlying Cause, Fast Remedy, Organic Fix).\n"
            "3. Root Health & Mycorrhizal Soil Ecology: Checking for root rot and anaerobic soil conditions.\n"
            "4. Safe Emergency Interventions: Foliar kelp spray, hydrogen peroxide drenches, and copper fungicides.\n"
            "5. Prevention Protocol: Spacing airflow, drip irrigation, and sanitation."
        )
    },
    # 2. Seed-to-Harvest Step-by-Step Grower's Journal
    {
        "id": "seed_to_harvest_journal",
        "title": "Seed-to-Harvest Step-by-Step Grower's Journal",
        "keywords": ["grow", "how to", "plant", "guide", "care", "harvest", "stages"],
        "instruction": (
            "【FORMAT: Seed-to-Harvest Step-by-Step Grower's Journal】\n"
            "Structure as a chronological cultivation journal from seed sowing to table.\n"
            "1. Phase 1 (Days 1-14): Seed germination medium, bottom heat, and humidity dome protocols.\n"
            "2. Phase 2 (Days 15-45): True leaf development, potting up, and organic feeding ratios.\n"
            "3. Phase 3 (Flowering & Fruit Set): Trellising, pruning suckers, and potassium/phosphorus balance.\n"
            "4. Growth Stage Milestones HTML <table> (Growth Phase, Days from Sowing, Light/Water Needs, Key Milestone).\n"
            "5. Peak Harvest Window & Post-Harvest Curing/Storage Guide."
        )
    },
    # 3. Organic IPM Biological Warfare vs Pest Guide
    {
        "id": "organic_ipm_battle",
        "title": "Organic Integrated Pest Management (IPM) Guide",
        "keywords": ["pest", "bugs", "aphids", "neem", "oil", "spray", "caterpillars", "slugs", "insects", "beetle"],
        "instruction": (
            "【FORMAT: Organic Integrated Pest Management (IPM) Guide】\n"
            "Structure as a biological defense playbook targeting garden invaders.\n"
            "1. Pest Identification & Action Thresholds: When to intervene vs when nature handles it.\n"
            "2. Three-Tiered Organic Defense Matrix HTML <table> (Target Pest, Tier 1 Cultural Control, Tier 2 Biological Predators, Tier 3 Organic Spray).\n"
            "3. Beneficial Insect Habitat: Attracting parasitic wasps, lacewings, and ladybugs with companion flowers.\n"
            "4. Organic Spray Chemistry & Timing: Applying neem, spinosad, and insecticidal soap without scorching foliage or harming bees.\n"
            "5. Post-Infestation Soil Rehabilitation."
        )
    },
    # 4. Cultivar Showdown & Harvest Yield Benchmarks
    {
        "id": "cultivar_taste_trial",
        "title": "Cultivar Showdown & Yield Benchmarks",
        "keywords": ["best", "varieties", "cultivars", "types", "heirloom", "hybrid", "flavor", "yield"],
        "instruction": (
            "【FORMAT: Cultivar Showdown & Yield Benchmarks】\n"
            "Structure as a trial garden evaluation comparing top performing varieties.\n"
            "1. Heirloom vs Hybrid Dilemma: Disease resistance vs unmatched vintage flavor.\n"
            "2. 5-7 Cultivar Benchmark HTML <table> (Variety, Days to Maturity, Disease Resistance Codes, Flavor Profile, Yield/Plant).\n"
            "3. Microclimate Matching: Cultivars bred for high heat/humidity vs cool northern short seasons.\n"
            "4. Seed Saving Viability: Open-pollinated true-to-type harvesting protocols.\n"
            "5. Grower's Recommendation Verdict for different backyard setups."
        )
    },
    # 5. Soil Science, Living Compost & Biochar Teardown
    {
        "id": "soil_microbiome_alchemy",
        "title": "Soil Science & Living Compost Teardown",
        "keywords": ["soil", "compost", "amendment", "fertilizer", "clay", "sand", "ph", "organic matter", "mulch"],
        "instruction": (
            "【FORMAT: Soil Science & Living Compost Teardown】\n"
            "Structure as a field soil biology handbook for converting dead dirt into rich living soil.\n"
            "1. Soil Texture Fingerprinting: The jar test for sand, silt, and heavy clay proportions.\n"
            "2. Amendment Chemistry HTML <table> (Soil Challenge, Organic Amendment, Application Rate/100 sq ft, Optimal Soil pH Range).\n"
            "3. The Hot Compost Recipe: Carbon-to-nitrogen ratios (30:1), internal thermophilic pile temps, and turning schedules.\n"
            "4. Mycorrhizae & Biochar Inoculation: Building permanent microbial sponges.\n"
            "5. Fall Soil Building & Cover Crop Strategies."
        )
    },
    # 6. Micro-Gardening & Small Space Architecture
    {
        "id": "small_space_blueprint",
        "title": "Small-Space & Raised Bed Architecture",
        "keywords": ["container", "pot", "small", "raised bed", "patio", "balcony", "indoor", "space"],
        "instruction": (
            "【FORMAT: Small-Space & Raised Bed Architecture】\n"
            "Structure as an intensive high-yield blueprint for urban lots and small yards.\n"
            "1. Vertical Architecture: A-frame trellises, cattle panel arches, and wall planters.\n"
            "2. Container Volume & Soil Mix Matrix HTML <table> (Crop, Minimum Pot Gallons, Soil Depth, Trellis Required, Yield Expectation).\n"
            "3. Self-Watering Sub-Irrigated Planters (SIPs) & Drip Automation for small footprints.\n"
            "4. Interplanting & Square Foot Density: Maximizing every square inch without nutrient starvation.\n"
            "5. Seasonal Rotation for Container Gardens."
        )
    }
]


def select_format_garden(topic: str) -> dict:
    topic_lower = topic.lower()
    scored = []
    for fmt in EXPANDED_FORMATS_GARDEN:
        score = sum(1 for kw in fmt["keywords"] if kw.lower() in topic_lower)
        if score > 0:
            scored.append((score, fmt))
    if scored:
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]
    h_idx = sum(ord(c) for c in topic) % len(EXPANDED_FORMATS_GARDEN)
    return EXPANDED_FORMATS_GARDEN[h_idx]


def generate_article_garden(
    keyword: str,
    topic_angle: str = "",
    topic: str = "",
    avoid_topics: list = None,
    related_articles: list = None,
    **kwargs
) -> dict:
    '''
    Generate an in-depth home horticulture guide with dynamic growing formats,
    zero boilerplate, and deep field-tested E-E-A-T.
    '''
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")

    full_subject = topic_angle or topic or keyword
    if keyword and keyword.lower() not in full_subject.lower():
        full_subject = f"{keyword}: {full_subject}"

    selected_format = select_format_garden(full_subject)
    print(f"📖 [Selected Format (Garden)] '{selected_format['title']}' (ID: {selected_format['id']})")

    client = genai.Client(api_key=GEMINI_API_KEY)

    links_text = ""
    if related_articles:
        links_text = "\n[Contextual Internal Linking Candidates]\n" + "\n".join(
            [f"- Guide: '{a.get('title')}' -> URL: {a.get('url')}" for a in related_articles[:3]]
        ) + "\nNaturally link to 1-2 candidate articles where contextually relevant.\n"

    user_prompt = (
        f"Write a masterclass gardening guide for GreenThumb Garden targeting:\n"
        f"Subject: {full_subject}\n\n"
        f"【ASSIGNED HORTICULTURAL FORMAT】\n"
        f"{selected_format['instruction']}\n\n"
        f"CORE REQUIREMENTS:\n"
        f"1. Zero generic fluff (no 'nature's miracle', 'a green thumb is all you need', 'fast-paced world').\n"
        f"2. 🚫 NO mechanical fixed Extension badges or boilerplate grey sources boxes. Integrate USDA zones, soil temps, and extension science organically.\n"
        f"3. Must include at least 1 comprehensive responsive HTML <table>.\n"
        f"4. Length: Thorough, practical grower's manual (1,800+ words).{links_text}"
    )

    last_error = None
    for model_name in MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT_GARDEN,
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
                data["h1"] = data.get("h1") or data.get("title", keyword)
                data["meta_title"] = data.get("meta_title") or data.get("title", keyword)
                data["meta_description"] = data.get("meta_description") or data.get("excerpt", "")

                # Fetch hero illustration bytes
                try:
                    from image_manager_garden import fetch_garden_image_bytes
                    img_prompt = data.get("image_prompt_en", f"{keyword} organic garden illustration")
                    hero_bytes = fetch_garden_image_bytes(img_prompt)
                    data["hero_bytes"] = hero_bytes
                except Exception as e:
                    print(f"⚠️ [Garden Hero Image] Error: {e}")
                    data["hero_bytes"] = None

                return data

            except Exception as e:
                last_error = e
                print(f"⚠️ {model_name} (Attempt {attempt+1}) error: {e}. Retrying...")
                time.sleep(2)

    raise RuntimeError(f"All models failed to generate Garden article: {last_error}")
