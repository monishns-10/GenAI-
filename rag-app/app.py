import os
import tempfile
import streamlit as st
from dotenv import load_dotenv

# Import LangChain modules
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import RetrievalQA

# Load API keys from .env file
load_dotenv(override=True)

# Streamlit Page Setup
st.set_page_config(page_title="RAG PDF Assistant", page_icon="📄")
st.title("📄 Chat with Your PDF")
st.write("Upload a PDF document to process it and ask grounded questions.")

# 1. Initialize session state for vector store to prevent re-building on UI reruns
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

# 2. File Upload UI
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

# 3. Process PDF and build Vector Store
if uploaded_file is not None and st.session_state.vector_store is None:
    with st.spinner("Processing PDF and building vector database..."):
        # Save uploaded file temporarily to disk so PyPDFLoader can read it
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        try:
            # Load PDF
            loader = PyPDFLoader(tmp_path)
            documents = loader.load()
        finally:
            os.remove(tmp_path)  # Clean up temporary file

        # Check for unreadable / empty PDF
        if not documents:
            st.error("The uploaded PDF appears to be empty or contains no readable text.")
        else:
            # Split document into manageable chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, 
                chunk_overlap=200
            )
            chunks = text_splitter.split_documents(documents)
            
            # Add this temporary debug line:
            st.warning(f"DEBUG: Successfully created {len(chunks)} chunks from the PDF.")

            if not chunks:
                st.error("Could not extract readable text chunks from the PDF.")
            else:
                # Create Embeddings and Store in FAISS
                embeddings = OpenAIEmbeddings()
                st.session_state.vector_store = FAISS.from_documents(chunks, embeddings)
                st.success("Vector database ready! You can now ask questions below.")

# 4. Query Input & Answer Generation
if st.session_state.vector_store is not None:
    user_query = st.text_input("Ask a question about the PDF content:")

    if user_query:
        with st.spinner("Searching vector database and generating answer..."):
            # Initialize LLM
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

            # Create Prompt Template
            prompt = PromptTemplate.from_template(
                """
Answer the question based strictly on the provided context below.
If you do not know the answer based on the context, say "I cannot find the answer in the provided document."

<context>
{context}
</context>

Question: {question}
"""
            )

            # Create Retriever and Retrieval QA chain
            retriever = st.session_state.vector_store.as_retriever(search_kwargs={"k": 4})
            qa = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={"prompt": prompt},
            )

            # Execute Query
            # Execute the query using the modern invoke method
            response = qa.invoke({"query": user_query})

            # Display Answer
            st.markdown("### Answer")
            st.write(response["result"])