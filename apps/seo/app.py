
import os
import re
import json
import streamlit as st

PROMPT_VERSION = "AI 검색 강화형 v1.2"

def get_client():
    try:
        from openai import OpenAI
    except Exception:
        st.error("openai 패키지가 필요합니다. requirements.txt를 확인해주세요.")
        st.stop()

    api_key = None
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        st.error("OPENAI_API_KEY가 설정되어 있지 않습니다. Streamlit Secrets 또는 환경변수에 추가해주세요.")
        st.stop()

    return OpenAI(api_key=api_key)

SYSTEM_PROMPT = """너는 미샵(MISHARP)의 여성의류 SEO/AI검색 최적화 실무 담당자다.
사용자가 입력한 상품 URL, 상품명, 상품정보를 바탕으로 카페24 상품등록용 SEO 필드를 생성한다.

반드시 아래 원칙을 지켜라.
- 네이버, 다음, 구글, Bing 검색성과 클릭률을 함께 고려
- 단순 상품명 반복 금지
- 상품군 키워드 + 상황형 키워드 + 체형고민형 키워드 + 타깃형 키워드를 자연스럽게 조합
- 유튜브 쇼츠, 인스타 릴스, 틱톡, 네이버 클립 검색 연결 가능성도 감안
- 네이버쇼핑, 스마트스토어, 카카오스타일, 지그재그 검색 의도도 감안
- title은 35~60자 내외
- description은 80~130자 내외
- author는 반드시 MISHARP 또는 미샵 중 하나로 통일
- keywords는 핵심 키워드, 확장 키워드, 상황형 키워드를 섞되 억지 반복 금지
- alt 텍스트는 해당 상품을 가장 짧고 명확하게 표현하는 1~2개 단어
- 아래 검색 의도를 반영:
  1) 어떤 체형에 잘 맞는지
  2) 어떤 상황에 입기 좋은지
  3) 어떤 연령대가 찾는 스타일인지
  4) 어떤 계절/코디에 활용도 높은지
- 결과는 설명 없이 아래 JSON 형식으로만 출력

출력 JSON 형식:
{
  "title": "",
  "author": "",
  "description": "",
  "keywords": "",
  "alt_text": ""
}
"""

USER_TEMPLATE = """[seo]
미샵 카페24 상품등록 시 검색엔진 최적화(seo) 자동 생성 프롬프트

상품 url 또는 상품명/상품정보 입력시 아래 입력 값 자동 생성

1.브라우저 타이틀(title) :
2.메타태그1 author :
3.메타태그2 description :
4.메타태그3 keywords(키워드는 ,로 구분하여 입력합니다) :
5.상품 이미지 alt 텍스트(alt 텍스트는 해당 상품을 표현할 수 있는 1개~2개 단어로 입력하세요) :

네이버, 다음, 구글, bing 검색 seo에 최적화된 위 1~5값을 아래 조건에 맞춰 생성해줘

조건
1. 네이버, 다음, 구글, bing에서 많이 검색될 가능성이 높은 키워드 순서를 우선 고려
2. 단순 상품명만 반복하지 말고
   상품군 키워드 + 상황형 키워드 + 체형고민형 키워드 + 타깃형 키워드를 적절히 조합
3. 유튜브 쇼츠, 인스타 릴스, 틱톡, 네이버 클립 검색에도 연결될 수 있도록 숏폼 검색 키워드 감안
4. 네이버쇼핑, 네이버 스마트스토어, 카카오스타일, 지그재그 검색 최적화도 감안
5. title은 검색성과 클릭률을 함께 고려해 35~60자 내외로 작성
6. description은 80~130자 내외로 작성
7. keywords는 핵심 키워드, 확장 키워드, 상황형 키워드를 섞어서 작성
8. alt 텍스트는 이미지 핵심을 가장 짧고 명확하게 표현
9. author는 "MISHARP" 또는 "미샵" 기준으로 통일
10. 키워드는 억지 반복하지 말고 실제 검색 의도에 맞게 구성
11. 아래 유형의 검색 의도를 반영
   - 어떤 체형에 잘 맞는지
   - 어떤 상황에 입기 좋은지
   - 어떤 연령대가 찾는 스타일인지
   - 어떤 계절/코디에 활용도 높은지
12. 결과는 설명 없이 아래 1~5 항목만 복붙 가능하게 출력

입력 정보
- 상품 URL: {product_url}
- 상품명: {product_name}
- 상품 정보: {product_info}
"""

def call_model(product_url: str, product_name: str, product_info: str, model_name: str = "gpt-4.1-mini"):
    client = get_client()
    user_prompt = USER_TEMPLATE.format(
        product_url=product_url.strip(),
        product_name=product_name.strip(),
        product_info=product_info.strip(),
    )
    response = client.chat.completions.create(
        model=model_name,
        temperature=0.5,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)

def clean_text(v: str) -> str:
    return re.sub(r"\s+", " ", (v or "")).strip()

def section_header(text: str):
    st.markdown(
        f"""
        <div style="
            margin:18px 0 8px 0;
            padding:12px 14px;
            border-radius:12px;
            background:#111827;
            color:#ffffff;
            font-size:18px;
            font-weight:800;
            line-height:1.5;
            border:1px solid rgba(255,255,255,0.14);
            display:block;
            visibility:visible;
            opacity:1;
        ">{text}</div>
        """,
        unsafe_allow_html=True,
    )

def render_result(data: dict):
    title = clean_text(data.get("title", ""))
    author = clean_text(data.get("author", "MISHARP"))
    description = clean_text(data.get("description", ""))
    keywords = clean_text(data.get("keywords", ""))
    alt_text = clean_text(data.get("alt_text", ""))

    st.success("SEO 생성이 완료되었습니다.")
    st.markdown("## 생성 결과")

    section_header("1. 브라우저 타이틀(title) (카페24 SEO 입력)")
    st.text_area("seo_result_title", value=title, height=95, label_visibility="collapsed")

    section_header("2. 메타태그1 author (카페24 SEO 입력)")
    st.text_area("seo_result_author", value=author, height=68, label_visibility="collapsed")

    section_header("3. 메타태그2 description (카페24 SEO 입력)")
    st.text_area("seo_result_description", value=description, height=120, label_visibility="collapsed")

    section_header("4. 메타태그3 keywords (카페24 SEO 입력)")
    st.text_area("seo_result_keywords", value=keywords, height=160, label_visibility="collapsed")

    section_header("5. 상품 이미지 alt 텍스트")
    st.text_area("seo_result_alt", value=alt_text, height=68, label_visibility="collapsed")

    plain_output = "\n".join([
        f"1.브라우저 타이틀(title) : {title}",
        f"2.메타태그1 author : {author}",
        f"3.메타태그2 description : {description}",
        f"4.메타태그3 keywords : {keywords}",
        f"5.상품 이미지 alt 텍스트 : {alt_text}",
    ])

    st.download_button(
        "TXT 다운로드",
        data=plain_output.encode("utf-8-sig"),
        file_name="misharp_seo_result.txt",
        mime="text/plain",
        use_container_width=True,
    )

def app():
    st.markdown(
        """
        <style>
        .seo-card {
            background:#ffffff;
            border:1px solid #ececec;
            border-radius:22px;
            padding:22px;
            margin:8px 0 18px 0;
            box-shadow:0 6px 18px rgba(0,0,0,0.04);
        }
        .seo-chip {
            display:inline-block;
            padding:6px 10px;
            border-radius:999px;
            font-size:12px;
            background:#111;
            color:#fff;
            margin-bottom:8px;
        }
        .seo-help {
            color:#d1d5db;
            font-size:14px;
            line-height:1.7;
        }
        .stTextArea textarea, .stTextInput input {
            color:#111111 !important;
            background:#ffffff !important;
        }
        .stTextArea label, .stTextInput label, .stSelectbox label {
            color:#ffffff !important;
            font-weight:700 !important;
            opacity:1 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="seo-chip">SEO 생성 · AI 검색 강화형</div>', unsafe_allow_html=True)
    st.markdown("### 미샵 SEO 생성기")
    st.caption(f"프롬프트 버전: {PROMPT_VERSION}")

    with st.expander("이 기능은 어떻게 쓰나요?"):
        st.write("상품 URL, 상품명, 상품 정보를 입력하고 SEO 생성을 누르면 카페24에 붙여넣을 1~5 항목이 생성됩니다.")

    st.markdown('<div class="seo-card">', unsafe_allow_html=True)
    product_url = st.text_input("상품 URL", placeholder="https://www.misharp.co.kr/product/detail.html?product_no=...")
    product_name = st.text_input("상품명", placeholder="예: 아멜리 비조 트렌치 자켓")
    product_info = st.text_area(
        "상품 정보",
        placeholder="소재, 핏, 추천 상황, 체형 포인트, 타깃 연령대, 코디 활용도 등을 자유롭게 입력하세요.",
        height=220,
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        model_name = st.selectbox("모델", ["gpt-4.1-mini", "gpt-4.1"], index=0)
    with col2:
        author_default = st.selectbox("author 기준", ["MISHARP", "미샵"], index=0)

    if st.button("SEO 생성", type="primary", use_container_width=True):
        if not product_url and not product_name and not product_info:
            st.warning("상품 URL, 상품명, 상품 정보 중 하나 이상 입력해주세요.")
        else:
            with st.spinner("AI 검색 최적화 SEO를 생성하는 중입니다..."):
                try:
                    result = call_model(product_url, product_name, product_info, model_name)
                    result["author"] = author_default
                    st.session_state["seo_result"] = result
                except Exception as e:
                    st.error(f"생성 중 오류가 발생했습니다: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

    if "seo_result" in st.session_state:
        render_result(st.session_state["seo_result"])

if __name__ == "__main__":
    app()
