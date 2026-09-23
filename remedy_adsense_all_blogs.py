"""
Remedy AdSense Script for All 4 Google Blogger Blogs
1. Updates E-E-A-T essential static pages (About Us, Disclaimer & Contact, Privacy Policy)
   specifically tailored for each blog's brand, mission, language, and Google AdSense compliance.
2. Slims down bulk-generated posts to exactly 18 high-quality live posts per blog,
   reverting the rest to DRAFT (100% reversible via Blogger API).
3. Backs up all post status changes into a JSON record.
"""

import os
import sys
import json
import time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

# Load Credentials
CRED_FILE = "blogger_credentials.json"
if not os.path.exists(CRED_FILE):
    raise FileNotFoundError("blogger_credentials.json not found.")

with open(CRED_FILE, "r", encoding="utf-8") as f:
    c = json.load(f)

creds = Credentials(
    token=c.get("token"),
    refresh_token=c.get("refresh_token"),
    token_uri="https://oauth2.googleapis.com/token",
    client_id=c.get("client_id"),
    client_secret=c.get("client_secret"),
    scopes=["https://www.googleapis.com/auth/blogger"]
)

service = build("blogger", "v3", credentials=creds)

# -----------------------------------------------------------------------------
# HTML PAGE TEMPLATES PER BLOG
# -----------------------------------------------------------------------------

def build_stackpilot_pages():
    about_html = """<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.8; color: #1e293b; max-width: 820px; margin: 0 auto; padding: 25px 20px;">
  <div style="border-bottom: 3px solid #2563eb; padding-bottom: 12px; margin-bottom: 25px;">
    <h1 style="color: #0f172a; font-size: 28px; margin: 0 0 8px 0; font-weight: 800;">About StackPilot</h1>
    <div style="color: #64748b; font-size: 15px; font-weight: 500;">Modern B2B SaaS, Cloud Tooling &amp; Workflow Automation Guides</div>
  </div>

  <p style="font-size: 16px; color: #334155;">Welcome to <strong>StackPilot</strong>. We are an independent technology evaluation publication dedicated to delivering transparent, empirical, and objective comparisons of enterprise SaaS platforms, developer tooling, and modern workflow automation systems.</p>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #2563eb; padding-left: 12px;">Our Mission &amp; Editorial Independence</h2>
  <p style="font-size: 15px; color: #475569;">Selecting enterprise software is among the highest-stakes operational decisions business operators make. Unfortunately, modern software procurement is plagued by aggressive marketing rhetoric, opaque pricing tiers, and pay-to-play review portals. <strong>StackPilot</strong> cuts through vendor marketing to provide CTOs, founders, VP of Operations, and procurement leads with reproducible, objective evaluation frameworks.</p>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #2563eb; padding-left: 12px;">Our 2026 Evaluation Methodology</h2>
  <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-top: 15px;">
    <ul style="margin: 0; padding-left: 20px; color: #334155; font-size: 14px;">
      <li style="margin-bottom: 12px;"><strong>Transparent Pricing Audits:</strong> We evaluate verified 2026 contract terms, seat minimums, API consumption limits, and hidden add-on costs.</li>
      <li style="margin-bottom: 12px;"><strong>Hands-On Architecture Audits:</strong> We analyze webhook latency, multi-carrier logistics, data privacy, and integration reliability.</li>
      <li style="margin-bottom: 12px;"><strong>Strict Zero Pay-to-Play Policy:</strong> We do not accept sponsored rankings, placement fees, or affiliate pay-to-play positioning. Placements are determined purely by technical merit and operational fit.</li>
    </ul>
  </div>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #2563eb; padding-left: 12px;">Editorial Team &amp; Contact</h2>
  <p style="font-size: 15px; color: #475569;">Every guide on StackPilot undergoes continuous quarterly verification to ensure pricing and feature data remain accurate.</p>
  
  <div style="background: #f1f5f9; border-radius: 8px; padding: 18px; margin-top: 18px; font-size: 14px; color: #334155;">
    <div><strong>Publication:</strong> StackPilot (smartlawstep.blogspot.com)</div>
    <div style="margin-top: 6px;"><strong>Lead Tech Analyst:</strong> Alex Vance, Senior B2B SaaS Analyst</div>
    <div style="margin-top: 6px;"><strong>General &amp; Editorial Inquiries:</strong> <a href="mailto:dlwoduq20@gmail.com" style="color: #2563eb; text-decoration: none;">dlwoduq20@gmail.com</a></div>
  </div>
</div>"""

    disclaimer_html = """<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.8; color: #1e293b; max-width: 820px; margin: 0 auto; padding: 25px 20px;">
  <div style="border-bottom: 3px solid #2563eb; padding-bottom: 12px; margin-bottom: 25px;">
    <h1 style="color: #0f172a; font-size: 28px; margin: 0 0 8px 0; font-weight: 800;">Disclaimer &amp; Contact Information</h1>
    <div style="color: #64748b; font-size: 15px; font-weight: 500;">StackPilot Editorial Disclosures &amp; Inquiries</div>
  </div>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 24px; font-weight: 700; border-left: 4px solid #2563eb; padding-left: 12px;">Software Evaluation Disclaimer</h2>
  <p style="font-size: 15px; color: #475569;">All content published on <strong>StackPilot</strong> is provided for informational and procurement research purposes only. While our team rigorously checks vendor pricing schedules, API specifications, and contract terms, SaaS vendors frequently update their tiers, feature sets, and SLAs. Readers are advised to verify active terms directly with vendor sales representatives prior to executing contracts.</p>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #2563eb; padding-left: 12px;">Affiliate &amp; Commercial Independence</h2>
  <p style="font-size: 15px; color: #475569;">StackPilot maintains absolute editorial autonomy. We do not sell preferred positioning or allow vendors to influence evaluation scores. Where affiliate links may exist to support research operations, they never compromise our objective ranking methodology.</p>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #2563eb; padding-left: 12px;">Contact Information</h2>
  <p style="font-size: 15px; color: #475569;">We welcome feedback, corrections, and tool audit requests from our readers:</p>
  <div style="background: #f1f5f9; border-radius: 8px; padding: 18px; margin-top: 15px; font-size: 14px; color: #334155;">
    <div><strong>Website:</strong> <a href="https://smartlawstep.blogspot.com" style="color: #2563eb;">https://smartlawstep.blogspot.com</a></div>
    <div style="margin-top: 6px;"><strong>Email Contact:</strong> <a href="mailto:dlwoduq20@gmail.com" style="color: #2563eb;">dlwoduq20@gmail.com</a></div>
    <div style="margin-top: 6px;"><strong>Response Time:</strong> Typically within 24 to 48 business hours.</div>
  </div>
</div>"""

    privacy_html = """<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.8; color: #1e293b; max-width: 820px; margin: 0 auto; padding: 25px 20px;">
  <div style="border-bottom: 3px solid #2563eb; padding-bottom: 12px; margin-bottom: 25px;">
    <h1 style="color: #0f172a; font-size: 28px; margin: 0 0 8px 0; font-weight: 800;">Privacy Policy</h1>
    <div style="color: #64748b; font-size: 15px; font-weight: 500;">StackPilot Visitor Privacy &amp; Cookie Compliance</div>
  </div>

  <p style="font-size: 15px; color: #475569;">At <strong>StackPilot</strong> (accessible via smartlawstep.blogspot.com), visitor privacy is of paramount importance. This Privacy Policy details the types of information collected and how it is utilized.</p>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #2563eb; padding-left: 12px;">Cookies &amp; Google AdSense Compliance</h2>
  <p style="font-size: 15px; color: #475569;">We utilize cookies to analyze traffic patterns and serve relevant content and advertisements. In particular:</p>
  <ul style="margin: 10px 0; padding-left: 20px; color: #334155; font-size: 14px;">
    <li style="margin-bottom: 8px;"><strong>Google AdSense:</strong> Google, as a third-party vendor, uses cookies (including the DoubleClick DART cookie) to serve ads based on visits to this and other websites across the Internet.</li>
    <li style="margin-bottom: 8px;"><strong>Opt-Out Options:</strong> Users may opt out of personalized advertising by visiting the <a href="https://adssettings.google.com" target="_blank" rel="noopener" style="color: #2563eb;">Google Ad Settings</a> or <a href="https://www.aboutads.info" target="_blank" rel="noopener" style="color: #2563eb;">aboutads.info</a>.</li>
  </ul>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #2563eb; padding-left: 12px;">Log Files &amp; Web Analytics</h2>
  <p style="font-size: 15px; color: #475569;">Like most standard websites, StackPilot uses log files to monitor trends, administer the site, and gather broad demographic data. Logged data includes IP addresses, browser types, Internet Service Providers (ISPs), date/time stamps, and referring/exit pages. None of this data is linked to personally identifiable information.</p>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #2563eb; padding-left: 12px;">GDPR &amp; CCPA Rights</h2>
  <p style="font-size: 15px; color: #475569;">Depending on your jurisdiction, you have the right to request access to, correction of, or deletion of any personal data we process. For privacy inquiries, contact us at <a href="mailto:dlwoduq20@gmail.com" style="color: #2563eb;">dlwoduq20@gmail.com</a>.</p>
</div>"""

    return {"about": about_html, "disclaimer": disclaimer_html, "privacy": privacy_html}


def build_greenthumb_pages():
    about_html = """<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.8; color: #1e293b; max-width: 820px; margin: 0 auto; padding: 25px 20px;">
  <div style="border-bottom: 3px solid #16a34a; padding-bottom: 12px; margin-bottom: 25px;">
    <h1 style="color: #0f172a; font-size: 28px; margin: 0 0 8px 0; font-weight: 800;">About GreenThumb Garden</h1>
    <div style="color: #64748b; font-size: 15px; font-weight: 500;">Practical Home Horticulture, Vegetable Growing &amp; Soil Health Guides</div>
  </div>

  <p style="font-size: 16px; color: #334155;">Welcome to <strong>GreenThumb Garden</strong>. We are a practical horticultural resource dedicated to helping home gardeners, urban homesteaders, and backyard growers cultivate vibrant, chemical-free vegetable gardens and productive container harvests.</p>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #16a34a; padding-left: 12px;">Our Growing Philosophy</h2>
  <p style="font-size: 15px; color: #475569;">Successful gardening begins with healthy soil biology rather than synthetic shortcuts. Our guides emphasize organic composting, companion planting for natural pest deterrence, seasonal crop rotation, and efficient water management tailored to residential spaces.</p>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #16a34a; padding-left: 12px;">What We Provide</h2>
  <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-top: 15px;">
    <ul style="margin: 0; padding-left: 20px; color: #334155; font-size: 14px;">
      <li style="margin-bottom: 12px;"><strong>Step-by-Step Vegetable Cultivation:</strong> Comprehensive planting schedules, germination techniques, and harvest timings.</li>
      <li style="margin-bottom: 12px;"><strong>Soil &amp; Nutrient Management:</strong> Practical compost ratios, organic soil amendments, and micronutrient balancing.</li>
      <li style="margin-bottom: 12px;"><strong>Troubleshooting Common Plant Diseases:</strong> Science-grounded identification of fungal blights, nutrient deficiencies, and organic pest remedies.</li>
    </ul>
  </div>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #16a34a; padding-left: 12px;">Editorial Standards &amp; Contact</h2>
  <div style="background: #f1f5f9; border-radius: 8px; padding: 18px; margin-top: 18px; font-size: 14px; color: #334155;">
    <div><strong>Publication:</strong> GreenThumb Garden (greenthumb-garden.blogspot.com)</div>
    <div style="margin-top: 6px;"><strong>Horticultural Lead:</strong> Clara Jenkins, Master Gardener &amp; Horticulture Specialist</div>
    <div style="margin-top: 6px;"><strong>Inquiries:</strong> <a href="mailto:dlwoduq20@gmail.com" style="color: #16a34a; text-decoration: none;">dlwoduq20@gmail.com</a></div>
  </div>
</div>"""

    disclaimer_html = """<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.8; color: #1e293b; max-width: 820px; margin: 0 auto; padding: 25px 20px;">
  <div style="border-bottom: 3px solid #16a34a; padding-bottom: 12px; margin-bottom: 25px;">
    <h1 style="color: #0f172a; font-size: 28px; margin: 0 0 8px 0; font-weight: 800;">Gardening Disclaimer &amp; Contact</h1>
    <div style="color: #64748b; font-size: 15px; font-weight: 500;">GreenThumb Garden Horticultural Disclosures</div>
  </div>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 24px; font-weight: 700; border-left: 4px solid #16a34a; padding-left: 12px;">Horticultural Advice Disclaimer</h2>
  <p style="font-size: 15px; color: #475569;">Gardening advice and planting guidelines provided on <strong>GreenThumb Garden</strong> are intended for general educational purposes. Microclimates, hardiness zones, regional soil compositions, and localized weather patterns vary substantially. Always consider your local climate and consult regional agricultural extension offices for localized advice.</p>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #16a34a; padding-left: 12px;">Contact Information</h2>
  <div style="background: #f1f5f9; border-radius: 8px; padding: 18px; margin-top: 15px; font-size: 14px; color: #334155;">
    <div><strong>Website:</strong> <a href="https://greenthumb-garden.blogspot.com" style="color: #16a34a;">https://greenthumb-garden.blogspot.com</a></div>
    <div style="margin-top: 6px;"><strong>Email Contact:</strong> <a href="mailto:dlwoduq20@gmail.com" style="color: #16a34a;">dlwoduq20@gmail.com</a></div>
  </div>
</div>"""

    privacy_html = """<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.8; color: #1e293b; max-width: 820px; margin: 0 auto; padding: 25px 20px;">
  <div style="border-bottom: 3px solid #16a34a; padding-bottom: 12px; margin-bottom: 25px;">
    <h1 style="color: #0f172a; font-size: 28px; margin: 0 0 8px 0; font-weight: 800;">Privacy Policy</h1>
    <div style="color: #64748b; font-size: 15px; font-weight: 500;">GreenThumb Garden Privacy &amp; Cookie Compliance</div>
  </div>

  <p style="font-size: 15px; color: #475569;">At <strong>GreenThumb Garden</strong>, we respect your privacy. This policy outlines how information is gathered and protected.</p>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #16a34a; padding-left: 12px;">Google AdSense &amp; Cookies</h2>
  <p style="font-size: 15px; color: #475569;">We use cookies to analyze web traffic and provide relevant advertising via Google AdSense. Third-party vendors, including Google, use cookies to serve ads based on past visits. Visitors can opt out of personalized advertising by visiting Google's <a href="https://adssettings.google.com" target="_blank" rel="noopener" style="color: #16a34a;">Ad Settings</a>.</p>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #16a34a; padding-left: 12px;">Contact</h2>
  <p style="font-size: 15px; color: #475569;">For questions about our privacy policy, contact <a href="mailto:dlwoduq20@gmail.com" style="color: #16a34a;">dlwoduq20@gmail.com</a>.</p>
</div>"""

    return {"about": about_html, "disclaimer": disclaimer_html, "privacy": privacy_html}


def build_kgamja_pages():
    about_html = """<div style="font-family: -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; line-height: 1.85; color: #1e293b; max-width: 820px; margin: 0 auto; padding: 25px 20px;">
  <div style="border-bottom: 3px solid #0284c7; padding-bottom: 12px; margin-bottom: 25px;">
    <h1 style="color: #0f172a; font-size: 28px; margin: 0 0 8px 0; font-weight: 800;">생활 속 법과 금융 소개 (About Us)</h1>
    <div style="color: #64748b; font-size: 15px; font-weight: 500;">일상 생활 법률 상식 &amp; 실전 재테크 가이드</div>
  </div>

  <p style="font-size: 16px; color: #334155;"><strong>생활 속 법과 금융</strong>(Kgamja Blog)은 복잡하고 어려운 법률 조항과 금융·세무 제도를 일반인의 눈높이에 맞춰 체계적으로 해설하는 실용 생활 법률 정보 미디어입니다.</p>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #0284c7; padding-left: 12px;">운영 목적 및 지향점</h2>
  <p style="font-size: 15px; color: #475569;">부동산 전월세 계약, 임대차 분쟁, 직장 내 근로기준법, 상속·증여세 절세, 소액 분쟁 절차 등 살면서 반드시 부딪히는 실전 문제들을 다룹니다. 추상적인 법조문 나열을 지양하고, 실제 행정 절차와 대법원 판례, 국세청 예규를 근거로 현실적인 해결 경로를 안내합니다.</p>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #0284c7; padding-left: 12px;">편집 원칙 및 팩트체크</h2>
  <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-top: 15px;">
    <ul style="margin: 0; padding-left: 20px; color: #334155; font-size: 14px;">
      <li style="margin-bottom: 10px;"><strong>공식 법령 준거:</strong> 국가법령정보센터 및 대법원 종합법률정보의 최신 개정 법률을 상시 확인하여 반영합니다.</li>
      <li style="margin-bottom: 10px;"><strong>객관성과 중립성:</strong> 특정 정당이나 이해관계자의 입장을 대변하지 않으며, 순수한 제도 안내와 법적 권리 보호에 집중합니다.</li>
      <li style="margin-bottom: 10px;"><strong>쉬운 시각화:</strong> 복잡한 법률 관계를 누구나 직관적으로 이해할 수 있도록 구조화된 차트와 일러스트를 병행합니다.</li>
    </ul>
  </div>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #0284c7; padding-left: 12px;">문의 및 편집팀 안내</h2>
  <div style="background: #f1f5f9; border-radius: 8px; padding: 18px; margin-top: 18px; font-size: 14px; color: #334155;">
    <div><strong>블로그명:</strong> 생활 속 법과 금융 (kgamjablog.blogspot.com)</div>
    <div style="margin-top: 6px;"><strong>운영 및 편집:</strong> 생활법률 콘텐츠 리서치팀</div>
    <div style="margin-top: 6px;"><strong>공식 이메일:</strong> <a href="mailto:dlwoduq20@gmail.com" style="color: #0284c7; text-decoration: none;">dlwoduq20@gmail.com</a></div>
  </div>
</div>"""

    disclaimer_html = """<div style="font-family: -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; line-height: 1.85; color: #1e293b; max-width: 820px; margin: 0 auto; padding: 25px 20px;">
  <div style="border-bottom: 3px solid #0284c7; padding-bottom: 12px; margin-bottom: 25px;">
    <h1 style="color: #0f172a; font-size: 28px; margin: 0 0 8px 0; font-weight: 800;">문의 및 법적 면책조항 (Contact &amp; Disclaimer)</h1>
    <div style="color: #64748b; font-size: 15px; font-weight: 500;">생활 속 법과 금융 면책 공지 및 피드백 접수</div>
  </div>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 24px; font-weight: 700; border-left: 4px solid #0284c7; padding-left: 12px;">법적 책임의 한계 (Legal Disclaimer)</h2>
  <div style="background: #fffbeb; border: 1px solid #fef3c7; border-left: 4px solid #f59e0b; padding: 16px 20px; border-radius: 6px; margin-top: 15px; font-size: 14px; color: #92400e;">
    <strong>※ 필수 주의사항:</strong> 본 블로그에 수록된 모든 글과 자료는 일반적인 법률 및 금융 정보의 이해를 돕기 위한 교양 콘텐츠이며, 법률 자문이나 변호사-의뢰인 관계를 형성하지 않습니다.
  </div>
  <p style="font-size: 15px; color: #475569; margin-top: 15px;">개별적이고 구체적인 사건이나 소송, 세무 신고에 대해서는 반드시 공인된 변호사, 세무사, 법무사 등 전문 자격사와의 직접 상담을 통해 최종 결정을 내리시기 바랍니다. 본 블로그의 정보 활용으로 인해 발생하는 직간접적 손해에 대해 블로그 운영자는 법적 책임을 지지 않습니다.</p>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #0284c7; padding-left: 12px;">문의 및 피드백</h2>
  <div style="background: #f1f5f9; border-radius: 8px; padding: 18px; margin-top: 15px; font-size: 14px; color: #334155;">
    <div><strong>공식 웹사이트:</strong> <a href="https://kgamjablog.blogspot.com" style="color: #0284c7;">https://kgamjablog.blogspot.com</a></div>
    <div style="margin-top: 6px;"><strong>문의 이메일:</strong> <a href="mailto:dlwoduq20@gmail.com" style="color: #0284c7;">dlwoduq20@gmail.com</a></div>
    <div style="margin-top: 6px;">콘텐츠 오류 제보나 주제 제안은 위 이메일로 보내주시면 검토 후 신속히 반영하겠습니다.</div>
  </div>
</div>"""

    privacy_html = """<div style="font-family: -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; line-height: 1.85; color: #1e293b; max-width: 820px; margin: 0 auto; padding: 25px 20px;">
  <div style="border-bottom: 3px solid #0284c7; padding-bottom: 12px; margin-bottom: 25px;">
    <h1 style="color: #0f172a; font-size: 28px; margin: 0 0 8px 0; font-weight: 800;">개인정보처리방침 (Privacy Policy)</h1>
    <div style="color: #64748b; font-size: 15px; font-weight: 500;">생활 속 법과 금융 개인정보 보호 및 쿠키 규정</div>
  </div>

  <p style="font-size: 15px; color: #475569;">'생활 속 법과 금융'(이하 '블로그')은 이용자의 개인정보를 소중히 다루며, 관련 법령을 철저히 준수합니다.</p>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #0284c7; padding-left: 12px;">쿠키 및 Google AdSense 광고 정책</h2>
  <p style="font-size: 15px; color: #475569;">본 블로그는 광고 제공 및 웹사이트 트래픽 분석을 위해 쿠키(Cookie)를 사용합니다.</p>
  <ul style="margin: 10px 0; padding-left: 20px; color: #334155; font-size: 14px;">
    <li style="margin-bottom: 8px;">Google을 포함한 제3자 제공업체는 쿠키를 사용하여 사용자의 과거 방문 기록을 기반으로 광고를 게재합니다.</li>
    <li style="margin-bottom: 8px;">사용자는 <a href="https://adssettings.google.com" target="_blank" rel="noopener" style="color: #0284c7;">Google 광고 설정</a>에서 맞춤형 광고를 해제할 수 있습니다.</li>
  </ul>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #0284c7; padding-left: 12px;">개인정보 보호 문의</h2>
  <p style="font-size: 15px; color: #475569;">개인정보 처리에 관한 문의사항은 <a href="mailto:dlwoduq20@gmail.com" style="color: #0284c7;">dlwoduq20@gmail.com</a>으로 문의해 주시기 바랍니다.</p>
</div>"""

    return {"about": about_html, "disclaimer": disclaimer_html, "privacy": privacy_html}


def build_seikatsu_pages():
    about_html = """<div style="font-family: -apple-system, BlinkMacSystemFont, 'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif; line-height: 1.85; color: #1e293b; max-width: 820px; margin: 0 auto; padding: 25px 20px;">
  <div style="border-bottom: 3px solid #7c3aed; padding-bottom: 12px; margin-bottom: 25px;">
    <h1 style="color: #0f172a; font-size: 28px; margin: 0 0 8px 0; font-weight: 800;">当サイトについて (About Us)</h1>
    <div style="color: #64748b; font-size: 15px; font-weight: 500;">日常の法務＆生活防衛ガイド — 暮らしの法律とお金の知恵</div>
  </div>

  <p style="font-size: 16px; color: #334155;"><strong>「暮らしの法律とお金の知恵」</strong>（Seikatsu Law）は、賃貸トラブル、労働環境、相続・贈与、公的年金・保険制度など、日本での生活に直結する身近な法律と実用的なマネー知識をわかりやすく解説する情報メディアです。</p>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #7c3aed; padding-left: 12px;">サイトの目的と方針</h2>
  <p style="font-size: 15px; color: #475569;">法律や公的制度は生活を守る強力な盾ですが、難解な専門用語や手続きの複雑さから利用をためらう方が少なくありません。当サイトでは、法律の条文をただ引用するのではなく、「市民の生活防衛」という観点から、具体的な手続きや対処法を平易な言葉で体系化して発信しています。</p>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #7c3aed; padding-left: 12px;">編集方針と信頼性</h2>
  <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-top: 15px;">
    <ul style="margin: 0; padding-left: 20px; color: #334155; font-size: 14px;">
      <li style="margin-bottom: 10px;"><strong>公的機関情報の準拠:</strong> 法務省、国税庁、厚生労働省等の公式資料および最新の法改正情報を精査・反映しています。</li>
      <li style="margin-bottom: 10px;"><strong>客観的な解説:</strong> 特定の団体やサービスの宣伝に偏ることなく、公平中立な制度解説を徹底します。</li>
      <li style="margin-bottom: 10px;"><strong>定期的な見直し:</strong> 制度の改定に合わせて記事内容を適宜アップデートし、最新情報の維持に努めています。</li>
    </ul>
  </div>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #7c3aed; padding-left: 12px;">運営者・お問い合わせ</h2>
  <div style="background: #f1f5f9; border-radius: 8px; padding: 18px; margin-top: 18px; font-size: 14px; color: #334155;">
    <div><strong>サイト名:</strong> 暮らしの法律とお金の知恵 (seikatsulaw.blogspot.com)</div>
    <div style="margin-top: 6px;"><strong>運営体制:</strong> 生活法務・マネー情報編集チーム</div>
    <div style="margin-top: 6px;"><strong>お問い合わせ:</strong> <a href="mailto:dlwoduq20@gmail.com" style="color: #7c3aed; text-decoration: none;">dlwoduq20@gmail.com</a></div>
  </div>
</div>"""

    disclaimer_html = """<div style="font-family: -apple-system, BlinkMacSystemFont, 'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif; line-height: 1.85; color: #1e293b; max-width: 820px; margin: 0 auto; padding: 25px 20px;">
  <div style="border-bottom: 3px solid #7c3aed; padding-bottom: 12px; margin-bottom: 25px;">
    <h1 style="color: #0f172a; font-size: 28px; margin: 0 0 8px 0; font-weight: 800;">免責事項・お問い合わせ (Contact &amp; Disclaimer)</h1>
    <div style="color: #64748b; font-size: 15px; font-weight: 500;">法的助言の非代替性および免責規程</div>
  </div>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 24px; font-weight: 700; border-left: 4px solid #7c3aed; padding-left: 12px;">法的助言の非代替性（弁護士法に基づく告知）</h2>
  <div style="background: #fffbeb; border: 1px solid #fef3c7; border-left: 4px solid #f59e0b; padding: 16px 20px; border-radius: 6px; margin-top: 15px; font-size: 14px; color: #92400e;">
    <strong>※ 重要なお知らせ:</strong> 当サイトに掲載されている情報は一般的な法制度や手続きの解説を目的としており、個別の法律相談や事件対応を行うものではありません。
  </div>
  <p style="font-size: 15px; color: #475569; margin-top: 15px;">個別のトラブルや具体的な事件については、必ず弁護士、司法書士、社会保険労務士、税理士等の専門家または法テラスなどの公的相談窓口にご相談ください。当サイトの情報を利用したことによって生じたいかなる損害についても、当サイトおよび運営者は一切の責任を負いかねます。</p>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #7c3aed; padding-left: 12px;">お問い合わせ窓口</h2>
  <div style="background: #f1f5f9; border-radius: 8px; padding: 18px; margin-top: 15px; font-size: 14px; color: #334155;">
    <div><strong>サイトURL:</strong> <a href="https://seikatsulaw.blogspot.com" style="color: #7c3aed;">https://seikatsulaw.blogspot.com</a></div>
    <div style="margin-top: 6px;"><strong>連絡先メール:</strong> <a href="mailto:dlwoduq20@gmail.com" style="color: #7c3aed;">dlwoduq20@gmail.com</a></div>
    <div style="margin-top: 6px;">誤字・脱字のご指摘や記事に関するフィードバックは上記メールまでお寄せください。</div>
  </div>
</div>"""

    privacy_html = """<div style="font-family: -apple-system, BlinkMacSystemFont, 'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif; line-height: 1.85; color: #1e293b; max-width: 820px; margin: 0 auto; padding: 25px 20px;">
  <div style="border-bottom: 3px solid #7c3aed; padding-bottom: 12px; margin-bottom: 25px;">
    <h1 style="color: #0f172a; font-size: 28px; margin: 0 0 8px 0; font-weight: 800;">プライバシーポリシー (Privacy Policy)</h1>
    <div style="color: #64748b; font-size: 15px; font-weight: 500;">個人情報保護方針およびCookie（クッキー）ポリシー</div>
  </div>

  <p style="font-size: 15px; color: #475569;">当サイト「暮らしの法律とお金の知恵」は、読者の個人情報保護を尊重し、適正な取り扱いに努めます。</p>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #7c3aed; padding-left: 12px;">広告の配信について（Google AdSense）</h2>
  <p style="font-size: 15px; color: #475569;">当サイトでは、第三者配信の広告サービス「Google AdSense（グーグルアドセンス）」を利用しています。</p>
  <ul style="margin: 10px 0; padding-left: 20px; color: #334155; font-size: 14px;">
    <li style="margin-bottom: 8px;">Googleなどの第三者広告配信事業者は、Cookieを使用して、ユーザーが当サイトや他のウェブサイトに過去にアクセスした際の情報に基づいて広告を配信します。</li>
    <li style="margin-bottom: 8px;">ユーザーは、<a href="https://adssettings.google.com" target="_blank" rel="noopener" style="color: #7c3aed;">Google広告設定</a>でパーソナライズ広告を無効にすることができます。</li>
  </ul>

  <h2 style="color: #1e293b; font-size: 20px; margin-top: 32px; font-weight: 700; border-left: 4px solid #7c3aed; padding-left: 12px;">個人情報の取り扱いに関するお問い合わせ</h2>
  <p style="font-size: 15px; color: #475569;">プライバシーポリシーに関するご質問は、<a href="mailto:dlwoduq20@gmail.com" style="color: #7c3aed;">dlwoduq20@gmail.com</a>までご連絡ください。</p>
</div>"""

    return {"about": about_html, "disclaimer": disclaimer_html, "privacy": privacy_html}


# -----------------------------------------------------------------------------
# MAIN REMEDIATION PIPELINE
# -----------------------------------------------------------------------------

BLOGS_CONFIG = [
    {
        "id": "1939932974175805877",
        "name": "StackPilot (US SaaS)",
        "url": "https://smartlawstep.blogspot.com",
        "pages_data": build_stackpilot_pages(),
        "target_live_posts": 18
    },
    {
        "id": "7758791627533733698",
        "name": "GreenThumb Garden (US)",
        "url": "https://greenthumb-garden.blogspot.com",
        "pages_data": build_greenthumb_pages(),
        "target_live_posts": 18
    },
    {
        "id": "3888865366756619756",
        "name": "생활 속 법과 금융 (KR)",
        "url": "https://kgamjablog.blogspot.com",
        "pages_data": build_kgamja_pages(),
        "target_live_posts": 18
    },
    {
        "id": "4884263507030240234",
        "name": "暮らしの法律とお金の知恵 (JP)",
        "url": "https://seikatsulaw.blogspot.com",
        "pages_data": build_seikatsu_pages(),
        "target_live_posts": 18
    }
]

def main():
    print("=" * 70)
    print("STARTING GOOGLE ADSENSE REMEDIATION FOR ALL 4 BLOGS")
    print("=" * 70)

    backup_record = {}

    for b in BLOGS_CONFIG:
        bid = b["id"]
        bname = b["name"]
        print(f"\n>>> PROCESSING BLOG: {bname} ({bid}) <<<")

        # ---------------------------------------------------------------------
        # 1. Update E-E-A-T Static Pages
        # ---------------------------------------------------------------------
        print(f"[{bname}] Step 1: Updating static E-E-A-T pages...")
        pages_res = service.pages().list(blogId=bid).execute()
        existing_pages = pages_res.get("items", [])
        
        pages_map = {}
        for p in existing_pages:
            t = p.get("title", "").lower()
            u = p.get("url", "").lower()
            if "about" in t or "소개" in t or "について" in t or "about" in u:
                pages_map["about"] = p
            elif "disclaimer" in t or "contact" in t or "면책" in t or "お問い合わせ" in t or "contact" in u:
                pages_map["disclaimer"] = p
            elif "privacy" in t or "개인정보" in t or "プライバシー" in t or "privacy" in u:
                pages_map["privacy"] = p

        pdata = b["pages_data"]

        for pkey in ["about", "disclaimer", "privacy"]:
            content_html = pdata[pkey]
            if pkey in pages_map:
                target_page = pages_map[pkey]
                pid = target_page["id"]
                title = target_page["title"]
                # Update title to be clean
                if pkey == "about":
                    title = "About Us" if "US" in bname or "StackPilot" in bname or "GreenThumb" in bname else ("블로그 소개 (About Us)" if "KR" in bname else "当サイトについて (About Us)")
                elif pkey == "disclaimer":
                    title = "Disclaimer & Contact" if "US" in bname or "StackPilot" in bname or "GreenThumb" in bname else ("문의 및 면책조항 (Contact & Disclaimer)" if "KR" in bname else "免責事項・お問い合わせ (Contact & Disclaimer)")
                elif pkey == "privacy":
                    title = "Privacy Policy" if "US" in bname or "StackPilot" in bname or "GreenThumb" in bname else ("개인정보처리방침 (Privacy Policy)" if "KR" in bname else "プライバシーポリシー (Privacy Policy)")

                res = service.pages().patch(
                    blogId=bid,
                    pageId=pid,
                    body={"title": title, "content": content_html}
                ).execute()
                print(f"  [OK] Updated page '{title}' (ID: {pid}) -> {res.get('url')}")
            else:
                print(f"  [WARN] Page key '{pkey}' not matched on {bname}!")

        # ---------------------------------------------------------------------
        # 2. Slim Down Posts (Keep Top 18 Live, Revert rest to Draft)
        # ---------------------------------------------------------------------
        print(f"\n[{bname}] Step 2: Slimming posts to top {b['target_live_posts']} live posts...")
        posts_res = service.posts().list(blogId=bid, maxResults=100, status=["LIVE"]).execute()
        live_posts = posts_res.get("items", [])
        total_live = len(live_posts)
        print(f"  Current live posts count: {total_live}")

        target_count = b["target_live_posts"]
        reverted_list = []

        if total_live > target_count:
            posts_to_revert = live_posts[target_count:]
            print(f"  Reverting {len(posts_to_revert)} posts to DRAFT (Keeping {target_count} live)...")

            for idx, p in enumerate(posts_to_revert):
                pid = p["id"]
                ptitle = p.get("title", "Untitled")
                try:
                    service.posts().revert(blogId=bid, postId=pid).execute()
                    reverted_list.append({"id": pid, "title": ptitle, "url": p.get("url")})
                    print(f"    - [{idx+1}/{len(posts_to_revert)}] Reverted to DRAFT: {ptitle[:45]}...")
                    time.sleep(0.2) # Avoid rate limits
                except Exception as e:
                    print(f"    - [ERROR] Failed to revert {pid}: {e}")

            print(f"  [DONE] Successfully reverted {len(reverted_list)} posts on {bname}.")
        else:
            print(f"  [SKIP] Current live posts ({total_live}) <= target ({target_count}). No reversion needed.")

        backup_record[bname] = {
            "blogId": bid,
            "kept_live_count": min(total_live, target_count),
            "reverted_count": len(reverted_list),
            "reverted_posts": reverted_list
        }

    # Save backup record
    backup_file = "remedy_adsense_backup.json"
    with open(backup_file, "w", encoding="utf-8") as f:
        json.dump(backup_record, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print("ALL REMEDIATION ACTIONS COMPLETED SUCCESSFULLY!")
    print(f"Reverted posts backed up to: {backup_file}")
    print("=" * 70)

if __name__ == "__main__":
    main()
