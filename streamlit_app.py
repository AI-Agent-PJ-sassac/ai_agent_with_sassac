import streamlit as st
import time
from workflow import HandoverWorkflow

# 페이지 설정
st.set_page_config(
    page_title="공공기관 인수인계 AI Agent",
    page_icon="🏛️",
    layout="wide"
)

# 헤더 스타일링
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #424242;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #F5F5F5;
    }
    .assistant-message {
        background-color: #E3F2FD;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🏛️ 공공기관 인수인계 AI Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">궁금한 업무 절차나 규정에 대해 물어보세요.</div>', unsafe_allow_html=True)

# 워크플로우 초기화 (캐시 사용)
@st.cache_resource
def get_workflow():
    try:
        return HandoverWorkflow()
    except Exception as e:
        st.error(f"초기화 실패: {e}")
        st.warning("벡터 DB가 생성되어 있는지 확인해주세요. (python vector_store.py 실행 필요)")
        return None

workflow = get_workflow()

# 대화 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []



# 이전 대화 내용 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "references" in message:
            with st.expander("📚 참조 문서 확인하기"):
                st.markdown(message["references"])

# 사용자 입력 처리
if prompt := st.chat_input("질문을 입력하세요..."):
    # 사용자 메시지 표시 및 저장
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    if workflow:
        # AI 응답 생성
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("🤔 답변 생성 중...")
            
            try:
                # 워크플로우 실행
                result = workflow.run(prompt, save_result=True)
                answer = result['answer']
                
                # 답변 표시
                message_placeholder.markdown(answer)
                
                # 참조 문서 구성
                ref_text = ""
                
                # 경고 메시지
                if result.get('warnings'):
                    ref_text += "### ⚠️ 참고사항\n"
                    for warning in result['warnings']:
                        ref_text += f"- {warning}\n"
                    ref_text += "\n"
                
                # 검색 결과 / 템플릿 / 예시 통계
                search_count = len(result.get('search_results', []))
                template_count = len(result.get('templates', []))
                example_count = len(result.get('examples', []))
                
                if search_count > 0 or template_count > 0 or example_count > 0:
                    ref_text += "### 📊 검색 통계\n"
                    if search_count: ref_text += f"- 검색 결과: {search_count}개\n"
                    if template_count: ref_text += f"- 템플릿: {template_count}개\n"
                    if example_count: ref_text += f"- 예시: {example_count}개\n"
                
                # 상세 참조 내용 (필요시 result['search_results'] 등 내용을 상세히 포맷팅 가능)
                # 여기서는 간단히 통계와 경고만 보여주거나, 원본 소스가 있다면 추가 가능
                
                # 참조 문서 표시
                if ref_text:
                    with st.expander("📚 참조 문서 및 상세 정보"):
                        st.markdown(ref_text)
                
                # 대화 기록에 저장
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer,
                    "references": ref_text if ref_text else None
                })
                
            except Exception as e:
                st.error(f"오류 발생: {e}")
                message_placeholder.markdown("죄송합니다. 오류가 발생했습니다.")
