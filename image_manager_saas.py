'''
B2B SaaS Dynamic Topic-Tailored Editorial Banner Generator for StackPilot
Produces 100% watermark-free, razor-sharp, topic-specific enterprise review banners (1200x675).
Every category has a bespoke color scheme and specialized UI dashboard visual
(e.g. IDE code editor for AI coding, deliverability gauge for cold email,
DAG workflow canvas for automation, lead verification cards for sales, etc.)
'''
import os
import io
import sys
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')


def get_ui_font(size: int, bold: bool = True) -> ImageFont.ImageFont:
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf"
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


# ==============================================================================
# SPECIALIZED TOPIC UI DRAWERS
# ==============================================================================

def draw_header_bar(draw, x1, y1, x2, title_text):
    draw.rectangle([x1+2, y1+2, x2-2, y1+48], fill="#1e293b")
    draw.ellipse([x1+18, y1+18, x1+30, y1+30], fill="#ef4444")
    draw.ellipse([x1+38, y1+18, x1+50, y1+30], fill="#f59e0b")
    draw.ellipse([x1+58, y1+18, x1+70, y1+30], fill="#10b981")
    draw.text((x1+85, y1+16), title_text, fill="#f8fafc", font=get_ui_font(13, True))


def draw_sales_intelligence(draw, x1, y1, x2, y2, accent):
    draw.rounded_rectangle([x1, y1, x2, y2], radius=16, fill="#1e1b4b", outline=accent, width=2)
    draw_header_bar(draw, x1, y1, x2, "B2B Prospect Intelligence & Direct-Dial Verify")
    leads = [
        ("VP of Revenue Operations", "Enterprise SaaS (1,000+ FTE)", "Direct: 94% Verified", "#10b981"),
        ("Head of Growth Marketing", "Mid-Market FinTech (250 FTE)", "Mobile Dial: 91% Match", "#818cf8"),
        ("Chief Technology Officer", "Cloud Infrastructure (500 FTE)", "Verified Work Email", "#38bdf8"),
        ("Director of Procurement", "Global Logistics (5,000+ FTE)", "GDPR & CCPA Compliant", "#f59e0b")
    ]
    for idx, (title_lead, comp, tag, col) in enumerate(leads):
        cy = y1 + 68 + idx * 88
        draw.rounded_rectangle([x1+25, cy, x2-25, cy+74], radius=8, fill="#312e81", outline="#4338ca", width=1)
        draw.ellipse([x1+40, cy+18, x1+68, cy+46], fill="#4338ca")
        draw.text((x1+49, cy+21), "✓", fill="#10b981", font=get_ui_font(16, True))
        draw.text((x1+85, cy+14), title_lead, fill="#ffffff", font=get_ui_font(14, True))
        draw.text((x1+85, cy+38), comp, fill="#c7d2fe", font=get_ui_font(11, False))
        draw.text((x2-175, cy+26), tag, fill=col, font=get_ui_font(12, True))
    draw.rounded_rectangle([x1+25, y2-75, x2-25, y2-15], radius=8, fill="#4338ca")
    draw.text((x1+40, y2-55), "Top Evaluated: ZoomInfo • Apollo.io ($49) • Cognism • Seamless", fill="#ffffff", font=get_ui_font(12, True))


def draw_email_deliverability(draw, x1, y1, x2, y2, accent):
    draw.rounded_rectangle([x1, y1, x2, y2], radius=16, fill="#042f2e", outline=accent, width=2)
    draw_header_bar(draw, x1, y1, x2, "Outbound SMTP & Deliverability Monitor")
    gx1, gy1, gx2, gy2 = x1+40, y1+75, x1+220, y1+255
    draw.ellipse([gx1, gy1, gx2, gy2], outline="#134e4a", width=16)
    draw.arc([gx1, gy1, gx2, gy2], start=135, end=405, fill="#10b981", width=16)
    draw.text((gx1+40, gy1+60), "98.4%", fill="#ffffff", font=get_ui_font(32, True))
    draw.text((gx1+35, gy1+105), "INBOX RATE", fill="#5eead4", font=get_ui_font(11, True))
    draw.text((gx2+30, gy1+25), "• Domain Warmup: ACTIVE (Unlimited)", fill="#f0fdfa", font=get_ui_font(13, True))
    draw.text((gx2+30, gy1+55), "• SPF / DKIM / DMARC: 100% PASS", fill="#6ee7b7", font=get_ui_font(13, True))
    draw.text((gx2+30, gy1+85), "• Smart Multi-Inbox Rotation: 50 ESPs", fill="#99f6e4", font=get_ui_font(13, False))
    draw.text((gx2+30, gy1+115), "• Bounce Shield Protection: Real-Time", fill="#cbd5e1", font=get_ui_font(13, False))
    platforms = [
        ("Instantly.ai Hyper", "98.4% Inbox", "Best for Scaling ($37)", "#10b981"),
        ("Smartlead.ai Scale", "97.8% Inbox", "Best API & Webhooks ($39)", "#2dd4bf"),
        ("Lemlist Multichannel", "96.2% Inbox", "Best Personalization ($59)", "#38bdf8")
    ]
    for idx, (name, rate, tag, col) in enumerate(platforms):
        cy = y1 + 285 + idx * 75
        draw.rounded_rectangle([x1+25, cy, x2-25, cy+62], radius=8, fill="#115e59", outline="#14b8a6", width=1)
        draw.text((x1+40, cy+12), name, fill="#ffffff", font=get_ui_font(14, True))
        draw.text((x1+40, cy+35), tag, fill="#ccfbf1", font=get_ui_font(11, False))
        draw.text((x2-140, cy+20), rate, fill=col, font=get_ui_font(14, True))


def draw_code_editor(draw, x1, y1, x2, y2, accent):
    draw.rounded_rectangle([x1, y1, x2, y2], radius=16, fill="#0d1117", outline=accent, width=2)
    draw_header_bar(draw, x1, y1, x2, "copilot_engine.py - AI Assistant Benchmark")
    code_lines = [
        ("import", "#ff7b72", " enterprise_ai", "#c9d1d9"),
        ("from", "#ff7b72", " models import Copilot, Claude_35", "#c9d1d9"),
        ("", "#c9d1d9", "", "#c9d1d9"),
        ("def", "#ff7b72", " analyze_codebase(repo: str):", "#79c0ff"),
        ("    # 2026 Evaluation: 98.4% Context Recall", "#8b949e", "", "#8b949e"),
        ("    ai = Copilot.connect(security='SOC2_Type_II')", "#d2a8ff", "", "#c9d1d9"),
        ("    suggestions = ai.generate_diff(latency='120ms')", "#7ee787", "", "#c9d1d9"),
        ("    return suggestions.verify_compliance()", "#79c0ff", "", "#c9d1d9"),
    ]
    font_code = get_ui_font(14, False)
    for idx, (t1, c1, t2, c2) in enumerate(code_lines):
        ly = y1 + 75 + idx * 36
        draw.text((x1+25, ly), str(idx+1), fill="#484f58", font=font_code)
        draw.text((x1+60, ly), t1, fill=c1, font=font_code)
        w1 = draw.textbbox((0, 0), t1, font=font_code)[2] - draw.textbbox((0, 0), t1, font=font_code)[0] + 6
        draw.text((x1+60+w1, ly), t2, fill=c2, font=font_code)
    pill_y = y2 - 110
    draw.rounded_rectangle([x1+25, pill_y, x2-25, pill_y+85], radius=10, fill="#1f2937", outline="#3b82f6", width=2)
    draw.text((x1+40, pill_y+15), "✦ AI Copilot Active: Multi-File Context Enabled", fill="#93c5fd", font=get_ui_font(13, True))
    draw.text((x1+40, pill_y+42), "Top Picks: GitHub Copilot ($19) • Cursor ($20) • Tabnine", fill="#e2e8f0", font=get_ui_font(12, False))


def draw_workflow_nodes(draw, x1, y1, x2, y2, accent):
    draw.rounded_rectangle([x1, y1, x2, y2], radius=16, fill="#2e1065", outline=accent, width=2)
    draw_header_bar(draw, x1, y1, x2, "Workflow DAG Canvas: Make vs. Zapier vs. n8n")
    nodes = [
        (x1+40, y1+100, "1. Inbound Webhook", "Payload Captured (JSON)", "#3b82f6"),
        (x1+290, y1+70, "2A. AI Filter & Enrich", "GPT-4o Auto-Triage", "#10b981"),
        (x1+290, y1+170, "2B. CRM Sync Router", "Salesforce & HubSpot", "#a855f7"),
        (x1+40, y1+270, "3. Multi-Channel Alert", "Slack + Email Escalation", "#f59e0b")
    ]
    draw.line([(x1+200, y1+130), (x1+290, y1+105)], fill="#a855f7", width=3)
    draw.line([(x1+200, y1+130), (x1+290, y1+205)], fill="#a855f7", width=3)
    draw.line([(x1+390, y1+240), (x1+200, y1+300)], fill="#a855f7", width=3)
    for nx, ny, ntitle, ndesc, ncol in nodes:
        draw.rounded_rectangle([nx, ny, nx+230, ny+65], radius=8, fill="#581c87", outline=ncol, width=2)
        draw.text((nx+15, ny+12), ntitle, fill="#ffffff", font=get_ui_font(13, True))
        draw.text((nx+15, ny+36), ndesc, fill="#e9d5ff", font=get_ui_font(11, False))
    draw.rounded_rectangle([x1+25, y2-150, x2-25, y2-20], radius=10, fill="#3b0764", outline="#9333ea", width=1)
    draw.text((x1+40, y2-135), "BENCHMARK: COMPLEX LOGIC & COST PER TASK", fill="#f5d0fe", font=get_ui_font(11, True))
    draw.text((x1+40, y2-105), "• Make.com: Visual DAG Winner • Best Pricing ($9-$29/mo)", fill="#ffffff", font=get_ui_font(12, False))
    draw.text((x1+40, y2-75), "• Zapier: Most Ecosystem Integrations (6,000+ Apps)", fill="#e9d5ff", font=get_ui_font(12, False))
    draw.text((x1+40, y2-45), "• n8n: Best Self-Hosted Enterprise Open-Source Engine", fill="#c084fc", font=get_ui_font(12, False))


def draw_video_studio(draw, x1, y1, x2, y2, accent):
    draw.rounded_rectangle([x1, y1, x2, y2], radius=16, fill="#2a1208", outline=accent, width=2)
    draw_header_bar(draw, x1, y1, x2, "AI Video Studio & Avatar Synthesis")
    vx1, vy1, vx2, vy2 = x1+35, y1+75, x2-35, y1+260
    draw.rounded_rectangle([vx1, vy1, vx2, vy2], radius=10, fill="#1c0b05", outline="#ea580c", width=1)
    draw.ellipse([x1+240, y1+135, x1+310, y1+205], fill="#ea580c")
    draw.polygon([(x1+270, y1+155), (x1+270, y1+185), (x1+295, y1+170)], fill="#ffffff")
    draw.rounded_rectangle([vx1+15, vy2-35, vx1+120, vy2-12], radius=4, fill="#000000")
    draw.text((vx1+25, vy2-30), "4K UHD 60fps", fill="#fb923c", font=get_ui_font(11, True))
    draw.text((vx2-120, vy2-30), "01:24 / 03:00", fill="#e2e8f0", font=get_ui_font(11, False))
    platforms = [
        ("Synthesia 2.0", "Photorealism: 9.8/10", "140+ Languages ($22)", "#10b981"),
        ("HeyGen Enterprise", "Instant Avatar Clones", "Realtime API ($29)", "#fb923c"),
        ("Descript", "Audio Script Timeline", "Automatic Filler Cut", "#38bdf8")
    ]
    for idx, (name, score, tag, col) in enumerate(platforms):
        cy = y1 + 285 + idx * 75
        draw.rounded_rectangle([x1+25, cy, x2-25, cy+62], radius=8, fill="#431407", outline="#7c2d12", width=1)
        draw.text((x1+40, cy+12), name, fill="#ffffff", font=get_ui_font(14, True))
        draw.text((x1+40, cy+35), tag, fill="#fed7aa", font=get_ui_font(11, False))
        draw.text((x2-170, cy+20), score, fill=col, font=get_ui_font(13, True))


def draw_voice_audio(draw, x1, y1, x2, y2, accent):
    draw.rounded_rectangle([x1, y1, x2, y2], radius=16, fill="#2b0923", outline=accent, width=2)
    draw_header_bar(draw, x1, y1, x2, "AI Voice Synthesis & Frequency Equalizer")
    bars_x = x1 + 45
    heights = [30, 65, 110, 80, 140, 95, 130, 60, 115, 85, 150, 70, 100, 45, 90, 120]
    for idx, bh in enumerate(heights):
        bx = bars_x + idx * 30
        draw.rounded_rectangle([bx, y1+220-bh, bx+16, y1+220], radius=4, fill="#f43f5e")
    draw.text((x1+45, y1+235), "48kHz Ultra HD Studio Clarity • Multi-Emotion Voice Modulation", fill="#fda4af", font=get_ui_font(12, True))
    platforms = [
        ("ElevenLabs Pro", "Ultra-Realistic Inflection", "Voice Library Winner", "#10b981"),
        ("PlayHT Enterprise", "Sub-100ms Latency API", "Best Streaming ($39)", "#f43f5e"),
        ("Murf.ai Business", "Built-In Voiceover Studio", "Commercial Rights", "#38bdf8")
    ]
    for idx, (name, desc, tag, col) in enumerate(platforms):
        cy = y1 + 275 + idx * 75
        draw.rounded_rectangle([x1+25, cy, x2-25, cy+62], radius=8, fill="#4c0519", outline="#881337", width=1)
        draw.text((x1+40, cy+12), name, fill="#ffffff", font=get_ui_font(14, True))
        draw.text((x1+40, cy+35), desc, fill="#fecdd3", font=get_ui_font(11, False))
        draw.text((x2-170, cy+20), tag, fill=col, font=get_ui_font(13, True))


def draw_customer_support(draw, x1, y1, x2, y2, accent):
    draw.rounded_rectangle([x1, y1, x2, y2], radius=16, fill="#082f49", outline=accent, width=2)
    draw_header_bar(draw, x1, y1, x2, "AI Chatbot & CSAT Resolution Engine")
    bubbles = [
        ("Customer: Where is my order #58210? Can I reroute it?", False, y1+75),
        ("AI Bot: Routed to FedEx Hub! New ETA is tomorrow 2 PM. ✓", True, y1+145),
        ("Customer: That was so fast, thank you!", False, y1+225)
    ]
    for text, is_bot, by in bubbles:
        if is_bot:
            draw.rounded_rectangle([x1+100, by, x2-30, by+58], radius=10, fill="#0284c7", outline="#38bdf8", width=1)
            draw.text((x1+115, by+18), text, fill="#ffffff", font=get_ui_font(12, True))
        else:
            draw.rounded_rectangle([x1+30, by, x2-100, by+58], radius=10, fill="#0c4a6e", outline="#075985", width=1)
            draw.text((x1+45, by+18), text, fill="#e0f2fe", font=get_ui_font(12, False))
    draw.rounded_rectangle([x1+25, y2-150, x2-25, y2-20], radius=10, fill="#0369a1", outline="#38bdf8", width=1)
    draw.text((x1+40, y2-135), "PERFORMANCE AUDIT: RESOLUTION & DEFLECTION", fill="#e0f2fe", font=get_ui_font(11, True))
    draw.text((x1+40, y2-105), "• Fin by Intercom: 82% Deflection Rate • Zero Setup Lag", fill="#ffffff", font=get_ui_font(12, False))
    draw.text((x1+40, y2-75), "• Ada CX: 78% Omnichannel First-Contact Resolution", fill="#bae6fd", font=get_ui_font(12, False))
    draw.text((x1+40, y2-45), "• Gorgias: Deep Shopify & Klaviyo Native Sync Winner", fill="#bae6fd", font=get_ui_font(12, False))


def draw_meeting_notes(draw, x1, y1, x2, y2, accent):
    draw.rounded_rectangle([x1, y1, x2, y2], radius=16, fill="#1c1917", outline=accent, width=2)
    draw_header_bar(draw, x1, y1, x2, "AI Meeting Transcription & Action Items")
    items = [
        ("Action Item 1: Finalize enterprise security review", "Assigned: DevOps Lead", "COMPLETED", "#10b981"),
        ("Action Item 2: Deploy multi-domain outreach campaign", "Assigned: Sales Team", "IN PROGRESS", "#f59e0b"),
        ("Action Item 3: Update Q3 carrier SLA benchmark", "Assigned: Ops Director", "SCHEDULED", "#38bdf8")
    ]
    for idx, (task, ass, tag, col) in enumerate(items):
        cy = y1 + 75 + idx * 85
        draw.rounded_rectangle([x1+25, cy, x2-25, cy+72], radius=8, fill="#292524", outline="#44403c", width=1)
        draw.text((x1+40, cy+14), task, fill="#ffffff", font=get_ui_font(13, True))
        draw.text((x1+40, cy+38), ass, fill="#a8a29e", font=get_ui_font(11, False))
        draw.text((x2-130, cy+26), tag, fill=col, font=get_ui_font(11, True))
    draw.rounded_rectangle([x1+25, y2-110, x2-25, y2-20], radius=10, fill="#292524", outline="#78716c", width=1)
    draw.text((x1+40, y2-95), "AUDITED LEADERS: ACCURACY & SOC2 VERIFICATION", fill="#d6d3d1", font=get_ui_font(11, True))
    draw.text((x1+40, y2-65), "• Otter.ai Business • Fireflies.ai ($10) • Fathom • tl;dv", fill="#ffffff", font=get_ui_font(12, False))


def draw_contract_clm(draw, x1, y1, x2, y2, accent):
    draw.rounded_rectangle([x1, y1, x2, y2], radius=16, fill="#0f172a", outline=accent, width=2)
    draw_header_bar(draw, x1, y1, x2, "Contract Lifecycle Intelligence & E-Sign")
    doc_y = y1 + 75
    draw.rounded_rectangle([x1+35, doc_y, x2-35, doc_y+170], radius=10, fill="#1e293b", outline="#475569", width=1)
    draw.text((x1+55, doc_y+20), "MASTER SERVICES AGREEMENT (MSA)", fill="#ffffff", font=get_ui_font(14, True))
    draw.text((x1+55, doc_y+50), "• AI Redline Clause Risk: LOW (Zero Non-Standard Indemnity)", fill="#94a3b8", font=get_ui_font(12, False))
    draw.text((x1+55, doc_y+75), "• Audit Trail: Cryptographic Timestamped Verification", fill="#94a3b8", font=get_ui_font(12, False))
    draw.rounded_rectangle([x1+55, doc_y+110, x1+220, doc_y+145], radius=6, fill="#064e3b")
    draw.text((x1+70, doc_y+120), "✓ EXECUTED & SEALED", fill="#6ee7b7", font=get_ui_font(11, True))
    draw.text((x2-180, doc_y+120), "SOC2 Type II Binding", fill="#94a3b8", font=get_ui_font(11, False))
    platforms = [
        ("Ironclad CLM", "AI Clause Extraction", "Enterprise Gold Standard", "#10b981"),
        ("PandaDoc Enterprise", "Integrated CPQ + E-Sign", "Best Mid-Market ROI", "#38bdf8"),
        ("DocuSign CLM", "Global Compliance", "Salesforce Native Workflow", "#f59e0b")
    ]
    for idx, (name, feat, tag, col) in enumerate(platforms):
        cy = y1 + 270 + idx * 75
        draw.rounded_rectangle([x1+25, cy, x2-25, cy+62], radius=8, fill="#1e293b", outline="#334155", width=1)
        draw.text((x1+40, cy+12), name, fill="#ffffff", font=get_ui_font(14, True))
        draw.text((x1+40, cy+35), feat, fill="#94a3b8", font=get_ui_font(11, False))
        draw.text((x2-180, cy+20), tag, fill=col, font=get_ui_font(12, True))


def draw_shipping_logistics(draw, x1, y1, x2, y2, accent):
    draw.rounded_rectangle([x1, y1, x2, y2], radius=16, fill="#0f172a", outline=accent, width=2)
    draw_header_bar(draw, x1, y1, x2, "Carrier Rate Shopping Engine & Discount API")
    mockup_rows = [
        ("USPS Priority Commercial", "$7.42 Base", "Discount: -44%", "#10b981"),
        ("UPS Ground Commercial", "$8.15 Base", "Discount: -68%", "#10b981"),
        ("FedEx Home Delivery", "$11.30 Base", "Standard API", "#60a5fa"),
        ("DHL Express Worldwide", "$28.50 Base", "Cross-Border", "#f59e0b")
    ]
    for idx, (carrier, price, tag, col) in enumerate(mockup_rows):
        cy = y1 + 75 + idx * 78
        draw.rounded_rectangle([x1+20, cy, x2-20, cy+62], radius=8, fill="#1e293b", outline="#334155", width=1)
        draw.text((x1+35, cy+12), carrier, fill="#f8fafc", font=get_ui_font(14, True))
        draw.text((x1+35, cy+35), "Real-time API response • 2-3 business days", fill="#64748b", font=get_ui_font(11, False))
        draw.text((x2-120, cy+12), price, fill="#ffffff", font=get_ui_font(15, True))
        draw.text((x2-130, cy+35), tag, fill=col, font=get_ui_font(11, True))
    draw.rounded_rectangle([x1+20, y2-95, x2-20, y2-20], radius=8, fill="#1e293b", outline="#334155", width=1)
    draw.text((x1+35, y2-75), "Top Evaluated: Shippo • ShipStation • EasyPost • Pirate Ship", fill="#93c5fd", font=get_ui_font(12, True))


def draw_subscription_billing(draw, x1, y1, x2, y2, accent):
    draw.rounded_rectangle([x1, y1, x2, y2], radius=16, fill="#042f2e", outline=accent, width=2)
    draw_header_bar(draw, x1, y1, x2, "Recurring Revenue & Dunning Recovery Engine")
    draw.text((x1+40, y1+80), "MONTHLY RECURRING REVENUE (MRR)", fill="#99f6e4", font=get_ui_font(11, True))
    draw.text((x1+40, y1+105), "$142,500.00", fill="#ffffff", font=get_ui_font(32, True))
    draw.rounded_rectangle([x1+280, y1+110, x1+380, y1+140], radius=6, fill="#065f46")
    draw.text((x1+295, y1+118), "+28.4% YoY", fill="#6ee7b7", font=get_ui_font(12, True))
    draw.text((x1+40, y1+165), "• Failed Payment Recovery Rate: 74% (Smart Dunning)", fill="#ccfbf1", font=get_ui_font(12, False))
    draw.text((x1+40, y1+190), "• Churn Reduction Impact: -3.8% across active subscribers", fill="#6ee7b7", font=get_ui_font(12, False))
    platforms = [
        ("Chargebee", "Multi-Currency & Tax", "Enterprise Subscription Leader", "#10b981"),
        ("Recharge Payments", "Shopify Native Leader", "One-Click Customer Portal", "#2dd4bf"),
        ("Stripe Billing", "Developer API Power", "Instant Global Settlement", "#38bdf8")
    ]
    for idx, (name, feat, tag, col) in enumerate(platforms):
        cy = y1 + 240 + idx * 75
        draw.rounded_rectangle([x1+25, cy, x2-25, cy+62], radius=8, fill="#115e59", outline="#14b8a6", width=1)
        draw.text((x1+40, cy+12), name, fill="#ffffff", font=get_ui_font(14, True))
        draw.text((x1+40, cy+35), feat, fill="#ccfbf1", font=get_ui_font(11, False))
        draw.text((x2-180, cy+20), tag, fill=col, font=get_ui_font(12, True))


def draw_cro_heatmap(draw, x1, y1, x2, y2, accent):
    draw.rounded_rectangle([x1, y1, x2, y2], radius=16, fill="#1c0b05", outline=accent, width=2)
    draw_header_bar(draw, x1, y1, x2, "CRO A/B Testing & User Heatmap Analytics")
    bx1, by1 = x1 + 40, y1 + 80
    draw.rounded_rectangle([bx1, by1, bx1+220, by1+140], radius=8, fill="#431407", outline="#ea580c", width=2)
    draw.text((bx1+20, by1+15), "VARIANT A (Original)", fill="#fed7aa", font=get_ui_font(12, True))
    draw.text((bx1+20, by1+45), "Conversion: 2.4%", fill="#ffffff", font=get_ui_font(18, True))
    draw.text((bx1+20, by1+85), "Sample: 50,000 users", fill="#fdba74", font=get_ui_font(11, False))
    bx2 = bx1 + 250
    draw.rounded_rectangle([bx2, by1, bx2+220, by1+140], radius=8, fill="#064e3b", outline="#10b981", width=2)
    draw.text((bx2+20, by1+15), "VARIANT B (Optimized)", fill="#6ee7b7", font=get_ui_font(12, True))
    draw.text((bx2+20, by1+45), "Conversion: 3.8%", fill="#ffffff", font=get_ui_font(18, True))
    draw.text((bx2+20, by1+85), "+58.3% Lift (p < 0.01)", fill="#10b981", font=get_ui_font(12, True))
    platforms = [
        ("VWO Enterprise", "Full-Stack & Server Side", "Statistically Rigorous", "#10b981"),
        ("Optimizely Web", "High-Volume Testing", "Enterprise Winner", "#fb923c"),
        ("Hotjar Business", "Session Recording & Heatmaps", "Best Qualitative Data", "#38bdf8")
    ]
    for idx, (name, feat, tag, col) in enumerate(platforms):
        cy = y1 + 250 + idx * 75
        draw.rounded_rectangle([x1+25, cy, x2-25, cy+62], radius=8, fill="#431407", outline="#7c2d12", width=1)
        draw.text((x1+40, cy+12), name, fill="#ffffff", font=get_ui_font(14, True))
        draw.text((x1+40, cy+35), feat, fill="#fed7aa", font=get_ui_font(11, False))
        draw.text((x2-170, cy+20), tag, fill=col, font=get_ui_font(12, True))


def draw_document_ai(draw, x1, y1, x2, y2, accent):
    draw.rounded_rectangle([x1, y1, x2, y2], radius=16, fill="#0f172a", outline=accent, width=2)
    draw_header_bar(draw, x1, y1, x2, "OCR & Document AI Field Extraction Matrix")
    fields = [
        ("Invoice Number", "INV-2026-9812", "100% Match", "#10b981"),
        ("Tax Amount (VAT)", "$1,842.50", "Calculated Valid", "#10b981"),
        ("Vendor Name", "Acme Cloud Infrastructure", "ERP Synced", "#38bdf8"),
        ("Line Item Table", "24 Items Extracted", "99.8% Accuracy", "#f59e0b")
    ]
    for idx, (label, val, tag, col) in enumerate(fields):
        cy = y1 + 75 + idx * 78
        draw.rounded_rectangle([x1+25, cy, x2-25, cy+64], radius=8, fill="#1e293b", outline="#334155", width=1)
        draw.text((x1+40, cy+12), label, fill="#94a3b8", font=get_ui_font(12, False))
        draw.text((x1+40, cy+34), val, fill="#ffffff", font=get_ui_font(14, True))
        draw.text((x2-150, cy+24), tag, fill=col, font=get_ui_font(12, True))
    draw.rounded_rectangle([x1+25, y2-85, x2-25, y2-20], radius=8, fill="#1e293b")
    draw.text((x1+40, y2-60), "Top Evaluated: Rossum • Hyperscience • ABBYY • Docsumo", fill="#38bdf8", font=get_ui_font(12, True))


def draw_ecommerce_generic(draw, x1, y1, x2, y2, accent):
    draw.rounded_rectangle([x1, y1, x2, y2], radius=16, fill="#1a1024", outline=accent, width=2)
    draw_header_bar(draw, x1, y1, x2, "E-Commerce Optimization & Multi-Channel Sync")
    metrics = [
        ("Average Order Value (AOV)", "$118.40", "+32% Post-Purchase Lift", "#10b981"),
        ("Customer Retention Rate", "48.2%", "Loyalty & Points Program", "#c084fc"),
        ("Catalog Sync Latency", "< 30 sec", "Shopify • Amazon • TikTok", "#38bdf8"),
        ("Cart Abandonment Recovery", "18.5%", "Automated SMS & Email", "#f59e0b")
    ]
    for idx, (label, val, tag, col) in enumerate(metrics):
        cy = y1 + 75 + idx * 78
        draw.rounded_rectangle([x1+25, cy, x2-25, cy+64], radius=8, fill="#2e1b40", outline="#4c2866", width=1)
        draw.text((x1+40, cy+12), label, fill="#d8b4fe", font=get_ui_font(12, False))
        draw.text((x1+40, cy+34), val, fill="#ffffff", font=get_ui_font(15, True))
        draw.text((x2-190, cy+24), tag, fill=col, font=get_ui_font(12, True))
    draw.rounded_rectangle([x1+25, y2-85, x2-25, y2-20], radius=8, fill="#2e1b40")
    draw.text((x1+40, y2-60), "Audited Platforms: Yotpo • Smile.io • Rebuy • Salsify", fill="#e9d5ff", font=get_ui_font(12, True))


# ==============================================================================
# THEME ROUTING ENGINE
# ==============================================================================

CATEGORY_CONFIGS = [
    {
        "keywords": ["prospecting", "zoominfo", "apollo", "lead", "sales"],
        "category_badge": "B2B SALES & PROSPECTING",
        "bg_color": "#090918",
        "accent": "#818cf8",
        "badge_bg": "#312e81",
        "drawer": draw_sales_intelligence
    },
    {
        "keywords": ["cold email", "outreach", "deliverability", "smtp", "inbox"],
        "category_badge": "OUTBOUND & COLD EMAIL",
        "bg_color": "#022c22",
        "accent": "#34d399",
        "badge_bg": "#064e3b",
        "drawer": draw_email_deliverability
    },
    {
        "keywords": ["coding", "copilot", "cursor", "developer", "code", "dev"],
        "category_badge": "DEVELOPER & AI CODING",
        "bg_color": "#030712",
        "accent": "#38bdf8",
        "badge_bg": "#082f49",
        "drawer": draw_code_editor
    },
    {
        "keywords": ["automation", "zapier", "make", "n8n", "workflow"],
        "category_badge": "WORKFLOW AUTOMATION",
        "bg_color": "#180629",
        "accent": "#c084fc",
        "badge_bg": "#581c87",
        "drawer": draw_workflow_nodes
    },
    {
        "keywords": ["video", "avatar", "demo", "synthesia", "heygen"],
        "category_badge": "AI VIDEO GENERATION",
        "bg_color": "#1c0b05",
        "accent": "#fb923c",
        "badge_bg": "#7c2d12",
        "drawer": draw_video_studio
    },
    {
        "keywords": ["voice", "speech", "tts", "elevenlabs", "audio"],
        "category_badge": "AI VOICE & SPEECH",
        "bg_color": "#230619",
        "accent": "#f43f5e",
        "badge_bg": "#881337",
        "drawer": draw_voice_audio
    },
    {
        "keywords": ["chatbot", "support", "intercom", "gorgias", "customer support"],
        "category_badge": "AI CUSTOMER SUPPORT",
        "bg_color": "#082f49",
        "accent": "#38bdf8",
        "badge_bg": "#0369a1",
        "drawer": draw_customer_support
    },
    {
        "keywords": ["meeting", "note", "transcription", "otter", "fireflies"],
        "category_badge": "AI MEETING ASSISTANTS",
        "bg_color": "#1c1917",
        "accent": "#a8a29e",
        "badge_bg": "#44403c",
        "drawer": draw_meeting_notes
    },
    {
        "keywords": ["contract", "clm", "agreement", "ironclad", "pandadoc", "legal"],
        "category_badge": "CONTRACT LIFECYCLE (CLM)",
        "bg_color": "#0b1329",
        "accent": "#38bdf8",
        "badge_bg": "#1e3a8a",
        "drawer": draw_contract_clm
    },
    {
        "keywords": ["shipping", "fulfillment", "carrier", "shippo", "shipstation"],
        "category_badge": "E-COMMERCE & SHIPPING",
        "bg_color": "#0f172a",
        "accent": "#60a5fa",
        "badge_bg": "#1e3a8a",
        "drawer": draw_shipping_logistics
    },
    {
        "keywords": ["subscription", "recurring", "billing", "chargebee", "recharge"],
        "category_badge": "SUBSCRIPTION & BILLING",
        "bg_color": "#042f2e",
        "accent": "#2dd4bf",
        "badge_bg": "#115e59",
        "drawer": draw_subscription_billing
    },
    {
        "keywords": ["cro", "a/b test", "testing", "conversion", "optimizely", "vwo"],
        "category_badge": "E-COMMERCE CRO & TESTING",
        "bg_color": "#1c0b05",
        "accent": "#ea580c",
        "badge_bg": "#7c2d12",
        "drawer": draw_cro_heatmap
    },
    {
        "keywords": ["document", "ocr", "extraction", "rossum", "hyperscience"],
        "category_badge": "AI DOCUMENT PROCESSING",
        "bg_color": "#0f172a",
        "accent": "#38bdf8",
        "badge_bg": "#1e293b",
        "drawer": draw_document_ai
    }
]


def resolve_config(title: str, category: str):
    search_str = f"{title} {category}".lower()
    for cfg in CATEGORY_CONFIGS:
        if any(k in search_str for k in cfg["keywords"]):
            return cfg
    # Default fallback
    return {
        "category_badge": category.upper() if category else "B2B SAAS GUIDE",
        "bg_color": "#120e24",
        "accent": "#a855f7",
        "badge_bg": "#4c1d95",
        "drawer": draw_ecommerce_generic
    }


def generate_stackpilot_ui_banner(title: str, category: str = "B2B SaaS Guide") -> bytes:
    '''
    Generates a native, ultra-clean StackPilot B2B Editorial Dashboard Banner (1200x675).
    Completely watermark-free, razor-sharp typography, dynamic topic-tailored visuals.
    '''
    cfg = resolve_config(title, category)
    w, h = 1200, 675
    img = Image.new("RGB", (w, h), color=cfg["bg_color"])
    draw = ImageDraw.Draw(img)

    # Subtle background pattern / grid
    grid_col = tuple(min(255, c + 14) for c in Image.new("RGB", (1, 1), cfg["bg_color"]).getpixel((0, 0)))
    for x in range(0, w, 40):
        draw.line([(x, 0), (x, h)], fill=grid_col, width=1)
    for y in range(0, h, 40):
        draw.line([(0, y), (w, y)], fill=grid_col, width=1)

    # Top Brand Bar
    draw.rounded_rectangle([70, 48, 310, 86], radius=6, fill="#0f172a", outline="#334155", width=1)
    draw.text((88, 58), "STACKPILOT AUDIT", fill="#94a3b8", font=get_ui_font(13, True))
    
    draw.rounded_rectangle([325, 48, 455, 86], radius=6, fill="#064e3b", outline="#10b981", width=1)
    draw.text((342, 58), "2026 GUIDE", fill="#6ee7b7", font=get_ui_font(13, True))

    # Category Pill Badge (Vibrant Category Color)
    badge_text = f" {cfg['category_badge']} "
    bbox_b = draw.textbbox((0, 0), badge_text, font=get_ui_font(13, True))
    bw = bbox_b[2] - bbox_b[0] + 20
    draw.rounded_rectangle([70, 105, 70 + bw, 142], radius=6, fill=cfg["badge_bg"], outline=cfg["accent"], width=2)
    draw.text((80, 114), badge_text, fill=cfg["accent"], font=get_ui_font(13, True))

    # Left Headline - Intelligent Multi-Line Word Wrapping (No cut words)
    font_title = get_ui_font(32, True)
    words = title.split()
    lines = []
    curr = []
    for w_word in words:
        test_line = " ".join(curr + [w_word])
        if len(test_line) <= 22:
            curr.append(w_word)
        else:
            if curr:
                lines.append(" ".join(curr))
            curr = [w_word]
    if curr:
        lines.append(" ".join(curr))

    line1 = lines[0] if len(lines) > 0 else title
    line2 = lines[1] if len(lines) > 1 else ""
    line3 = lines[2] if len(lines) > 2 else ""

    draw.text((70, 165), line1, fill="#ffffff", font=font_title)
    if line2:
        draw.text((70, 212), line2, fill=cfg["accent"], font=font_title)
    if line3:
        draw.text((70, 258), line3, fill="#cbd5e1", font=font_title)

    # Trust Subtitle
    sub_y = 315 if line3 else 275
    draw.text((70, sub_y), "• 5-7 Platforms Tested in Real Production", fill="#e2e8f0", font=get_ui_font(13, True))
    draw.text((70, sub_y+25), "• Independent Performance & API Benchmark", fill="#94a3b8", font=get_ui_font(12, False))
    draw.text((70, sub_y+48), "• Transparent Pricing & Compliance Scorecard", fill="#94a3b8", font=get_ui_font(12, False))

    # Bottom badge
    draw.rounded_rectangle([70, 580, 360, 620], radius=8, fill="#1e293b", outline="#334155", width=1)
    draw.text((85, 592), "VERIFIED BY STACKPILOT LABS", fill="#38bdf8", font=get_ui_font(12, True))

    # Right Side: Call the custom visual drawer
    card_x1, card_y1, card_x2, card_y2 = 540, 50, 1135, 620
    cfg["drawer"](draw, card_x1, card_y1, card_x2, card_y2, cfg["accent"])

    out = io.BytesIO()
    img.save(out, format="JPEG", quality=95)
    return out.getvalue()


def fetch_saas_image_bytes(image_prompt_en: str, title: str = "", category: str = "E-Commerce & Retail Tech") -> bytes:
    '''
    Generate and download modern topic-tailored B2B SaaS editorial banner bytes.
    GUARANTEES 100% WATERMARK-FREE output and visually distinct graphics.
    '''
    print(f"[StackPilot Banner] Generating custom UI dashboard banner for: '{title}'...")
    banner_bytes = generate_stackpilot_ui_banner(title or image_prompt_en, category)
    if banner_bytes and len(banner_bytes) > 20000:
        print(f"[OK] StackPilot native editorial banner generated ({len(banner_bytes)} bytes, 100% watermark-free)")
        return banner_bytes
    return None
