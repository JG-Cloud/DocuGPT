# tips from : https://betterprogramming.pub/building-a-multi-document-reader-and-chatbot-with-langchain-and-chatgpt-d1864d47e339

import os
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import Chroma, faiss
from langchain_openai import OpenAIEmbeddings

OPENAI_API_KEY="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"

pdf_loader = PyPDFLoader('/mnt/g/My Drive/Study/Git-Cheatsheet.pdf')
pdf_docs = pdf_loader.load()


txt_loader = TextLoader('/mnt/g/My Drive/Study/Kubernetes/EKS notes.txt')
txt_docs = txt_loader.load()


# we split the data into chunks of 1,000 characters, with an overlap
# of 200 characters between the chunks, which helps to give better results
# and contain the context of the information between chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
documents = text_splitter.split_documents(pdf_docs)


vectordb = faiss.FAISS.from_documents(
    documents=documents,
    embedding=OpenAIEmbeddings(api_key=OPENAI_API_KEY),
)

vectordb.save_local(folder_path="./FAISS_DB/faiss_index/")


from langchain.chains import RetrievalQA
from langchain_openai import OpenAI


qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(api_key=OPENAI_API_KEY),
    retriever=vectordb.as_retriever(search_kwargs={'k': 7}),
    return_source_documents=True
)

# we can now execute queries against our Q&A chain
query = 'What is command for a single line git query?'

result = qa_chain.invoke({'query': query})

print(result['result'])