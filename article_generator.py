"""
Article Generator using Gemini API with reliable flash models and retry backoff
"""
import json
import re
import time
from google import genai
from google.genai import types
from config import GEMINI_API_KEY
from prompt_template import SYSTEM_PROMPT

MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-3-flash-preview"
]


ARCHETYPES_KR = [
    {
        "name": "procedure_first",
        "instruction": (
            "글 구성 아키타입 A (신속 절차 및 증거 확보 중심형):\n"
            "1. 1인칭 공감 도입부 + 검증일자 포함 E-E-A-T 기준 박스\n"
            "2. '골든타임 긴급 행동 수칙': 당일 즉시 확보해야 할 3대 증거 자료\n"
            "3. 법원/관공서 단계별 해결 절차 (동적 H2/H3)\n"
            "4. 실무 비교 및 필요 서류 정리 반응형 <table> 표\n"
            "5. '내 상황에 맞는 최적의 해결 절차' 의사결정 매트릭스 표\n"
            "6. 자주 묻는 질문 FAQ (FAQPage schema)\n"
            "7. 관련 법령 및 공식 근거 자료 (Sources & References) 섹션"
        )
    },
    {
        "name": "cost_evidence_first",
        "instruction": (
            "글 구성 아키타입 B (비용 분석 및 실익 계산 중심형):\n"
            "1. 1인칭 공감 도입부 + 검증일자 포함 E-E-A-T 기준 박스\n"
            "2. '소송 vs 합의 손익 계산': 변호사 보수, 인지대, 송달료 대비 회수 실익 분석\n"
            "3. 상대방의 반박/이의신청을 무력화하는 객관적 증거 채증 요령 (동적 H2/H3)\n"
            "4. 비용 및 기간 비교 반응형 <table> 표\n"
            "5. '내 상황에 맞는 최적의 해결 절차' 의사결정 매트릭스 표\n"
            "6. 실무 FAQ (FAQPage schema)\n"
            "7. 관련 법령 및 공식 근거 자료 (Sources & References) 섹션"
        )
    },
    {
        "name": "scenario_matrix_first",
        "instruction": (
            "글 구성 아키타입 C (상대방 유형별 맞춤 대응 로드맵 중심형):\n"
            "1. 1인칭 공감 도입부 + 검증일자 포함 E-E-A-T 기준 박스\n"
            "2. '상대방 태도에 따른 3가지 분기점': 연락 가능 vs 연락 두절 vs 적반하장 고소 협박\n"
            "3. 분기별 실무 대처법과 전자소송 접수 요령 (동적 H2/H3)\n"
            "4. 상황별 필수 구비 서류 <table> 표\n"
            "5. '내 상황에 맞는 최적의 해결 절차' 의사결정 매트릭스 표\n"
            "6. 핵심 FAQ (FAQPage schema)\n"
            "7. 관련 법령 및 공식 근거 자료 (Sources & References) 섹션"
        )
    }
]


def generate_article(topic: str, related_articles: list = None) -> dict:
    """
    Generate a full SEO-optimized article matching kgamjablog's DNA with E-E-A-T, dynamic headings,
    sources section, and structural archetype diversity.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")

    import random
    archetype = random.choice(ARCHETYPES_KR)
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    links_text = ""
    if related_articles:
        links_text = "\n[내부 링크 후보 글 목록 (Contextual Internal Linking)]\n" + "\n".join(
            [f"- 글: '{a.get('title')}' -> URL: {a.get('url')}" for a in related_articles[:3]]
        ) + "\n위 목록 중 본문 문맥과 가장 잘 어울리는 1~2개 글을 본문 중간에 <a href='URL'>글제목</a> 형태로 자연스럽게 링크 박스로 연결해 주세요.\n"

    user_prompt = (
        f"다음 주제에 대해 독자에게 실질적인 법적·금융 해결책을 주는 고품질 블로그 글을 작성해 주세요:\n주제: {topic}\n\n"
        f"{archetype['instruction']}\n\n"
        f"필수 요구사항:\n"
        f"1. ❌ 무조건 승소/100% 환불 보장 등 과장된 단정 표현 절대 금지 (객관적 입증 요건과 현실적 법적 절차로 서술).\n"
        f"2. 도입부 직후 검증일자('2026년 9월 18일 기준')가 포함된 E-E-A-T 박스를 반드시 삽입하십시오.\n"
        f"3. 본문 내에 비교 <table> 및 '내 상황에 맞는 최적의 해결 절차 (Decision Matrix)' 표를 포함하십시오.\n"
        f"4. 글 최하단에 '관련 법령 및 공식 근거 자료 (Sources & References)' 섹션을 반드시 포함하십시오.{links_text}"
    )

    last_error = None
    for model_name in MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
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
                    raise ValueError(f"Invalid JSON response")

            except Exception as e:
                last_error = e
                print(f"⚠️ {model_name} (시도 {attempt+1}) 일시적 오류: {e}. 잠시 후 재시도...")
                time.sleep(2)

    raise RuntimeError(f"All models failed to generate article: {last_error}")
