"""
3구역 · 현실 적용 존 (Streamlit)
실행: streamlit run app.py
"""
from __future__ import annotations

import re
import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

_BASE = Path(__file__).resolve().parent
_FLOW_SVG = _BASE / "assets" / "zone3_user_flow_diagram.svg"


def _scenario_image_path(question: dict) -> Path | None:
    """assets/ 기준 상대 경로. 예: scenarios/med_chest_xray.svg"""
    rel = question.get("image")
    if not rel:
        return None
    p = _BASE / "assets" / rel
    return p if p.is_file() else None

# ─────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="3구역 · 현실 적용 존",
    page_icon="🤖",
    layout="centered",
)

st.markdown(
    """
<style>
.zone-header {
    background: linear-gradient(135deg, #7c83eb 0%, #9b87c9 100%);
    color: white;
    padding: 1.5rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    text-align: center;
    box-shadow: 0 6px 24px rgba(124, 131, 235, 0.22);
}
.zone-header h1 { margin: 0; font-size: 1.6rem; }
.zone-header p  { margin: 0.3rem 0 0; opacity: 0.9; font-size: 0.95rem; }

.scenario-box {
    background: #f8f9ff;
    border-left: 4px solid #667eea;
    padding: 1rem 1.2rem;
    border-radius: 0 8px 8px 0;
    margin: 1rem 0;
}
.ai-result-box {
    padding: 1rem 1.2rem;
    border-radius: 8px;
    margin: 0.8rem 0;
    font-weight: 600;
}
.result-partial   { background: #d1ecf1; border: 1px solid #17a2b8; color: #0c5460; }

.explanation-box {
    background: #fff8e1;
    border: 1px solid #ffe082;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-top: 0.8rem;
}
.limit-box {
    background: #fce4ec;
    border: 1px solid #e91e63;
    border-radius: 8px;
    padding: 0.8rem 1.2rem;
    margin-top: 0.6rem;
    font-size: 0.9rem;
}
/* 메인·사이드바 공통 톤: 같은 팔레트 계열로 맞춤 */
.stApp {
    background: linear-gradient(165deg,
        #e8ecff 0%,
        #ede9fe 26%,
        #e0f2fe 52%,
        #fef3c7 78%,
        #fce7f3 100%) !important;
}
.main .block-container {
    padding-top: 1.1rem !important;
    background: rgba(255, 255, 255, 0.72) !important;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: 20px !important;
    border: 1px solid rgba(255, 255, 255, 0.9) !important;
    box-shadow: 0 6px 28px rgba(71, 85, 105, 0.08) !important;
}
/* 사이드바: 본문과 대비되지 않게 비슷한 채도의 색감 */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,
        #e8e8ff 0%,
        #f0e8ff 30%,
        #e6f7f6 60%,
        #fff8e8 100%) !important;
    border-right: 1px solid rgba(148, 163, 184, 0.35) !important;
}
[data-testid="stSidebar"] > div {
    background: transparent !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li {
    color: #475569 !important;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #4f46e5 !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(129, 140, 248, 0.35) !important;
}
/* 분야 선택 CTA: 채도 낮은 인디고 계열 */
.stApp button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1 0%, #818cf8 50%, #a5b4fc 100%) !important;
    color: #ffffff !important;
    border: none !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em;
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.28) !important;
}
.stApp button[kind="primary"]:hover {
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.36) !important;
    filter: brightness(1.04);
}
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# 시나리오 데이터
# ─────────────────────────────────────────────
SCENARIOS = {
    "🏥 의료": {
        "color": "#667eea",
        "intro": "AI가 의료 영상을 분석하고 질병 여부를 판단합니다.",
        "questions": [
            {
                "title": "폐 X-ray 판독",
                "situation": (
                    "AI가 흉부 X-ray 이미지를 분석하고 있습니다. "
                    "오른쪽 폐 하엽에 불투명한 부분이 관찰됩니다. "
                    "환자는 38도 발열과 기침 증상을 호소합니다."
                ),
                "image_desc": "🫁 흉부 X-ray 이미지 (오른쪽 하단 불투명 음영 관찰)",
                "image": "scenarios/med_chest_xray.svg",
                "question": "AI의 판단 결과는 무엇일까요?",
                "choices": [
                    "정상 — 특이 소견 없음",
                    "폐렴 의심 — 추가 검사 권고",
                    "폐암 확정 — 즉시 입원",
                ],
                "ai_answer": 1,
                "confidence": 82,
                "explanation": (
                    "AI는 불투명 음영의 위치·모양·밀도를 분석해 **폐렴 의심** 소견을 출력합니다. "
                    "'확정'이 아니라 '의심'인 이유는 AI가 통계적 패턴으로 학습했기 때문입니다. "
                    "최종 진단은 반드시 의사가 임상 증상과 함께 종합 판단해야 합니다."
                ),
                "ai_limit": (
                    "⚠️ AI 한계: 동일한 음영이 결핵·폐부종과 유사하게 보일 수 있어 "
                    "오탐률(False Positive)이 존재합니다. 훈련 데이터에 없는 희귀 질환은 놓칠 수 있습니다."
                ),
            },
            {
                "title": "피부 병변 분류",
                "situation": (
                    "스마트폰으로 촬영한 피부 사진을 AI가 분석합니다. "
                    "직경 6mm, 불규칙한 경계, 갈색-흑색 혼합 색소를 가진 병변입니다."
                ),
                "image_desc": "🔬 피부 병변 사진 (비대칭, 불규칙 경계, 다색)",
                "image": "scenarios/med_skin_lesion.svg",
                "question": "여러분이라면 이 병변을 어떻게 판단하겠나요?",
                "choices": [
                    "양성 점 — 경과 관찰",
                    "지루각화증 — 치료 불필요",
                    "악성 흑색종 의심 — 전문의 상담 권고",
                ],
                "ai_answer": 2,
                "confidence": 74,
                "explanation": (
                    "ABCDE 기준(비대칭·경계·색·크기·변화)을 학습한 AI는 **악성 흑색종 의심**을 출력합니다. "
                    "신뢰도가 74%로 낮은 이유는 조명·피부색·해상도에 따라 결과가 달라지기 때문입니다."
                ),
                "ai_limit": (
                    "⚠️ AI 한계: 조명·각도·피부색 차이로 인식률이 크게 변합니다. "
                    "2구역에서 배운 '같은 물체도 배경에 따라 다르게 인식'되는 현상이 의료에서도 발생합니다!"
                ),
            },
        ],
    },
    "🚗 자율주행": {
        "color": "#11998e",
        "intro": "AI가 카메라·센서 데이터를 실시간으로 처리해 주행을 결정합니다.",
        "questions": [
            {
                "title": "교차로 보행자 감지",
                "situation": (
                    "자율주행 차량이 교차로에 접근하고 있습니다. "
                    "신호등은 녹색이지만 카메라에 사람 형체가 감지되었습니다. "
                    "우천으로 카메라 시야가 70% 수준입니다."
                ),
                "image_desc": "📷 전방 카메라 영상 (우천, 교차로, 신호 녹색, 왼쪽에 인물 윤곽)",
                "image": "scenarios/auto_crosswalk.svg",
                "question": "AI는 어떤 행동을 선택해야 할까요?",
                "choices": [
                    "녹색 신호이므로 속도 유지",
                    "감속하며 추가 센서(라이다) 확인",
                    "즉시 급정거",
                ],
                "ai_answer": 1,
                "confidence": 91,
                "explanation": (
                    "AI는 카메라 신뢰도 저하를 감지하면 자동으로 **라이다·레이더 데이터와 융합**합니다. "
                    "'감속 + 재확인'이 최적 전략인 이유는 급정거가 후방 추돌을 유발할 수 있기 때문입니다."
                ),
                "ai_limit": (
                    "⚠️ AI 한계: 폭우·역광 상황에서 카메라 인식률이 50% 이하로 떨어질 수 있습니다. "
                    "센서 퓨전(Sensor Fusion)으로 보완하지만, 엣지 케이스에서 오판 가능성이 남습니다."
                ),
            },
            {
                "title": "차선 변경 판단",
                "situation": (
                    "고속도로 주행 중 전방 50m에 느린 차량이 있습니다. "
                    "왼쪽 차선에는 빠른 차량이 접근 중이고, "
                    "오른쪽 차선은 현재 비어 있습니다."
                ),
                "image_desc": "🛣️ 3차선 고속도로 — 전방 저속 차, 좌측 고속 차, 우측 공간",
                "image": "scenarios/auto_highway.svg",
                "question": "여러분이라면 어느 차선을 선택하겠나요?",
                "choices": [
                    "현재 차선 유지 (속도 줄임)",
                    "왼쪽 차선으로 추월",
                    "오른쪽 차선으로 변경",
                ],
                "ai_answer": 2,
                "confidence": 88,
                "explanation": (
                    "AI는 좌측 차량 속도·거리·TTC(충돌예상시간)를 계산해 **오른쪽 차선이 더 안전**하다고 판단합니다. "
                    "추월보다 우측 이동이 위험도가 낮다는 통계 기반 결정입니다."
                ),
                "ai_limit": (
                    "⚠️ AI 한계: 사각지대의 오토바이처럼 센서 범위 밖 물체는 탐지하지 못합니다. "
                    "예상치 못한 끼어들기나 낙하물에는 반응 지연이 생길 수 있습니다."
                ),
            },
        ],
    },
    "🔒 보안": {
        "color": "#f093fb",
        "intro": "AI가 CCTV 및 출입 데이터를 분석해 이상 행동을 탐지합니다.",
        "questions": [
            {
                "title": "얼굴 인식 출입 통제",
                "situation": (
                    "데이터센터 출입구에서 얼굴 인식 시스템이 작동 중입니다. "
                    "등록된 직원 A씨와 92% 일치하는 얼굴이 감지되었지만, "
                    "근무 시간(09-18시)이 아닌 새벽 2시입니다."
                ),
                "image_desc": "📹 출입구 카메라 — 새벽 2시, 얼굴 일치율 92%",
                "image": "scenarios/security_access.svg",
                "question": "AI는 출입을 어떻게 처리해야 할까요?",
                "choices": [
                    "92% 일치이므로 즉시 출입 허가",
                    "출입 보류 + 보안팀 알림 + 추가 인증 요청",
                    "100% 불일치로 처리하여 경보 발령",
                ],
                "ai_answer": 1,
                "confidence": 95,
                "explanation": (
                    "AI는 **얼굴 일치율 + 시간 이상 + 행동 패턴**을 종합해 '위험 스코어'를 계산합니다. "
                    "단순 얼굴 인식만이 아니라 컨텍스트(시간·장소·패턴)를 함께 분석하는 것이 현대 AI 보안의 핵심입니다."
                ),
                "ai_limit": (
                    "⚠️ AI 한계: 일란성 쌍둥이·정교한 마스크에는 취약합니다. "
                    "또한 편향된 훈련 데이터로 인해 특정 인종·성별의 인식률이 낮을 수 있어 공정성 문제가 제기됩니다."
                ),
            },
        ],
    },
    "🛒 쇼핑 추천": {
        "color": "#f5a623",
        "intro": "AI가 구매 이력·행동 데이터를 분석해 개인 맞춤 상품을 추천합니다.",
        "questions": [
            {
                "title": "협업 필터링 추천",
                "situation": (
                    "사용자가 러닝화를 구매했습니다. "
                    "AI가 '이 상품을 구매한 사람들의 다음 구매 패턴'을 분석하고 있습니다. "
                    "분석 데이터: 러닝 양말 68%, 스포츠 음료 45%, 스마트워치 39%, 운동복 35%"
                ),
                "image_desc": "📊 구매 패턴 분석 — 러닝화 구매 후 연관 상품 구매율",
                "image": "scenarios/shopping_pattern.svg",
                "question": "AI는 어떤 상품을 가장 먼저 추천할까요?",
                "choices": [
                    "스마트워치 (고마진 상품)",
                    "러닝 양말 (가장 높은 연관율)",
                    "운동복 (재고 소진 필요)",
                ],
                "ai_answer": 1,
                "confidence": 78,
                "explanation": (
                    "순수 **협업 필터링(Collaborative Filtering)** AI는 연관율이 가장 높은 러닝 양말을 추천합니다. "
                    "하지만 실제 상용 시스템은 마진·재고·광고비 등 비즈니스 목표를 함께 최적화하기 때문에 "
                    "AI의 추천이 항상 '사용자에게 최선'인 것은 아닙니다."
                ),
                "ai_limit": (
                    "⚠️ AI 한계: '필터 버블' 현상 — 비슷한 상품만 반복 추천해 새로운 취향 발견을 방해합니다. "
                    "또한 초기 데이터가 없는 신규 사용자(Cold Start Problem)에게는 추천이 부정확합니다."
                ),
            },
        ],
    },
}

# 분야 선택 카드 (세로 바·글자·배지는 낮은 채도 / 카드 배경은 은은하게)
FIELD_VISUAL = {
    "🏥 의료": {
        "bar": "#b4c0f5",
        "bg": "linear-gradient(145deg, rgba(199,210,254,0.38) 0%, rgba(255,255,255,0.92) 50%, #fafbff 100%)",
        "border": "1px solid rgba(165,180,252,0.5)",
        "shadow": "0 6px 22px rgba(99,102,241,0.07)",
        "title_color": "#3f3f4d",
        "text_color": "#5b5b6a",
        "badge_bg": "rgba(129,140,248,0.16)",
        "badge_fg": "#5153a1",
        "badge_border": "1px solid rgba(129,140,248,0.38)",
    },
    "🚗 자율주행": {
        "bar": "#9fdbd4",
        "bg": "linear-gradient(145deg, rgba(153,246,228,0.35) 0%, rgba(255,255,255,0.92) 50%, #fafffe 100%)",
        "border": "1px solid rgba(94,234,212,0.45)",
        "shadow": "0 6px 22px rgba(45,212,191,0.08)",
        "title_color": "#3f3f4d",
        "text_color": "#4d5f5c",
        "badge_bg": "rgba(45,212,191,0.14)",
        "badge_fg": "#3d6b62",
        "badge_border": "1px solid rgba(45,212,191,0.38)",
    },
    "🔒 보안": {
        "bar": "#e9b8e0",
        "bg": "linear-gradient(145deg, rgba(251,207,232,0.4) 0%, rgba(255,255,255,0.92) 50%, #fffafd 100%)",
        "border": "1px solid rgba(244,114,182,0.4)",
        "shadow": "0 6px 22px rgba(192,132,252,0.07)",
        "title_color": "#3f3f4d",
        "text_color": "#5c5560",
        "badge_bg": "rgba(216,180,254,0.2)",
        "badge_fg": "#6b4f7a",
        "badge_border": "1px solid rgba(192,132,252,0.38)",
    },
    "🛒 쇼핑 추천": {
        "bar": "#f5d08a",
        "bg": "linear-gradient(145deg, rgba(254,243,199,0.55) 0%, rgba(255,255,255,0.92) 50%, #fffdf8 100%)",
        "border": "1px solid rgba(251,191,36,0.45)",
        "shadow": "0 6px 22px rgba(245,158,11,0.08)",
        "title_color": "#3f3f4d",
        "text_color": "#5c5648",
        "badge_bg": "rgba(251,191,36,0.18)",
        "badge_fg": "#8a6231",
        "badge_border": "1px solid rgba(251,191,36,0.42)",
    },
}


def init_state() -> None:
    defaults = {
        "step": 1,
        "field": None,
        "q_index": 0,
        "user_choice": None,
        "score": 0,
        "total": 0,
        # (field, q_index) — Streamlit 재실행 시 점수·애니메이션 중복 방지
        "scored_turn": None,
        "progress_turn": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _choice_label(i: int) -> str:
    return "ABCDEFG"[i]


def _render_flow_diagram_sidebar() -> None:
    """SVG는 data: URL로 넣으면 브라우저가 막는 경우가 많아 iframe(html)로 삽입합니다."""
    if not _FLOW_SVG.is_file():
        st.caption("assets/zone3_user_flow_diagram.svg 가 app.py와 같은 프로젝트의 assets 폴더에 있어야 합니다.")
        return
    try:
        svg = _FLOW_SVG.read_text(encoding="utf-8")
    except OSError:
        st.caption("흐름도 파일을 읽을 수 없습니다.")
        return
    if "<svg" in svg:
        svg = re.sub(
            r"<svg\s+",
            '<svg style="max-width:100%;height:auto;display:block;" ',
            svg,
            count=1,
        )
    components.html(
        f'<div style="width:100%;overflow:auto;background:rgba(255,255,255,0.78);'
        f"border-radius:12px;border:1px solid rgba(148,163,184,0.35);padding:6px 4px;"
        f'">{svg}</div>',
        height=520,
        scrolling=True,
    )


# ─────────────────────────────────────────────
# 사이드바: 흐름도 + 1·2구역 연계 안내
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
<div style="
  background:rgba(255,255,255,0.55);
  border-radius:14px;
  padding:14px 16px 12px 16px;
  margin-bottom:10px;
  border:1px solid rgba(129,140,248,0.28);
  box-shadow:0 4px 14px rgba(99,102,241,0.08);
">
  <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.08em;color:#6366f1;text-transform:uppercase;margin-bottom:10px;">교육 연계</div>
  <ul style="margin:0;padding-left:1.1rem;color:#475569;font-size:0.9rem;line-height:1.55;">
    <li><b style="color:#4f46e5;">1구역</b> 분류 체험 (가위·공·컵)</li>
    <li><b style="color:#7c3aed;">2구역</b> 오류 분석 (조건에 따른 인식 차이)</li>
    <li><b style="color:#0891b2;">3구역</b> 실제 적용 시나리오</li>
  </ul>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
<div style="
  font-size:0.7rem;font-weight:700;letter-spacing:0.06em;color:#6366f1;
  text-transform:uppercase;margin:6px 0 8px 0;
">사용자 흐름도</div>
""",
        unsafe_allow_html=True,
    )
    _render_flow_diagram_sidebar()

init_state()

# ─────────────────────────────────────────────
# 헤더
# ─────────────────────────────────────────────
st.markdown(
    """
<div class="zone-header">
  <h1>🤖 3구역 · 현실 적용 존</h1>
  <p>AI가 실생활과 산업에서 어떻게 판단하는지 직접 체험해보세요</p>
</div>
""",
    unsafe_allow_html=True,
)

step_labels = ["분야 선택", "상황 파악", "내 판단", "AI 결과", "AI 설명"]
cols_step = st.columns(5)
for i, (col, label) in enumerate(zip(cols_step, step_labels)):
    step_num = i + 1
    if step_num < st.session_state.step:
        col.markdown(
            f"<div style='text-align:center;color:#28a745;font-size:0.78rem;'>✅<br>{label}</div>",
            unsafe_allow_html=True,
        )
    elif step_num == st.session_state.step:
        col.markdown(
            f"<div style='text-align:center;color:#667eea;font-weight:700;font-size:0.78rem;'>🔵<br>{label}</div>",
            unsafe_allow_html=True,
        )
    else:
        col.markdown(
            f"<div style='text-align:center;color:#aaa;font-size:0.78rem;'>○<br>{label}</div>",
            unsafe_allow_html=True,
        )

st.markdown(
    "<hr style='margin:0.5rem 0 1.2rem;border:none;border-top:1px solid #eee;'>",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# STEP 1
# ─────────────────────────────────────────────
if st.session_state.step == 1:
    st.markdown("### ✨ ① 체험할 분야를 선택하세요")
    st.caption("각 분야에서 AI가 실제로 어떤 판단을 내리는지 확인할 수 있습니다.")

    field_list = list(SCENARIOS.keys())
    # 2행×2열: 가로 읽기 순서(의료→자율주행, 보안→쇼핑)로 정렬
    rows = (field_list[0:2], field_list[2:4])

    btn_idx = 0
    for pair in rows:
        c_left, c_right = st.columns(2, gap="medium")
        for col, field in zip((c_left, c_right), pair):
            meta = SCENARIOS[field]
            intro = meta["intro"]
            count = len(meta["questions"])
            vis = FIELD_VISUAL.get(
                field,
                {
                    "bar": "#c4c4d4",
                    "bg": "linear-gradient(180deg,#f8fafc,#fff)",
                    "border": "1px solid #e2e8f0",
                    "shadow": "0 4px 14px rgba(15,23,42,0.06)",
                    "title_color": "#3f3f4d",
                    "text_color": "#5b5b6a",
                    "badge_bg": "rgba(100,116,139,0.12)",
                    "badge_fg": "#475569",
                    "badge_border": "1px solid rgba(100,116,139,0.3)",
                },
            )
            with col:
                st.markdown(
                    f"""
<div style="
  position:relative;
  border-radius:16px;
  padding:16px 16px 12px 18px;
  min-height:176px;
  margin-bottom:8px;
  background:{vis['bg']};
  border:{vis['border']};
  box-shadow:{vis['shadow']};
  box-sizing:border-box;
  overflow:hidden;
">
  <div style="position:absolute;left:0;top:0;bottom:0;width:5px;border-radius:16px 0 0 16px;background:{vis['bar']};"></div>
  <div style="font-size:1.05rem;font-weight:600;margin:0 0 10px 0;line-height:1.3;color:{vis['title_color']};letter-spacing:-0.02em;">{field}</div>
  <div style="font-size:0.9rem;color:{vis['text_color']};line-height:1.55;margin:0;">{intro}</div>
  <div style="margin-top:14px;display:inline-block;padding:5px 12px;border-radius:999px;font-size:0.76rem;font-weight:600;color:{vis['badge_fg']};background:{vis['badge_bg']};border:{vis['badge_border']};">📋 시나리오 {count}개</div>
</div>
""",
                    unsafe_allow_html=True,
                )
                if st.button(
                    "🚀 이 분야 체험하기",
                    key=f"field_{btn_idx}",
                    type="primary",
                    use_container_width=True,
                    help=f"{field}: {intro}",
                ):
                    st.session_state.field = field
                    st.session_state.q_index = 0
                    st.session_state.step = 2
                    st.rerun()
            btn_idx += 1

    if st.session_state.total > 0:
        st.info(f"📊 지금까지 {st.session_state.total}문제 중 {st.session_state.score}개가 AI와 동일한 선택")

# ─────────────────────────────────────────────
# STEP 2–5
# ─────────────────────────────────────────────
elif st.session_state.step >= 2:
    field = st.session_state.field
    q_idx = st.session_state.q_index
    scenario = SCENARIOS[field]
    questions = scenario["questions"]

    if q_idx >= len(questions):
        st.success(f"🎉 **{field}** 분야 완료!")
        st.metric("AI와 같은 선택", f"{st.session_state.score}/{st.session_state.total}")
        st.markdown("### 💡 핵심 정리")
        st.info(
            "AI는 **패턴 인식**에 탁월하지만, 학습 데이터 범위 밖의 상황에서는 오류가 발생합니다. "
            "의료·자율주행·보안 등 고위험 분야에서는 **AI + 사람의 협력**이 필수입니다."
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 다른 분야 체험하기", use_container_width=True):
                st.session_state.step = 1
                st.session_state.field = None
                st.session_state.q_index = 0
                st.session_state.user_choice = None
                st.rerun()
        with c2:
            if st.button("🏠 처음으로", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        st.stop()

    q = questions[q_idx]
    turn_key = (field, q_idx)

    st.markdown(f"**{field}** — {q['title']} ({q_idx + 1}/{len(questions)})")

    if st.session_state.step == 2:
        st.subheader("② 상황을 파악하세요")
        img_path = _scenario_image_path(q)
        if img_path is not None:
            st.image(
                str(img_path),
                use_container_width=True,
                caption=f"{q['image_desc']} · 교육용 상황 일러스트 (실제 영상·기록 아님)",
            )
        st.markdown(
            f"""
        <div class="scenario-box">
        <strong>{q['image_desc']}</strong><br><br>
        {q['situation']}
        </div>
        """,
            unsafe_allow_html=True,
        )

        if st.button("✅ 상황 파악 완료 → 내가 직접 판단해보기", use_container_width=True):
            st.session_state.step = 3
            st.rerun()

    elif st.session_state.step == 3:
        st.subheader("③ 여러분이라면 어떻게 판단하겠나요?")
        st.caption(q["situation"][:100] + "...")

        img_path = _scenario_image_path(q)
        if img_path is not None:
            img_col, q_col = st.columns([0.95, 1.05], gap="medium")
            with img_col:
                st.image(str(img_path), use_container_width=True, caption="상황 참고")
            with q_col:
                st.markdown(f"**{q['question']}**")
                for i, choice in enumerate(q["choices"]):
                    if st.button(
                        f"{_choice_label(i)}. {choice}",
                        key=f"choice_{i}",
                        use_container_width=True,
                    ):
                        st.session_state.user_choice = i
                        st.session_state.step = 4
                        st.rerun()
                if st.button("◀ 상황 다시 보기"):
                    st.session_state.step = 2
                    st.rerun()
        else:
            st.markdown(f"**{q['question']}**")
            for i, choice in enumerate(q["choices"]):
                if st.button(
                    f"{_choice_label(i)}. {choice}",
                    key=f"choice_{i}",
                    use_container_width=True,
                ):
                    st.session_state.user_choice = i
                    st.session_state.step = 4
                    st.rerun()
            if st.button("◀ 상황 다시 보기"):
                st.session_state.step = 2
                st.rerun()

    elif st.session_state.step == 4:
        st.subheader("④ AI의 판단 결과 확인")

        user_c = st.session_state.user_choice
        ai_c = q["ai_answer"]
        conf = q["confidence"]

        st.markdown("**내 판단:**")
        st.info(f"{_choice_label(user_c)}. {q['choices'][user_c]}")

        if st.session_state.progress_turn != turn_key:
            st.markdown("**🤖 AI 판단 중...**")
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.006)
                progress.progress(i + 1)
            progress.empty()
            st.session_state.progress_turn = turn_key

        st.markdown("**🤖 AI 결과:**")
        st.markdown(
            f"""
        <div class="ai-result-box result-partial">
        {_choice_label(ai_c)}. {q['choices'][ai_c]}<br>
        <small>신뢰도: {conf}%</small>
        </div>
        """,
            unsafe_allow_html=True,
        )

        if st.session_state.scored_turn != turn_key:
            st.session_state.scored_turn = turn_key
            if user_c == ai_c:
                st.session_state.score += 1
            st.session_state.total += 1

        if user_c == ai_c:
            st.success("✅ AI와 같은 판단을 내렸습니다!")
        else:
            st.warning("🤔 AI와 다른 판단을 내렸습니다. 왜 다른지 설명을 확인해보세요.")

        if st.button("📖 왜 이런 결과가 나왔나요? →", use_container_width=True):
            st.session_state.step = 5
            st.rerun()

    elif st.session_state.step == 5:
        st.subheader("⑤ AI의 특징과 한계")

        st.markdown(
            f"""
        <div class="explanation-box">
        <strong>📌 AI가 이렇게 판단한 이유</strong><br><br>
        {q['explanation']}
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
        <div class="limit-box">
        {q['ai_limit']}
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("**🧠 생각해볼 질문:**")
        st.info(
            "이 AI 시스템이 틀렸을 때 책임은 누구에게 있을까요? "
            "AI 개발자, 사용 기업, 아니면 최종 판단을 내린 사람?"
        )

        st.caption("💡 2구역에서 본 것처럼, 입력(각도·배경·조건)이 바뀌면 실제 AI도 결과가 달라질 수 있습니다.")

        c1, c2 = st.columns(2)
        with c1:
            if q_idx + 1 < len(questions):
                if st.button("▶ 다음 시나리오", use_container_width=True):
                    st.session_state.q_index += 1
                    st.session_state.user_choice = None
                    st.session_state.step = 2
                    st.rerun()
            else:
                if st.button("🎯 결과 보기", use_container_width=True):
                    st.session_state.q_index += 1
                    st.session_state.step = 2
                    st.rerun()
        with c2:
            if st.button("🔄 다른 분야 선택", use_container_width=True):
                st.session_state.step = 1
                st.session_state.field = None
                st.session_state.q_index = 0
                st.session_state.user_choice = None
                st.rerun()

st.markdown("---")
st.caption("3구역 현실 적용 존 · AI 분류 체험 교육 프로그램")
