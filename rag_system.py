import os
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

# OpenAI API 키 설정
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# OpenAI API 키를 환경 변수에서 가져옴
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# 1. 문서 로드
loader = DirectoryLoader("path/to/your/documents", glob="**/*.txt")
documents = loader.load()

# 2. 문서 분할
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)

# 3. OpenAI 임베딩 생성 및 Chroma 벡터 저장소에 저장
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(texts, embeddings, persist_directory="./chroma_db")

# 4. 검색 및 질문-답변 체인 생성
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)

# 5. 질문에 대한 답변 생성 함수
def get_answer(query):
    return qa_chain.run(query)

# 사용 예시
if __name__ == "__main__":
    question = "What is the main topic of the documents?"
    answer = get_answer(question)
    print(f"Question: {question}")
    print(f"Answer: {answer}")