import streamlit as st
import os
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma

# Streamlit 앱 설정
st.title("RAG Chatbot")

# OpenAI API 키 설정 (Streamlit Secrets에서 가져오기)
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# 벡터 저장소 로드
embeddings = OpenAIEmbeddings()
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# ChatOpenAI 모델 초기화
llm = ChatOpenAI(model_name="gpt-4-0613", temperature=0)

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