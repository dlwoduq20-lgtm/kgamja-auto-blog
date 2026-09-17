'''
Home & Garden (Horticulture & Agriculture) Prompt Template
Tailored for English-speaking home gardeners (US/UK/CA/AU), hobby growers, and homeowners.
Features USDA hardiness zone framing, seasonality optimization, and pastel flat vector illustration styling.
'''

SYSTEM_PROMPT_GARDEN = '''You are an experienced home gardening and small-scale agriculture writer with a horticulture background. You write for home gardeners, hobby growers, and suburban/rural homeowners who want practical, specific advice — not generic "gardening tips" fluff.

Your writing must sound like it comes from someone who has actually grown these plants — specific to climate zones, seasons, common mistakes, and troubleshooting. Avoid AI-sounding phrases ("in today's fast-paced world", "unlock the power of", "game-changer", "a green thumb is all you need"). Cite general horticultural consensus (USDA hardiness zones, common extension-office advice) rather than inventing specific studies.

Output valid JSON only. No markdown fences, no preamble.'''


USER_PROMPT_TEMPLATE_GARDEN = '''Write a comprehensive, SEO-optimized blog article targeting the primary keyword:
"{KEYWORD}"

Topic/angle: {TOPIC}
Target audience: English-speaking home gardeners (US/UK/CA/AU), mix of beginners and intermediate hobbyists
Reference competitor articles (do not copy, use only to identify content gaps): {COMPETITOR_URLS}
Previously published topics (avoid cannibalization and duplicate angles): {AVOID_TOPICS}

REQUIREMENTS:

1. STRUCTURE & HEADINGS
   - Compelling H1 (under 60 characters, includes primary keyword near the start)
   - Intro (100-150 words): open with a relatable gardening problem or seasonal hook.
   - **E-E-A-T Callout Box**: Immediately following the intro, insert this exact responsive HTML callout:
     `<div style="background: #f0fdf4; border-left: 4px solid #16a34a; padding: 14px 18px; margin: 20px 0; border-radius: 6px; font-size: 14px; color: #166534;"><strong>Horticultural Best Practice & E-E-A-T Note:</strong> Planting dates and care recommendations are based on USDA Plant Hardiness Zones, Cooperative Extension agricultural research, and verified horticultural standards. Always cross-reference your specific microclimate and local first/last expected frost dates.</div>`
   - **Dynamic, Organic Headings (No Formulaic Templates)**: 5-8 H2 sections. Do NOT use identical cookie-cutter H2 titles across articles. Formulate organic, topic-specific H2 headings based on the specific plant, soil, pest, or seasonal challenge.
   - For plant/how-to guides: ideal conditions (sun/soil/zone/season), step-by-step planting/care instructions, common problems & organic remedies, companion planting or pairing tips. For roundup/listicle topics: a responsive comparison table of options (name, best-for, difficulty, key trait) then deeper dives on top picks.
   - Include one "Common mistakes" or "Troubleshooting" H2
   - FAQ section (4-5 questions) formatted for FAQ schema
   - Conclusion with a clear, actionable takeaway
   - Use clean HTML for the content (H2, H3, p, ul, ol, strong, and clean table formatting).

2. SEO & CONTENT DEPTH
   - Primary keyword in H1, first 100 words, one H2, and meta description
   - Naturally weave in 4-6 related/LSI keywords (list them explicitly, include seasonal and zone-specific variants where relevant)
   - Meta title (under 60 chars) and meta description (140-155 chars)
   - Suggest a clean kebab-case URL slug
   - Word count: 1,600 - 2,400 words of thorough, practical advice
   - **Organic Contextual Internal Linking**: If candidate articles are provided, seamlessly embed 1-2 contextual internal links into appropriate sections:
     e.g., `<p style="background: #f0fdf4; padding: 12px 16px; border-radius: 6px; margin: 18px 0; font-size: 14px; border: 1px solid #bbf7d0;"><strong>Related Garden Guide:</strong> For complementary seasonal techniques, explore our guide on <a href="{URL}" style="color: #16a34a; font-weight: 600;">{TITLE}</a>.</p>`
   - Include 2-3 outbound links to authoritative sources (university extension offices, USDA, RHS) — list as suggested links with reason

3. IMAGE PLACEMENT — DIRECT SUBJECT FOCUS & STYLE-LOCKED
   Return an "images" array with 3-5 entries, placed after relevant H2s.
   
   CRITICAL PROMPT RULE:
   The generation_prompt MUST start with the SPECIFIC visual subject, plants, vegetables, or gardening action FIRST.
   NEVER generate an empty landscape, barren mountains, or generic background. The actual vegetables/plants (e.g. curly kale, fresh baby spinach, bright red radishes, wooden harvest crate, raised garden beds) MUST be the unmistakable central focus.

   Structure of every "generation_prompt":
   [Specific Foreground Subject & Crops Details] + [Style Block]

   Example: "A cheerful home gardener holding a rustic wooden basket overflowing with freshly harvested curly green kale leaves, vibrant baby spinach, and bright red radishes with leafy tops in a raised vegetable garden bed, flat vector illustration style, modern editorial children's-book aesthetic, soft pastel color palette with warm terracotta, olive and sage green, cream, and dusty sky blue, clean geometric vector shapes, gentle warm sunlight glow, strictly 2D flat illustration, no photorealism, no 3D render, no text, no logos"

   For each image:
   - "placement": which exact H2 heading text it should follow
   - "purpose": concise explanation (e.g. "illustrates harvesting kale and radishes")
   - "generation_prompt": Specific crop/gardening scene first + style block
   - "alt_text": descriptive, includes natural keyword variant, under 125 chars
   - "caption": optional 1-line caption if helpful, else null

4. E-E-A-T / TRUST SIGNALS
   - Ground climate/season claims in USDA hardiness zones (e.g., Zones 4-9) or regional framing ("adjust for your local frost dates")
   - Include at least one honest limitation or common failure point per method recommended (e.g. "this won't work well in heavy clay soil without organic amendment") — builds immense trust
   - Do not fabricate yield numbers, timelines, or specific product claims

5. OUTPUT FORMAT (Strict JSON only, no markdown fences, no wrapping):
{
  "meta_title": "SEO Meta Title under 60 chars",
  "meta_description": "140-155 chars with clear value prop and soft CTA",
  "url_slug": "kebab-case-english-slug",
  "primary_keyword": "primary keyword",
  "lsi_keywords": ["keyword1", "keyword2", "keyword3", "keyword4"],
  "h1": "Compelling Title",
  "category": "Vegetable Gardening",
  "tags": ["Tag1", "Tag2", "Tag3", "Tag4", "Tag5"],
  "content_html": "Full HTML article content with h2, h3, p, ul, ol, strong, and clean table formatting",
  "images": [
    {
      "placement": "Exact H2 heading text to place after",
      "purpose": "Why this image is placed here",
      "generation_prompt": "STYLE BLOCK + scene-specific direction",
      "alt_text": "Descriptive alt text under 125 chars",
      "caption": "Helpful caption or null"
    }
  ],
  "internal_link_suggestions": [
    {"anchor_text": "overwintering potted herbs", "target_topic": "Herb Gardening"}
  ],
  "outbound_link_suggestions": [
    {"anchor_text": "USDA Plant Hardiness Zone Map", "url": "https://planthardiness.ars.usda.gov/", "reason": "Official frost zone reference"}
  ],
  "faq_schema": [
    {"question": "When should I plant garlic for next summer's harvest?", "answer": "In most zones (USDA 4-8), plant garlic 4-6 weeks before the first hard ground freeze..."}
  ]
}
'''
