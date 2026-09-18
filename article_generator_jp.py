"""
Japanese Article Generator using Gemini API with reliable flash models and retry backoff
"""
import json
import re
import time
import random
from google import genai
from google.genai import types
from config import GEMINI_API_KEY
from prompt_template_jp import SYSTEM_PROMPT_JP

MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-3-flash-preview"
]

ARCHETYPES_JP = [
    {
        "name": "procedure_first",
        "instruction": (
            "記事構成アーキタイプA（緊急初動・証拠保全優先型）:\n"
            "1. 一人称共感導入部 + 検証日入りE-E-A-T監修基準ボックス\n"
            "2. 『初動対応の鉄則』：トラブル当日に即時確保すべき重要証拠3選\n"
            "3. 裁判所・公的機関のステップ別手続きマニュアル（動的H2/H3）\n"
            "4. 実務比較・必要書類まとめHTML <table>\n"
            "5. 『あなたの状況に最適な解決手順マトリクス (Decision Matrix)』表\n"
            "6. 実務FAQ（FAQPage schema）\n"
            "7. 根拠法令および公的機関出典（Sources & References）セクション"
        )
    },
    {
        "name": "cost_evidence_first",
        "instruction": (
            "記事構成アーキタイプB（費用対効果・実益計算優先型）:\n"
            "1. 一人称共感導入部 + 検証日入りE-E-A-T監修基準ボックス\n"
            "2. 『損益分岐点分析』：弁護士・司法書士費用、印紙・予納金 vs 回収実益のリアル\n"
            "3. 相手方の反論や不当請求を無効化する客観的立証資料の集め方（動的H2/H3）\n"
            "4. 費用・期間比較HTML <table>\n"
            "5. 『あなたの状況に最適な解決手順マトリクス (Decision Matrix)』表\n"
            "6. 実務FAQ（FAQPage schema）\n"
            "7. 根拠法令および公的機関出典（Sources & References）セクション"
        )
    },
    {
        "name": "scenario_matrix_first",
        "instruction": (
            "記事構成アーキタイプC（相手方対応パターン別ロードマップ優先型）:\n"
            "1. 一人称共感導入部 + 検証日入りE-E-A-T監修基準ボックス\n"
            "2. 『相手の態度による3つの分岐点』：連絡可能 vs 音信不通 vs 逆ギレ・威圧的態度\n"
            "3. 分岐別実務対応と申立書・内容証明作成の要点（動的H2/H3）\n"
            "4. 状況別必要書類一覧HTML <table>\n"
            "5. 『あなたの状況に最適な解決手順マトリクス (Decision Matrix)』表\n"
            "6. 実務FAQ（FAQPage schema）\n"
            "7. 根拠法令および公的機関出典（Sources & References）セクション"
        )
    }
]


def generate_article_jp(topic: str, related_articles: list = None) -> dict:
    """
    Generate a full SEO-optimized Japanese article matching Japanese Google SEO, E-E-A-T,
    sources section, and structural archetype diversity.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")

    archetype = random.choice(ARCHETYPES_JP)
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    links_text = ""
    if related_articles:
        links_text = "\n[内部リンク候補記事リスト (Contextual Internal Linking)]\n" + "\n".join(
            [f"- 記事: '{a.get('title')}' -> URL: {a.get('url')}" for a in related_articles[:3]]
        ) + "\n上記リストから本文の文脈に最も合致する1〜2件を選び、本文中に <a href='URL'>記事タイトル</a> の形式で自然な案内リンクボックスを挿入してください。\n"

    user_prompt = (
        f"以下のテーマについて、読者のピンチを解決する実体験談＋具体的マニュアル形式のブログ記事を作成してください：\nテーマ: {topic}\n\n"
        f"{archetype['instruction']}\n\n"
        f"必須要求事項:\n"
        f"1. ❌ 「絶対に勝てる」「100%解決」等の誇大広告・断定的表現を厳禁し、客観的な法的要件と立証手順で記述してください。\n"
        f"2. 導入部直後に最新検証日（'2026年9月18日基準'）入りE-E-A-T基準ボックスを必ず配置してください。\n"
        f"3. 本文内に実務比較<table>および『あなたの状況に最適な解決手順マトリクス (Decision Matrix)』表を含めてください。\n"
        f"4. 記事最下部に『根拠法令および公的機関出典（Sources & References）』セクションを必ず配置してください。{links_text}"
    )

    last_error = None
    for model_name in MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT_JP,
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
                    raise ValueError("Invalid JSON response")

            except Exception as e:
                last_error = e
                print(f"⚠️ {model_name} (試行 {attempt+1}) 一時的エラー: {e}. 再試行中...")
                time.sleep(2)

    raise RuntimeError(f"All models failed to generate article: {last_error}")
