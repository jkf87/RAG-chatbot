import streamlit as st
import os
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter

# Streamlit 앱 설정
st.title("RAG Chatbot")

# OpenAI API 키 설정 (Streamlit Secrets에서 가져오기)
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# 문서 로드 및 벡터 저장소 생성 (처음 실행 시에만)
@st.cache_resource
def load_documents_and_create_vectorstore():
    loader = DirectoryLoader("/documents", glob="**/*.txt")
    documents = loader.load()
    
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(texts, embeddings, persist_directory="./chroma_db")
    
    return vectorstore

# 벡터 저장소 로드
vectorstore = load_documents_and_create_vectorstore()

# ChatOpenAI 모델 초기화
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

# ConversationalRetrievalChain 생성
qa_chain = ConversationalRetrievalChain.from_llm(
    llm,
    vectorstore.as_retriever(),
    return_source_documents=True
)

# 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 사용자 입력
user_input = st.text_input("질문을 입력하세요:")

if user_input:
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # RAG 체인 실행
    response = qa_chain({"question": user_input, "chat_history": [(msg["role"], msg["content"]) for msg in st.session_state.messages]})
    
    # 봇 응답 추가
    st.session_state.messages.append({"role": "assistant", "content": response["answer"]})

# 채팅 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 소스 문서 표시 (선택적)
if st.checkbox("소스 문서 표시"):
    st.write("참조된 소스 문서:")
    for doc in response.get("source_documents", []):
        st.write(doc.page_content)