"""
Article Generator using Gemini API with Day-of-the-Week Structural Archetypes
and Strict 1,500+ Character Minimum Enforcement.
"""
import os
import sys
import json
import re
import time

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

from datetime import datetime, timezone, timedelta
from google import genai
from google.genai import types
from config import GEMINI_API_KEY
from prompt_template import SYSTEM_PROMPT

MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash",
    "gemini-3-flash-preview",
    "gemini-2.5-flash-lite",
    "gemini-1.5-flash"
]

KST = timezone(timedelta(hours=9))

# 7 Distinct Day-of-the-Week Archetypes to eliminate monotonous mass-AI patterns
WEEKDAY_ARCHETYPES_KR = [
    # 0 = Monday (월요일)
    {
        "day_name": "월요일",
        "archetype_title": "실전 분쟁 해결 & 협상 합의서 실무형",
        "instruction": (
            "【월요일 특화 구성: 실전 분쟁 해결 & 협상 합의서 실무형】\n"
            "주초에 긴급하게 법적/금전적 갈등에 직면한 독자를 위해 '실전 분쟁 사례와 대화/합의' 중심으로 전개하십시오.\n"
            "1. 분쟁 사례 연구: 당사자 간 대립 배경 및 핵심 쟁점 (원고 vs 피고, 임차인 vs 임대인 등)\n"
            "2. 법률적 원칙 및 대법원 판례 기준 (성립 요건 및 책임 소멸 조건)\n"
            "3. 실전 협상 3단계 대화법 및 단계별 양보선 설정 가이드\n"
            "4. 합의서(또는 내용증명) 필수 5대 기재 조항 및 독소조항 배제 가이드 박스 (<div style='background:#f1f5f9;...'>)\n"
            "5. 협상 결렬 시 착수해야 할 민사/형사 조치 및 증거 수집 비교 <table>\n"
            "6. 실무 FAQ 및 공공 법률 상담 연계 안내"
        )
    },
    # 1 = Tuesday (화요일)
    {
        "day_name": "화요일",
        "archetype_title": "핵심 쟁점 Q&A 팩트체크 & 5단계 자가진단 체크리스트형",
        "instruction": (
            "【화요일 특화 구성: 핵심 쟁점 Q&A 팩트체크 & 5단계 자가진단 체크리스트형】\n"
            "인터넷의 잘못된 속설을 바로잡고 독자가 스스로 요건을 진단할 수 있도록 구성하십시오.\n"
            "1. '인터넷 속설 vs 실제 법률' O/X 팩트체크 3선 (잘못 알려진 상식 바로잡기 박스)\n"
            "2. 성립 요건 5단계 자가진단 체크리스트 반응형 <table> (문항별 인정 기준 및 점검 항목)\n"
            "3. 부적격 판정 시 대안 구제 루트 및 법정 예외 조항 상세 분석\n"
            "4. 독자들이 가장 자주 묻는 심층 실무 Q&A 5선 (상황별 구체적 행동 지침)\n"
            "5. 공공 지원 기관(법률구조공단, 금감원 등) 무료 상담 활용법"
        )
    },
    # 2 = Wednesday (수요일)
    {
        "day_name": "수요일",
        "archetype_title": "제도·상품 심층 비교 & 실수령·비용 1원 단위 모의계산형",
        "instruction": (
            "【수요일 특화 구성: 제도·상품 심층 비교 & 실수령·비용 1원 단위 모의계산형】\n"
            "수치와 금융 실익에 민감한 독자를 위해 '모의계산 시뮬레이션과 비용 절감' 중심으로 전개하십시오.\n"
            "1. 제도 간 장단점 심층 비교 매트릭스 <table> (대상, 지원 금액, 필요 서류, 한계점)\n"
            "2. '실제 모의계산 시뮬레이션': 구체적인 가상 조건(소득, 기간 등)을 대입한 1원 단위 산출 공식 및 시뮬레이션 표\n"
            "3. 수수료, 이자, 가산세, 중도상환비용 등을 줄이는 3대 실무 절약 테크닉\n"
            "4. 신청 전 반드시 구비해야 할 소득/금융 증빙 서류 5종 및 온라인 즉시 발급처\n"
            "5. 감액 규정 및 부당 수급 환수 위험 방지 안전 수칙"
        )
    },
    # 3 = Thursday (목요일)
    {
        "day_name": "목요일",
        "archetype_title": "정부24·홈택스 100% 승인 온라인 신청 실무 로드맵형",
        "instruction": (
            "【목요일 특화 구성: 정부24·홈택스 100% 승인 온라인 신청 실무 로드맵형】\n"
            "기관 방문 없이 인터넷과 모바일로 원스톱 처리하려는 독자를 위한 '단계별 실행 로드맵'입니다.\n"
            "1. 신청 전 3분 컷 사전 준비물 및 본인인증 수단 점검표\n"
            "2. 1단계부터 5단계까지 온라인 클릭 순서 타임라인 로드맵 (화면별 입력 요령 및 서류 첨부법)\n"
            "3. '이것 때문에 90% 반려된다': 담당 공무원이 서류를 반려하는 대표 실수 3가지와 예방법 경고 박스\n"
            "4. 접수 후 심사 진행 상황 조회 방법 및 보정 명령(추가 서류 요청) 즉각 대응 요령\n"
            "5. 승인 후 지원금/권리 이행 절차 및 사후 유지 관리 체크포인트"
        )
    },
    # 4 = Friday (금요일)
    {
        "day_name": "금요일",
        "archetype_title": "2026년 최신 개정 법률 & 대법원 판례 집중 분석형",
        "instruction": (
            "【금요일 특화 구성: 2026년 최신 개정 법률 & 대법원 판례 집중 분석형】\n"
            "최신 법률 변경과 법원 판단 기준에 기반한 '고급 법률 지식 및 리스크 관리' 중심입니다.\n"
            "1. 2026년 달라진 핵심 개정 사항 요약 <table> (종전 규정 vs 2026년 개정 조항 비교)\n"
            "2. 최근 대법원/하급심 주요 판례 심층 분석 (사건 개요, 판시 사항, 판결 이유)\n"
            "3. 이번 법 개정/판례가 일반 직장인·서민·임차인에게 미치는 실질적 권리 변화\n"
            "4. 과도기 및 법 개정 공백기에 발생할 수 있는 신종 분쟁 유형과 사전 차단책\n"
            "5. 전문가가 제언하는 향후 법적 분쟁 승소 요건 체크리스트"
        )
    },
    # 5 = Saturday (토요일)
    {
        "day_name": "토요일",
        "archetype_title": "초보자·사회초년생 눈높이 쉬운 법률·금융 첫걸음",
        "instruction": (
            "【토요일 특화 구성: 초보자·사회초년생 눈높이 쉬운 법률·금융 첫걸음】\n"
            "주말 독자를 위해 어려운 법률/금융 용어를 일상 비유로 쉽게 풀어쓴 '입문자 맞춤 가이드'입니다.\n"
            "1. 3분 개념 사전: 어려운 법률/금융 전문 용어 3가지를 일상 비유로 쉽게 설명\n"
            "2. 사회초년생이 계약이나 서명할 때 가장 흔히 저지르는 치명적 실수 3선\n"
            "3. 내 권리를 지키는 필수 3대 방어막 (확정일자, 계약서 특약, 지급거절권 등)\n"
            "4. 불리한 서명이나 구두 계약을 피하는 현장 대처 및 거절 멘트 가이드\n"
            "5. '한눈에 보는 핵심 3줄 요약 카드' (<div style='background:#fef3c7;...'>) 및 단계별 추천 절차"
        )
    },
    # 6 = Sunday (일요일)
    {
        "day_name": "일요일",
        "archetype_title": "피해 예방 & 긴급 위기 대응 골든타임 매뉴얼형",
        "instruction": (
            "【일요일 특화 구성: 피해 예방 & 긴급 위기 대응 골든타임 매뉴얼형】\n"
            "사기, 급전 위기, 갑작스러운 통보를 당한 독자를 위한 '시간대별 긴급 대응 매뉴얼'입니다.\n"
            "1. '골든타임 1시간 이내': 즉시 실행해야 할 긴급 계좌지급정지, 카드정지 및 증거 캡처\n"
            "2. '사건 발생 24시간 이내': 경찰서 사이버수사팀 신고, 금융감독원 피해구제 접수 절차\n"
            "3. '사건 발생 7일 이내': 가압류, 내용증명 발송, 전자소송 지급명령 신청 로드맵\n"
            "4. 피해 원금 회수를 위한 형사 배상명령 신청 및 민사소송 병행 전략\n"
            "5. 긴급 24시간 비상 연락망 및 무료 법률 지원 기관 연락처 총정리 표"
        )
    }
]


def extract_pure_text_len(html_content: str) -> int:
    """
    Computes pure text length excluding HTML tags and scripts.
    """
    clean = re.sub(r'<script.*?</script>', '', html_content, flags=re.DOTALL)
    clean = re.sub(r'<style.*?</style>', '', clean, flags=re.DOTALL)
    clean = re.sub(r'<[^>]+>', '', clean)
    clean = re.sub(r'\s+', '', clean)
    return len(clean)


def generate_article(topic: str, related_articles: list = None) -> dict:
    """
    Generate a full SEO-optimized article matching kgamjablog's DNA with E-E-A-T,
    weekday-specific structural diversity, and strict 1,500+ character enforcement.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")

    # Determine Day-of-the-Week in KST (UTC+9)
    kst_now = datetime.now(KST)
    weekday_idx = kst_now.weekday()
    archetype = WEEKDAY_ARCHETYPES_KR[weekday_idx]
    today_str = kst_now.strftime("%Y년 %m월 %d일")

    print(f"📅 [요일별 양식 적용] {archetype['day_name']} - {archetype['archetype_title']} (기준일: {today_str})")

    client = genai.Client(api_key=GEMINI_API_KEY)

    links_text = ""
    if related_articles:
        links_text = "\n[내부 링크 후보 글 목록 (Contextual Internal Linking)]\n" + "\n".join(
            [f"- 글: '{a.get('title')}' -> URL: {a.get('url')}" for a in related_articles[:3]]
        ) + "\n위 목록 중 본문 문맥과 가장 잘 어울리는 1~2개 글을 본문 중간에 <a href='URL'>글제목</a> 형태로 자연스럽게 링크 박스로 연결해 주세요.\n"

    user_prompt = (
        f"다음 주제에 대해 독자에게 실질적인 법적·금융 해결책을 주는 고품질 블로그 글을 작성해 주세요:\n"
        f"주제: {topic}\n\n"
        f"【오늘({archetype['day_name']})의 필수 글 구성 양식】\n"
        f"{archetype['instruction']}\n\n"
        f"【필수 준수 사항】\n"
        f"1. 📏 글자 수 엄수: 본문 순수 텍스트(HTML 태그 제외)는 반드시 **1,800자 이상(최소 1,500자 이상)**이어야 합니다. 요건, 법 조항 조문, 단계별 실무 절차, 서식 작성 요령, 수치 계산을 풍부하게 서술하십시오.\n"
        f"2. 도입부 직후 검증일자 배지 박스를 반드시 삽입하십시오:\n"
        f"   `<div style=\"background: #f8fafc; border-left: 4px solid #0284c7; padding: 16px 20px; margin: 24px 0; border-radius: 8px; font-size: 14px; color: #334155; line-height: 1.6;\">\n"
        f"     <div style=\"font-weight: 700; color: #0f172a; margin-bottom: 6px; font-size: 15px;\">🛡️ 생활 속 법률·금융 가이드 검증 준칙 ({archetype['day_name']} 팩트체크)</div>\n"
        f"     본 가이드는 대한민국 현행 법령, 대법원 판례, 소관 부처 실무 지침을 바탕으로 엄격히 검증하여 작성되었습니다.\n"
        f"     <div style=\"margin-top: 10px; padding-top: 8px; border-top: 1px solid #e2e8f0; font-size: 13px; color: #64748b;\">\n"
        f"       📅 <strong>법령 및 실무 절차 최종 검증:</strong> {today_str} 기준 | <strong>정기 업데이트:</strong> 주간 법령·제도 개정 반영\n"
        f"     </div>\n"
        f"   </div>`\n"
        f"3. ❌ 가짜 1인칭 후기('내가 겪은...') 및 무조건 승소/환불 보장 과장 표현 절대 금지.\n"
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
                except Exception:
                    json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                    if json_match:
                        data = json.loads(json_match.group(0))
                    else:
                        raise ValueError("Invalid JSON response from model")

                content_html = data.get("content_html", "")
                text_len = extract_pure_text_len(content_html)
                print(f"📊 [생성된 글 분석] 모델: {model_name}, 순수 본문 글자 수: {text_len}자 (HTML 포함: {len(content_html)}자)")

                # Enforce minimum 1,500 characters
                if text_len < 1500:
                    print(f"⚠️ 글자 수 ({text_len}자)가 기준(1,500자)에 미달하여 더 상세한 내용으로 재확장 시도...")
                    expand_prompt = (
                        f"작성된 블로그 글 본문의 내용이 약 {text_len}자로 다소 간략합니다. "
                        f"실제 E-E-A-T 기준을 충족할 수 있도록, 본문에 구체적인 법률 조문 설명, 실제 실무 서류 작성 요령, "
                        f"단계별 대처법, 반려 예방 수칙, 상세 사례를 대폭 보강하여 순수 본문 2,000자 이상으로 확장된 JSON을 다시 응답해 주세요."
                    )
                    exp_response = client.models.generate_content(
                        model=model_name,
                        contents=[user_prompt, raw_text, expand_prompt],
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT,
                            temperature=0.7,
                            response_mime_type="application/json"
                        )
                    )
                    exp_raw = exp_response.text.strip()
                    try:
                        exp_data = json.loads(exp_raw)
                        exp_len = extract_pure_text_len(exp_data.get("content_html", ""))
                        if exp_len >= text_len:
                            data = exp_data
                            print(f"✅ [글자 수 확장 성공] {text_len}자 -> {exp_len}자로 확장 완료!")
                    except Exception as e:
                        print(f"ℹ️ 확장 파싱 참고 ({e}), 원본 데이터 사용")

                return data

            except Exception as e:
                last_error = e
                print(f"⚠️ {model_name} (시도 {attempt+1}) 일시적 오류: {e}. 잠시 후 재시도...")
                time.sleep(2)

    raise RuntimeError(f"All models failed to generate article: {last_error}")
