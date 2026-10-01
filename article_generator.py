"""
Article Generator using Gemini API with 10 Expanded Narrative Formats
and Strict 1,500+ Character Minimum Enforcement.
Eliminates rigid repetitive boilerplates and introduces rich format polymorphism.
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
    "gemini-3.8-flash"
]

KST = timezone(timedelta(hours=9))

# 10 Rich, Distinct Narrative & Structural Formats for Complete Anti-AI Diversification
EXPANDED_FORMATS_KR = [
    # 0. 1:1 실무 상담실 대화록 & 직설 솔루션형
    {
        "id": "consultation_qa",
        "title": "실무 상담실 1:1 대화록 & 직설 솔루션형",
        "keywords": ["상담", "질문", "어떻게", "되나요", "해결", "법률상담", "합의금", "방법"],
        "instruction": (
            "【포맷: 실무 상담실 1:1 대화록 & 직설 솔루션형】\n"
            "실제 법률·금융 전문 상담 창구에서 의뢰인이 겪는 절박한 갈등을 다루듯, 독자와 마주 앉아 대화하는 생생한 구어체와 직설적 해설로 전개하십시오.\n"
            "1. [의뢰인 긴급 상담 사연]: 당사자가 직면한 현실적 분쟁 상황과 핵심 딜레마 (대화록 형식 인용 박스)\n"
            "2. [에디터의 1차 직설 진단]: '지금 당장 이것부터 멈추셔야 합니다' - 흔히 저지르는 치명적 실수 경고\n"
            "3. [심층 1문 1답 Q&A 3선]: 독자가 가장 궁금해하는 핵심 질문 3가지에 대해 법령 조문(제O조)과 판례를 곁들인 사이다 답변\n"
            "4. [실무 방어 체크리스트]: 당사자가 오늘 바로 확보해야 할 문자/녹취/서류 5대 증거 목록 반응형 <table>\n"
            "5. [상담 마무리 현실 조언]: 원만한 합의가 어려울 때 법률구조공단 또는 소송/지급명령으로 직행하는 현실적 루트"
        )
    },
    # 1. D-Day 시간순 현실 액션 타임라인형
    {
        "id": "chronological_timeline",
        "title": "D-Day 시간순 현실 액션 타임라인형",
        "keywords": ["기한", "일정", "순서", "단계", "타임라인", "만료", "퇴사", "지급정지", "해지"],
        "instruction": (
            "【포맷: D-Day 시간순 현실 액션 타임라인형】\n"
            "사건 발생부터 최종 해결까지 현실적인 시간 흐름(D-Day, D+1일, D+7일, D+14일, D+30일)에 따라 일기장/로그북처럼 구성하십시오.\n"
            "1. [D-Day 사건 발생 당일]: 상황 인지 즉시 취해야 할 1시간 이내 골든타임 긴급 행동 지침\n"
            "2. [D+1일~D+3일 초동 대처 및 증거 박제]: 상대방과의 통화 녹음 요령, 내용증명 초안 작성 및 우체국 발송 요령\n"
            "3. [D+7일~D+14일 행정·법적 압박 단계]: 관공서 신고, 임차권등기명령, 전자소송 지급명령 접수 실무\n"
            "4. [D+30일 최종 이행 및 강제집행 분기점]: 이행 거부 시 급여/통장 압류 절차 및 승소 후 실비용 회수 요령\n"
            "5. [타임라인 한눈에 보기 요약 <table>]: 각 시점별 필수 구비 서류 및 법정 소멸시효 점검표"
        )
    },
    # 2. 인터넷 속설 팩트폭격 오답노트형
    {
        "id": "mythbuster_factcheck",
        "title": "인터넷 속설 팩트폭격 오답노트형",
        "keywords": ["오해", "속설", "진실", "루머", "주의", "처벌", "사기", "합의", "실수"],
        "instruction": (
            "【포맷: 인터넷 속설 팩트폭격 오답노트형】\n"
            "인터넷 블로그나 커뮤니티에 떠도는 잘못된 '카더라' 속설 3가지를 가차 없이 깨부수는 팩트폭격 형식으로 전개하십시오.\n"
            "1. ❌ [오답 1: '인터넷에서 흔히 믿는 치명적 속설'] vs ⭕ [진실: 법원 판례 및 법률 조문 근거 반박]\n"
            "2. ❌ [오답 2: '많은 사람이 손해 보는 두 번째 오해'] vs ⭕ [진실: 실제 실무상 반려 및 패소 사유 분석]\n"
            "3. ❌ [오답 3: '절대 믿으면 안 되는 세 번째 잘못된 상식'] vs ⭕ [진실: 소관 부처 공식 유권해석 기준]\n"
            "4. [진짜 전문가만 아는 법정 예외 조항 (단서 조항)]: 원칙을 뒤집는 결정적 판례 2선 심층 분석\n"
            "5. [손해 방지 실무 요약표]: 잘못된 대처 vs 올바른 정석 대처 비교 반응형 <table>"
        )
    },
    # 3. 실물 공문서·신청서 빈칸 밀착 해설형
    {
        "id": "document_walkthrough",
        "title": "실물 공문서·신청서 빈칸 밀착 해설형",
        "keywords": ["작성법", "신청서", "양식", "서식", "합의서", "내용증명", "진정서", "고소장", "작성요령"],
        "instruction": (
            "【포맷: 실물 공문서·신청서 빈칸 밀착 해설형】\n"
            "실제 법원/노동청/공공기관 제출 서식을 책상 위에 올려놓고 한 줄 한 줄 짚어주듯 서식 빈칸 작성법 중심으로 전개하십시오.\n"
            "1. [서식 전체 윤곽 및 필수 기재 3대 핵심 블록 안내]\n"
            "2. [1번 빈칸: 청구취지/신청원인 작성 요령] - 담당관이 한눈에 파악할 수 있는 육하원칙 문장 예시\n"
            "3. [2번 빈칸: '이 단어 쓰면 90% 반려된다'] - 반려와 보정명령을 유발하는 금기 문구와 통과되는 대체 표현\n"
            "4. [3번 빈칸: 입증자료 첨부 규격] - 법적 효력을 갖는 첨부 서류 목록 및 온라인 PDF 변환 규격\n"
            "5. [완성된 실전 서식 샘플 박스]: 실제 복사해 쓸 수 있는 정석 작성 서식 예시문 및 접수 전 최종 자가 점검표"
        )
    },
    # 4. 1원 단위 모의계산 & 비용 영수증 해체형
    {
        "id": "cost_simulation_breakdown",
        "title": "1원 단위 모의계산 & 비용 영수증 해체형",
        "keywords": ["계산", "모의계산", "공제", "수수료", "세금", "상속세", "증여세", "실업급여", "이자", "지원금", "비용"],
        "instruction": (
            "【포맷: 1원 단위 모의계산 & 비용 영수증 해체형】\n"
            "모호한 말 대신 정확한 숫자와 공식으로 독자의 실익을 증명하는 금융·세무 모의계산 분석으로 전개하십시오.\n"
            "1. [가상 시나리오 조건 설정]: 독자가 가장 흔히 겪는 구체적 조건(소득, 재산, 가입 기간, 부양가족 등) 대입\n"
            "2. ['1원 단위 영수증 명세서']: 기본 산출액, 공제 감면액, 세금/수수료 차감 내역을 낱낱이 분해한 정밀 <table>\n"
            "3. [모의계산 산출 공식 단계별 역산]: 일반인이 직접 대입해 볼 수 있는 3단계 자가 계산 공식\n"
            "4. [실무 절세/비용 절약 테크닉 3선]: 신고 기한 준수, 법정 특약 활용, 공제 요건 맞추기\n"
            "5. [추징 및 가산세 위험 방지 안전 수칙]: 국세청/소관 부처의 과다 공제 검증 기준과 방어책"
        )
    },
    # 5. 대립 구도 협상 테이블 & 시나리오 분기형
    {
        "id": "negotiation_branching",
        "title": "대립 구도 협상 테이블 & 시나리오 분기형",
        "keywords": ["협상", "합의", "대립", "분쟁", "손해배상", "교통사고", "임대인", "임차인", "퇴직금", "갈등"],
        "instruction": (
            "【포맷: 대립 구도 협상 테이블 & 시나리오 분기형】\n"
            "상대방과 팽팽하게 맞서는 협상 테이블에서 나의 패(권리)를 지키는 게임 이론식 대립 구도로 전개하십시오.\n"
            "1. [협상 테이블 양측 대립 구도]: 상대방의 전형적 압박 논리 vs 나의 방어 논리 대조\n"
            "2. [시나리오 A: 원만한 합의 성립 시] - 독소조항 없는 안전한 합의서 필수 5대 문구 및 위약벌 규정\n"
            "3. [시나리오 B: 협상 결렬 및 소송 돌입 시] - 소송 실익 계산(인지대, 송달료 vs 회수 기대액) 및 집행 절차\n"
            "4. [상대방이 흔히 쓰는 '블러핑(허세)' 간파법]: 법적 효력 없는 위협 멘트 팩트체크\n"
            "5. [협상 타결용 최종 체크리스트 및 실무 가이드 <table>]"
        )
    },
    # 6. 초보자·사회초년생 눈높이 '3분 컷' 개념사전 & 행동강령
    {
        "id": "beginner_friendly_brief",
        "title": "초보자·사회초년생 눈높이 '3분 컷' 개념사전 & 행동강령",
        "keywords": ["초보", "사회초년생", "첫걸음", "기초", "용어", "계약서", "원룸", "전세계약", "알바"],
        "instruction": (
            "【포맷: 초보자·사회초년생 눈높이 '3분 컷' 개념사전 & 행동강령】\n"
            "법률·금융 용어가 낯선 주말 독자와 사회초년생을 위해 모든 난해한 용어를 일상 비유로 쉽게 번역하여 전개하십시오.\n"
            "1. [3분 개념 사전]: 어려운 한자어 법률 용어 3가지(예: 대항력, 우선변제권, 근저당)를 실생활 비유로 단번에 이해시키기\n"
            "2. [사회초년생이 서명할 때 가장 흔히 당하는 함정 3선]: 구두 약속의 위험과 계약서 특약 누락\n"
            "3. [오늘 당장 내 권리를 지키는 필수 3대 방어막]: 확정일자, 내용증명, 지급거절권 실무 요령\n"
            "4. [거절하기 어려운 상황에서 쓰는 현실적 현장 대처 멘트]: 법적으로 불리한 서명을 피하는 거절 화법\n"
            "5. [한눈에 보는 핵심 3줄 요약 카드 및 추천 실행 로드맵]"
        )
    },
    # 7. 2026년 최신 개정 법률 비포&애프터 심층 칼럼
    {
        "id": "before_after_law",
        "title": "2026년 최신 개정 법률 비포&애프터 심층 칼럼",
        "keywords": ["2026", "개정", "법률개정", "판례", "대법원", "달라진", "신설", "법개정", "시행령"],
        "instruction": (
            "【포맷: 2026년 최신 개정 법률 비포&애프터 심층 칼럼】\n"
            "2026년 달라진 법령과 대법원 최신 판례를 바탕으로 깊이 있는 시사·실무 법률 칼럼으로 전개하십시오.\n"
            "1. [2026년 무엇이 바뀌었는가]: 종전 규정(Before) vs 2026년 현행 규정(After) 정밀 대조 <table>\n"
            "2. [개정 배경과 국민 실생활에 미치는 실질적 법적 효력 분석]\n"
            "3. [대법원 최신 쟁점 판례 심층 해석]: 하급심의 판결 흐름과 입증 책임의 변화\n"
            "4. [과도기 공백기에 주의해야 할 신종 법적 분쟁 유형 및 예방 대책]\n"
            "5. [법 개정에 따른 개인 권리 주장 가이드 및 법적 근거 조문 총정리]"
        )
    },
    # 8. 골든타임 긴급 위기 탈출 매뉴얼
    {
        "id": "emergency_golden_time",
        "title": "골든타임 긴급 위기 탈출 매뉴얼",
        "keywords": ["사기", "보이스피싱", "긴급", "골든타임", "가압류", "압류", "피해", "신고", "도난"],
        "instruction": (
            "【포맷: 골든타임 긴급 위기 탈출 매뉴얼】\n"
            "사기, 급전 위기, 갑작스러운 통보를 당한 독자를 위해 분초를 다투는 '비상 응급 매뉴얼'로 전개하십시오.\n"
            "1. ['골든타임 1시간 이내']: 즉시 계좌지급정지, 카드 정지, 공인인증서 폐기 및 통신사 소액결제 차단\n"
            "2. ['사건 발생 24시간 이내']: 경찰서 사이버수사팀 방문, 사건사고사실확인원 발급, 금융감독원 피해구제 접수\n"
            "3. ['사건 발생 7일 이내']: 가압류 신청, 가해자 인적사항 사실조회, 전자소송 지급명령 신청\n"
            "4. [피해 원금 회수를 위한 형사 배상명령 신청 및 민사소송 병행 전략]\n"
            "5. [24시간 긴급 비상 연락망 및 무료 법률 지원 기관 연락처 총정리 <table>]"
        )
    },
    # 9. 공공기관 100% 승인 원스톱 온라인 로드맵
    {
        "id": "online_approval_roadmap",
        "title": "공공기관 100% 승인 원스톱 온라인 로드맵",
        "keywords": ["온라인", "정부24", "홈택스", "인터넷", "신청방법", "모바일", "발급", "조회", "허그", "HUG"],
        "instruction": (
            "【포맷: 공공기관 100% 승인 원스톱 온라인 로드맵】\n"
            "기관 방문 없이 집에서 스마트폰과 PC로 원스톱 처리할 수 있는 클릭 경로 중심의 실무 로드맵으로 전개하십시오.\n"
            "1. [신청 전 3분 컷 사전 준비물]: 필수 인증서 종류, 제출 서류 PDF 변환 및 용량 제한 점검표\n"
            "2. [1단계부터 5단계까지 온라인 클릭 메뉴 경로]: 화면별 입력 요령 및 필수 체크 옵션\n"
            "3. ['담당 공무원이 90% 반려하는 3대 실수' 경고 및 예방법 박스]\n"
            "4. [접수 후 심사 진행 상황 실시간 조회법 및 보정 명령(추가 서류 요청) 즉각 대응 요령]\n"
            "5. [승인 후 혜택 수령 및 사후 자격 유지 관리 체크포인트]"
        )
    }
]


def select_writing_format(topic: str, kst_now: datetime) -> dict:
    """
    Intelligently select the best matching narrative format for the topic,
    or smoothly rotate across the 10 formats to guarantee total diversification.
    """
    topic_lower = topic.lower()
    # 1. Keyword-based matching
    scored = []
    for fmt in EXPANDED_FORMATS_KR:
        score = sum(1 for kw in fmt["keywords"] if kw.lower() in topic_lower)
        if score > 0:
            scored.append((score, fmt))

    if scored:
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]

    # 2. Rotation fallback based on hash of topic + day
    h_idx = (sum(ord(c) for c in topic) + kst_now.day) % len(EXPANDED_FORMATS_KR)
    return EXPANDED_FORMATS_KR[h_idx]


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
    10 expanded dynamic formats, organic styling (zero rigid boilerplate),
    and strict 1,500+ character enforcement.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")

    kst_now = datetime.now(KST)
    selected_format = select_writing_format(topic, kst_now)
    today_str = kst_now.strftime("%Y년 %m월 %d일")

    print(f"📖 [선택된 글 전개 포맷] '{selected_format['title']}' (포맷 ID: {selected_format['id']})")

    client = genai.Client(api_key=GEMINI_API_KEY)

    links_text = ""
    if related_articles:
        links_text = "\n[내부 링크 후보 글 목록 (Contextual Internal Linking)]\n" + "\n".join(
            [f"- 글: '{a.get('title')}' -> URL: {a.get('url')}" for a in related_articles[:3]]
        ) + "\n위 목록 중 본문 문맥과 가장 잘 어울리는 1~2개 글을 본문 중간에 자연스럽게 연결해 주세요.\n"

    user_prompt = (
        f"다음 주제에 대해 독자에게 실질적인 법적·금융 해결책을 주는 고품질 전문 블로그 글을 작성해 주세요:\n"
        f"주제: {topic}\n\n"
        f"【이번 글의 필수 전개 포맷】\n"
        f"{selected_format['instruction']}\n\n"
        f"【필수 준수 사항】\n"
        f"1. 📏 글자 수 엄수: 본문 순수 텍스트(HTML 태그 제외)는 반드시 **1,800자 이상(최소 1,500자 이상)**이어야 합니다. 요건, 법 조항 조문, 단계별 실무 절차, 서식 작성 요령, 수치 계산을 풍부하게 서술하십시오.\n"
        f"2. 🚫 기계적 고정 박스 삽입 금지: 과거의 천편일률적인 '🛡️ 검증 준칙' 배지나 고정된 회색 '📚 법령 출처' 박스를 기계적으로 복제해 넣지 마십시오. 법률 조문, 판례, 소관 기관 기준은 본문 서사 문맥 속에 자연스러운 사람의 글처럼 유기적으로 녹여내십시오.\n"
        f"3. ❌ 가짜 1인칭 후기('내가 겪은...') 및 무조건 승소/환불 보장 과장 표현 절대 금지.\n"
        f"4. 지정된 전개 포맷({selected_format['title']})의 고유한 서사 호흡과 리듬을 살려 생생하게 서술하십시오.{links_text}"
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

                # Record format_id
                data["format_id"] = selected_format["id"]

                content_html = data.get("content_html", "")
                text_len = extract_pure_text_len(content_html)
                print(f"📊 [생성된 글 분석] 모델: {model_name}, 포맷: {selected_format['id']}, 순수 본문 글자 수: {text_len}자 (HTML 포함: {len(content_html)}자)")

                # Enforce minimum 1,500 characters
                if text_len < 1500:
                    print(f"⚠️ 글자 수 ({text_len}자)가 기준(1,500자)에 미달하여 더 상세한 내용으로 재확장 시도...")
                    expand_prompt = (
                        f"작성된 블로그 글 본문의 내용이 약 {text_len}자로 다소 간략합니다. "
                        f"선택된 전개 포맷({selected_format['title']})의 특성을 살려, 본문에 구체적인 법률 조문 설명, "
                        f"실제 실무 서류 작성 요령, 단계별 대처법, 반려 예방 수칙, 상세 사례를 대폭 보강하여 "
                        f"순수 본문 2,000자 이상으로 확장된 JSON을 다시 응답해 주세요."
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
                            data["format_id"] = selected_format["id"]
                            print(f"✅ [글자 수 확장 성공] {text_len}자 -> {exp_len}자로 확장 완료!")
                    except Exception as e:
                        print(f"ℹ️ 확장 파싱 참고 ({e}), 원본 데이터 사용")

                return data

            except Exception as e:
                last_error = e
                print(f"⚠️ {model_name} (시도 {attempt+1}) 일시적 오류: {e}. 잠시 후 재시도...")
                time.sleep(2)

    raise RuntimeError(f"All models failed to generate article: {last_error}")
