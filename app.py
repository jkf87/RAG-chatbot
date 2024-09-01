import streamlit as st
import os
from dotenv import load_dotenv
import base64
import pdfplumber
import PyPDF2
from rag_system import load_retrieval_qa_chain, get_answer

# .env 파일에서 환경 변수 로드
load_dotenv()

# Streamlit 앱 설정
st.set_page_config(page_title="RAG Chatbot", layout="wide")
st.title("RAG Chatbot")

# OpenAI API 키 설정
openai_api_key = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = openai_api_key

# PDF 관련 함수들
def get_base64_of_pdf(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def get_num_pages(file_path):
    with open(file_path, 'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)
        return len(pdf_reader.pages)

def extract_pdf_content(file_path, page_num):
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        if 0 <= page_num < len(pdf_reader.pages):
            page = pdf_reader.pages[page_num]
            return page.extract_text()
    return "페이지를 찾을 수 없습니다."

# PDF 데이터 로드
@st.cache_resource
def load_pdf_data():
    pdf_data = {}
    pdf_files = [f for f in os.listdir("./documents") if f.endswith('.pdf')]
    for pdf_file in pdf_files:
        file_path = f"./documents/{pdf_file}"
        pdf_data[pdf_file] = {
            'path': file_path,
            'base64': get_base64_of_pdf(file_path),
            'num_pages': get_num_pages(file_path)
        }
    return pdf_data

# 벡터 저장소 및 PDF 데이터 로드
qa_chain = load_retrieval_qa_chain()
pdf_data = load_pdf_data()

# 세션 상태 초기화
if 'selected_pdf' not in st.session_state:
    st.session_state.selected_pdf = list(pdf_data.keys())[0] if pdf_data else None
if 'selected_page' not in st.session_state:
    st.session_state.selected_page = 1
if 'messages' not in st.session_state:
    st.session_state.messages = []

# 소스 문서 버튼 클릭 핸들러
def handle_source_click(pdf_file, page_number):
    st.session_state.selected_pdf = pdf_file
    st.session_state.selected_page = page_number + 1

# 레이아웃 설정
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Chat")

    # 사용자 입력
    if prompt := st.chat_input("질문을 입력하세요:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            # RAG 체인 실행
            response = get_answer(qa_chain, prompt, [(msg["content"], msg["content"]) for msg in st.session_state.messages if msg["role"] == "user"])
            full_response = response["answer"]
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

        # 소스 문서 링크 추가
        if response.get("source_documents"):
            st.markdown("**참조된 소스 문서:**")
            for i, doc in enumerate(response["source_documents"]):
                pdf_file = os.path.basename(doc.metadata['source'])
                page_number = doc.metadata['page']
                if st.button(f"문서 {i+1} (페이지 {page_number+1}) 보기", key=f"source_button_{i}", on_click=handle_source_click, args=(pdf_file, page_number)):
                    pass
                with st.expander(f"문서 {i+1} 내용"):
                    st.write(doc.page_content)

    # 채팅 기록 표시 (최신 응답을 맨 위로)
    for message in reversed(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

with col2:
    st.subheader("PDF Viewer")
    if pdf_data:
        # PDF 선택
        selected_pdf = st.selectbox("PDF 선택", list(pdf_data.keys()), index=list(pdf_data.keys()).index(st.session_state.selected_pdf), key="pdf_selector")
        if selected_pdf != st.session_state.selected_pdf:
            st.session_state.selected_pdf = selected_pdf
            st.session_state.selected_page = 1

        # 페이지 선택
        total_pages = pdf_data[st.session_state.selected_pdf]['num_pages']
        page_number = st.number_input("페이지 선택", min_value=1, max_value=total_pages, value=st.session_state.selected_page, key="page_selector")

        # PDF 페이지 표시
        if page_number != st.session_state.selected_page:
            st.session_state.selected_page = page_number
        else:
            with pdfplumber.open(pdf_data[st.session_state.selected_pdf]['path']) as pdf:
                page = pdf.pages[st.session_state.selected_page - 1]
                image = page.to_image()
                st.image(image.original, use_column_width=True)

            st.markdown(f"**{st.session_state.selected_pdf} (페이지 {st.session_state.selected_page}/{total_pages})**")
    else:
        st.markdown("PDF 문서를 찾을 수 없습니다. 'documents' 폴더에 PDF 파일을 추가해주세요.")

# 디버깅 정보 표시
with st.sidebar:
    st.write("Debug Info:")
    st.write(f"Selected PDF: {st.session_state.selected_pdf}")
    st.write(f"Selected Page: {st.session_state.selected_page}")
    st.sidebar.expander("Debug Info").markdown(f"Selected PDF: {st.session_state.selected_pdf}\nSelected Page: {st.session_state.selected_page}")