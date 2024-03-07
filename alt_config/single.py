# tips from : https://betterprogramming.pub/building-a-multi-document-reader-and-chatbot-with-langchain-and-chatgpt-d1864d47e339

import os
from pydoc import doc
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import OpenAI


OPENAI_API_KEY="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"

pdf_loader = PyPDFLoader('/mnt/g/My Drive/Study/Git-Cheatsheet.pdf')
documents = pdf_loader.load()


txt_loader = TextLoader('/mnt/g/My Drive/Study/Kubernetes/EKS notes.txt')
txt_docs = txt_loader.load()

# print(txt_docs)

############

# Load QA chain

chain = load_qa_chain(llm=OpenAI(api_key=OPENAI_API_KEY))
query = 'What is command for a single line git query?'

response = chain.invoke({"input_documents": documents, "question": query})

print(response['output_text'])