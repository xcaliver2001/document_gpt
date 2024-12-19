import os
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings, CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain.chains import RetrievalQA

# 사이드바에 OpenAI API 키 입력받기
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")
github_url = "https://github.com/your-repo-link"
st.sidebar.markdown(f"[View on GitHub]({github_url})")

# API 키가 없으면 경고 메시지 표시
if not api_key:
    st.warning("Please enter your OpenAI API key in the sidebar.")
    st.stop()

# OpenAI API 키 설정
llm = ChatOpenAI(api_key=api_key)

# 캐시 디렉토리 설정
cached_dir = LocalFileStore('./cache/')

# 텍스트 분할기 설정
splitter = CharacterTextSplitter.from_tiktoken_encoder(
    separator='\n',
    chunk_size=600,
    chunk_overlap=100,
)

# 파일 업로드
st.title("Document QA with RAG Pipeline")
uploaded_file = st.file_uploader("Upload a text file", type=["txt"])

# 파일이 업로드되면 처리 및 벡터화
if uploaded_file:
    # 데이터 디렉토리 생성
    os.makedirs("./data", exist_ok=True)

    # 파일 저장
    document_path = f"./data/{uploaded_file.name}"
    with open(document_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # 파일 로딩 및 분할
    loader = UnstructuredFileLoader(document_path)
    docs = loader.load_and_split(text_splitter=splitter)

    # 임베딩 및 벡터 저장소 설정
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    cached_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings, cached_dir)
    vectorstore = FAISS.from_documents(docs, cached_embeddings)

    # QA 체인 설정
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type='refine',
        retriever=vectorstore.as_retriever(),
    )

    # 사용자 질문 입력
    question = st.text_input("Ask a question about the document:")

    # 질문이 있을 경우 답변 제공
    if question:
        answer = chain.run(question)
        st.write(f"**Answer:** {answer}")

else:
    st.write("Please upload a document to start.")
