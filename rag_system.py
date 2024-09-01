import os
from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI

# .env 파일에서 환경 변수 로드
load_dotenv()

# OpenAI API 키를 환경 변수에서 가져옴
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def load_retrieval_qa_chain():
    # 임베딩 로드
    embeddings = OpenAIEmbeddings()
    
    # 벡터 저장소 로드
    vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

    # ChatOpenAI 모델 초기화
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    # ConversationalRetrievalChain 생성
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm,
        vectorstore.as_retriever(),
        return_source_documents=True
    )

    return qa_chain

# 질문에 대한 답변 생성 함수
def get_answer(qa_chain, query, chat_history):
    return qa_chain({"question": query, "chat_history": chat_history})

# 사용 예시
if __name__ == "__main__":
    qa_chain = load_retrieval_qa_chain()
    question = "문서 내용을 기반으로 질문에 응답해줘. 모르는 것은 모른다고해. 사실과 너의 생각을 구분해서 알려줘. 영어로 생각하고 한글로 답변해"
    response = get_answer(qa_chain, question, [])
    print(f"Question: {question}")
    print(f"Answer: {response['answer']}")