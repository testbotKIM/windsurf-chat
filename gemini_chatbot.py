import streamlit as st
import google.generativeai as genai
import os

# Gemini API 키 설정 (환경변수 또는 직접 입력)
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    try:
        API_KEY = st.secrets["GEMINI_API_KEY"]
    except Exception:
        st.error("Gemini API 키가 설정되어 있지 않습니다. 환경변수 또는 .streamlit/secrets.toml을 확인하세요.")
        st.stop()
genai.configure(api_key=API_KEY)

genai.configure(api_key=API_KEY)

# Gemini 모델 준비
model = genai.GenerativeModel("gemini-pro")

st.title("Gemini 챗봇")
st.write("Gemini API와 Streamlit을 활용한 간단한 챗봇입니다.")

# 세션 상태에 대화 기록 저장
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 이전 대화 출력
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 입력
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 출력 및 기록
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gemini API로 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("Gemini가 답변 중..."):
            try:
                response = model.generate_content(prompt)
                answer = response.text
            except Exception as e:
                answer = f"오류 발생: {e}"
            st.markdown(answer)
            st.session_state["messages"].append({"role": "assistant", "content": answer})