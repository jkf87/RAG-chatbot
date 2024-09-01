import os
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma

# .env 파일에서 환경 변수 로드
load_dotenv()

# OpenAI API 키를 환경 변수에서 가져옴
openai_api_key = os.getenv("OPENAI_API_KEY")

def ingest_documents():
    # PDF 문서 로드
    pdf_files = [f for f in os.listdir("./documents") if f.endswith('.pdf')]
    if not pdf_files:
        print("PDF 문서를 찾을 수 없습니다. 'documents' 폴더에 PDF 파일을 추가해주세요.")
        return

    documents = []
    for pdf_file in pdf_files:
        loader = PyPDFLoader(f"./documents/{pdf_file}")
        documents.extend(loader.load())

    # 문서 분할
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)

    # 임베딩 및 벡터 저장소 생성
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(texts, embeddings, persist_directory="./chroma_db")
    vectorstore.persist()

    print("문서 처리 및 벡터 저장소 생성이 완료되었습니다.")

if __name__ == "__main__":
    ingest_documents()