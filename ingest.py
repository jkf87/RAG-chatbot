import os
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma

# OpenAI API 키 설정 (환경 변수로 설정하는 것이 좋습니다)
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# 문서 로드
loader = TextLoader("path/to/your/document.txt")
documents = loader.load()

# 문서 분할
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)

# 임베딩 및 벡터 저장소 생성
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(texts, embeddings, persist_directory="./chroma_db")
vectorstore.persist()

print("문서 처리 및 벡터 저장소 생성이 완료되었습니다.")