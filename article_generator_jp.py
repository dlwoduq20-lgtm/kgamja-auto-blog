"""
Japanese Article Generator using Gemini API with 8 Dynamic Narrative Formats.
Eliminates rigid boilerplates and introduces complete structural diversification.
"""
import json
import re
import time
import random
from datetime import datetime, timezone, timedelta
from google import genai
from google.genai import types
from config import GEMINI_API_KEY
from prompt_template_jp import SYSTEM_PROMPT_JP

MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash"
]

JST = timezone(timedelta(hours=9))

EXPANDED_FORMATS_JP = [
    # 0. 1:1 実務法律相談・対話形式
    {
        "id": "consultation_qa_jp",
        "title": "実務法律相談 1:1 対話＆直截ソリューション型",
        "keywords": ["相談", "質問", "どうすれば", "解決", "対応", "弁護士", "慰謝料", "養育費"],
        "instruction": (
            "【フォーマット: 実務法律相談 1:1 対話＆直截ソリューション型】\n"
            "法テラスや専門法律相談窓口で相談者が直面する切実な葛藤を扱うように、読者と向かい合って話すような口語体と実践的解説で展開してください。\n"
            "1. 【相談者の緊急相談内容】: 当事者が直面した現実的トラブルと葛藤（対話録形式の引用ボックス）\n"
            "2. 【エディターの直言診断】: 「今すぐこれだけは絶対にやめてください」- やりがちな致命的失敗の警告\n"
            "3. 【深層一問一答 Q&A 3選】: 読者が最も気になる3つの疑問に対する法令条文（民法等）と判例を交えた回答\n"
            "4. 【実務防衛チェックリスト】: 今すぐ確保すべきLINE/録音/書面 5大証拠一覧 <table>\n"
            "5. 【現実的出口戦略】: 話し合いが困難な場合に法テラスや少額訴訟・調停へ進むルート案内"
        )
    },
    # 1. トラブル発生〜解決 D-Day アクションタイムライン形式
    {
        "id": "chronological_timeline_jp",
        "title": "D-Day 時系列アクションタイムライン型",
        "keywords": ["期限", "日程", "手順", "ステップ", "タイムライン", "退去", "解雇", "督促", "差し押さえ"],
        "instruction": (
            "【フォーマット: D-Day 時系列アクションタイムライン型】\n"
            "トラブル発生から最終解決までの現実的な時間経過（D-Day、3日以内、14日以内、30日以内）に沿ってログブック形式で構成してください。\n"
            "1. 【D-Day トラブル発生当日】: 状況認知直後に取るべき1時間以内の初動防衛ルール\n"
            "2. 【D+1〜3日 初動対応と証拠保全】: 相手方との通話録音の要領、内容証明郵便の文面作成と送付\n"
            "3. 【D+7〜14日 公的機関・法的圧力段階】: 労働基準監督署、消費生活センター、支払督促申立などの実務\n"
            "4. 【D+30日 最終履行と強制執行の分岐点】: 相手方が応じない場合の財産開示・差押え手続きと実費回収\n"
            "5. 【タイムラインまとめ表 <table>】: 各時期の必要書類と時効・除斥期間の点検リスト"
        )
    },
    # 2. ネットの誤解・都市伝説 3選 徹底論破ファクトチェック形式
    {
        "id": "mythbuster_factcheck_jp",
        "title": "ネットの誤解・都市伝説 徹底論破ファクトチェック型",
        "keywords": ["誤解", "噂", "真実", "注意", "違法", "詐欺", "示談", "失敗", "払わない"],
        "instruction": (
            "【フォーマット: ネットの誤解・都市伝説 徹底論破ファクトチェック型】\n"
            "SNSやネット掲示板に溢れる危険な「都市伝説・誤った対処法」3選を根拠法令と判例で論破する構成で展開してください。\n"
            "1. ❌【誤解1: 「ネットでよく言われる危険な対処法」】 vs ⭕【真実: 裁判所判例・法令条文に基づく反論】\n"
            "2. ❌【誤解2: 「多くの人が損をする2つ目の盲点」】 vs ⭕【真実: 実際の不利益・敗訴リスク分析】\n"
            "3. ❌【誤解3: 「絶対信じてはいけない3つ目の俗説」】 vs ⭕【真実: 官公庁の公式見解】\n"
            "4. 【プロだけが知る例外規定（但し書）】: 原則を覆す決定的判例2選の解説\n"
            "5. 【損失防止の実務比較表 <table>】: 誤った対処 vs 正しい定石対応の対照"
        )
    },
    # 3. 裁判所・内容証明 実物書式 穴埋め徹底解説形式
    {
        "id": "document_walkthrough_jp",
        "title": "実物書式・申立書 穴埋め徹底解説型",
        "keywords": ["書き方", "申立書", "様式", "書式", "示談書", "内容証明", "届出", "通知書", "文例"],
        "instruction": (
            "【フォーマット: 実物書式・申立書 穴埋め徹底解説型】\n"
            "実際の裁判所提出書類や内容証明郵便の用紙を机の上に広げて一行ずつ解説するように展開してください。\n"
            "1. 【書式の全体構造と必須記載3大ブロック】\n"
            "2. 【空欄1: 請求の趣旨・原因の書き方】 - 相手方や裁判官が一目で理解できる5W1H文例\n"
            "3. 【空欄2: 『この文言を書くと不受理・逆効果になるNG表現』】 - 補正命令や相手の反論を招く危険な言葉と代替案\n"
            "4. 【空欄3: 添付証拠の提出規格】 - 効力を持つ付属書類一覧とPDF化・電子申立の注意点\n"
            "5. 【完成実戦文例サンプル】: コピーして使える実戦ひな形ボックスと提出前のセルフチェック表"
        )
    },
    # 4. 損益分岐点・費用試算シミュレーション形式
    {
        "id": "cost_simulation_jp",
        "title": "損益分岐点・1円単位費用試算シミュレーション型",
        "keywords": ["費用", "計算", "試算", "弁護士費用", "印紙代", "過払い金", "相場", "手取り", "損得"],
        "instruction": (
            "【フォーマット: 損益分岐点・1円単位費用試算シミュレーション型】\n"
            "抽象論ではなく具体的な金額シミュレーションで読者の実利を証明する構成で展開してください。\n"
            "1. 【モデルケース条件設定】: 読者が直面しやすい具体的状況（請求額、過失割合、相手方の資力等）を設定\n"
            "2. 【1円単位の損益分岐点明細表 <table>】: 請求可能額、弁護士報酬、裁判印紙代・予納金、実質手残り額の内訳\n"
            "3. 【自分でできる3ステップ試算式】: 一般の読者が自力で当てはめられる計算公式\n"
            "4. 【費用を抑える実務テクニック3選】: 着手金ゼロプラン、法テラスの民事法律扶助、弁護士特約の活用法\n"
            "5. 【回収不能・倒れのリスク回避策】: 相手方の無資力による掛け倒れを防ぐ事前調査法"
        )
    },
    # 5. 相手方の主張 vs 自分の対抗策 交渉テーブル・分岐形式
    {
        "id": "negotiation_branching_jp",
        "title": "交渉テーブル＆シナリオ分岐型",
        "keywords": ["交渉", "示談", "対立", "トラブル", "管理会社", "大家", "相手方", "反論", "減額"],
        "instruction": (
            "【フォーマット: 交渉テーブル＆シナリオ分岐型】\n"
            "相手方（管理会社、加害者保険会社、雇用主）との交渉現場で主導権を握るゲーム理論的対立構図で展開してください。\n"
            "1. 【交渉テーブルの対立構図】: 相手方の典型的な圧力・言い分 vs こちらの法的防御論理の対照\n"
            "2. 【シナリオA: 円満示談が成立する場合】 - 後の蒸し返しを防ぐ示談書・合意書の必須条項\n"
            "3. 【シナリオB: 交渉決裂・法的措置へ進む場合】 - 調停・支払督促・少額訴訟への即時切り替え手順\n"
            "4. 【相手の「ハッタリ（ブラフ）」の見破り方】: 法的根拠のない脅し文句のファクトチェック\n"
            "5. 【交渉妥結用セルフチェック表 <table>】"
        )
    },
    # 6. 初心者向け『3分でわかる』法律用語図解＆即時防衛マニュアル
    {
        "id": "beginner_primer_jp",
        "title": "初心者向け『3分でわかる』用語図解＆即時防衛マニュアル型",
        "keywords": ["初心者", "基礎", "簡単", "初めて", "用語", "敷金", "賃貸契約", "クーリングオフ"],
        "instruction": (
            "【フォーマット: 初心者向け『3分でわかる』用語図解＆即時防衛マニュアル型】\n"
            "法律用語が苦手な読者のために、すべての専門用語を日常生活のたとえ話に翻訳して展開してください。\n"
            "1. 【3分概念辞典】: 難しい専門用語3つ（例：善管注意義務、通常損耗、対抗要件等）を日常のたとえで分かりやすく解説\n"
            "2. 【初心者が契約・サインで最も陥りやすい3大罠】: 口約束の危険と特約の盲点\n"
            "3. 【今日から自分の権利を守る3大防壁】: 書面化、日付付き証拠、支払保留権\n"
            "4. 【その場で困った時の切り返しフレーズ】: 不利な承諾を避ける現場トーク例\n"
            "5. 【要点まとめカードと今すぐやるべき手順】"
        )
    },
    # 7. 2026年最新法改正・最高裁判例 ビフォーアフター深層分析コラム
    {
        "id": "before_after_law_jp",
        "title": "2026年最新法改正・判例ビフォーアフター深層分析型",
        "keywords": ["2026", "法改正", "判例", "最高裁", "変更", "新法", "施行", "ガイドライン"],
        "instruction": (
            "【フォーマット: 2026年最新法改正・判例ビフォーアフター深層分析型】\n"
            "2026年の法改正や最新裁判例をベースにした本格的な実務法律コラムとして展開してください。\n"
            "1. 【何が変わったのか】: 以前のルール(Before) vs 2026年現行ルール(After) 対比 <table>\n"
            "2. 【法改正の背景と生活者への実質的影響】\n"
            "3. 【最新重要判例の深層解説】: 裁判所が下した判断理由と立証責任の所在\n"
            "4. 【過渡期に注意すべき新種トラブルと予防策】\n"
            "5. 【改正法に基づく権利主張ガイド】"
        )
    }
]


def select_format_jp(topic: str) -> dict:
    topic_lower = topic.lower()
    scored = []
    for fmt in EXPANDED_FORMATS_JP:
        score = sum(1 for kw in fmt["keywords"] if kw.lower() in topic_lower)
        if score > 0:
            scored.append((score, fmt))
    if scored:
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]
    h_idx = sum(ord(c) for c in topic) % len(EXPANDED_FORMATS_JP)
    return EXPANDED_FORMATS_JP[h_idx]


def generate_article_jp(topic: str, related_articles: list = None) -> dict:
    """
    Generate a full SEO-optimized Japanese article with 8 dynamic narrative formats,
    organic legal citations, and zero rigid boilerplate.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")

    selected_format = select_format_jp(topic)
    print(f"📖 [選択された展開フォーマット(JP)] '{selected_format['title']}' (ID: {selected_format['id']})")

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    links_text = ""
    if related_articles:
        links_text = "\n[内部リンク候補記事リスト (Contextual Internal Linking)]\n" + "\n".join(
            [f"- 記事: '{a.get('title')}' -> URL: {a.get('url')}" for a in related_articles[:3]]
        ) + "\n上記リストから本文の文脈に最も合致する1〜2件を選び、本文中に自然な案内リンクボックスを挿入してください。\n"

    user_prompt = (
        f"以下のテーマについて、読者のピンチを解決する実戦マニュアル形式の高品質ブログ記事を作成してください：\nテーマ: {topic}\n\n"
        f"【今回の必須展開フォーマット】\n"
        f"{selected_format['instruction']}\n\n"
        f"【必須要求事項】:\n"
        f"1. ❌ 「絶対に勝てる」「100%解決」等の誇大広告・断定的表現を厳禁し、客観的な法的要件と立証手順で記述してください。\n"
        f"2. 🚫 画一的な固定バッジ（『🛡️ 監修基準』ボックスや末尾の定型出典枠）を機械的に貼り付けないでください。根拠条文や官公庁基準は本文の自然な流れの中に記述してください。\n"
        f"3. 指定フォーマット（{selected_format['title']}）の文体・構成リズムを忠実に再現してください。{links_text}"
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
                print(f"⚠️ {model_name} (試行 {attempt+1}) エラー: {e}. 再試行中...")
                time.sleep(2)

    raise RuntimeError(f"All models failed to generate Japanese article: {last_error}")
