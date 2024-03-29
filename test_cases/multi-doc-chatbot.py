# tips from : https://betterprogramming.pub/building-a-multi-document-reader-and-chatbot-with-langchain-and-chatgpt-d1864d47e339

import os
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_community.vectorstores import faiss
from langchain_openai import OpenAIEmbeddings

OPENAI_API_KEY=os.environ['OPENAI_API_KEY']

documents = []
for file in os.listdir('./alt_config/docs/'):
    if file.endswith('pdf'):
        pdf_path = './alt_config/docs/' + file
        pdf_loader = PyPDFLoader(pdf_path)
        documents.extend(pdf_loader.load())

    elif file.endswith('txt'):
        txt_path = './alt_config/docs/' + file
        txt_loader = TextLoader(txt_path)
        documents.extend(txt_loader.load())

    elif file.endswith('doc') or file.endswith('docx'):
        docx_path = './alt_config/docs/' + file
        docx_loader = Docx2txtLoader(docx_path)
        documents.extend(docx_loader.load())


# we split the data into chunks of 1,000 characters, with an overlap
# of 200 characters between the chunks, which helps to give better results
# and contain the context of the information between chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
docs_split = text_splitter.split_documents(documents)


vectordb = faiss.FAISS.from_documents(
    documents=docs_split,
    embedding=OpenAIEmbeddings(api_key=OPENAI_API_KEY),
)

vectordb.save_local(folder_path="./alt_config/FAISS_DB/faiss_index/")



from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI


qa_chain = ConversationalRetrievalChain.from_llm(
    ChatOpenAI(api_key=OPENAI_API_KEY),
    vectordb.as_retriever(search_kwargs={'k': 6}),
    return_source_documents=True
)

import sys

chat_history = []
while True:
    # this prints to the terminal, and waits to accept an input from the user
    query = input('Prompt: ')
    # give us a way to exit the script
    if query == 'exit' or query == 'quit' or query == 'q':
        print('Exiting')
        # delete docs
        for file in os.listdir('./alt_config/docs/'):
            os.remove(f'./alt_config/docs/{file}')
        # delete vectordb files
        for file in os.listdir('./alt_config/FAISS_DB/faiss_index/'):
            os.remove(f'./alt_config/FAISS_DB/faiss_index/{file}')
        sys.exit()
        
    # we pass in the query to the LLM, and print out the response. As well as
    # our query, the context of semantically relevant information from our
    # vector store will be passed in, as well as list of our chat history
    
    result = qa_chain.invoke({'question': query, 'chat_history': chat_history})
    print('Answer: ' + result['answer'])
    
    
    # we build up the chat_history list, based on our question and response
    # from the LLM, and the script then returns to the start of the loop
    # and is again ready to accept user input.
    chat_history.append((query, result['answer']))