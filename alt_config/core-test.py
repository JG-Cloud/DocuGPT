# tips from : https://betterprogramming.pub/building-a-multi-document-reader-and-chatbot-with-langchain-and-chatgpt-d1864d47e339

import os
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_community.vectorstores import faiss
from langchain_openai import OpenAIEmbeddings

import streamlit as st

OPENAI_API_KEY=os.environ['OPENAI_API_KEY']

documents = []


def main():
    streamlit_ui()
    docs_path = 'docs/'
    # load_documents = file_loader(docs_path)
    # docs_split = chunks(load_documents)
    # embed_to_db = embeddings(docs_split)
    # chains(embed_to_db)

def api_key_check(OPENAI_API_KEY):
    if (OPENAI_API_KEY).startswith('sk'):
        st.write(':white_check_mark: Key looks correct')
        
        os.environ['OPENAI_API_KEY'] = f"{OPENAI_API_KEY}"
    
        return True
    
    else:
        OPENAI_API_KEY = ""
        st.write(':x: Key is incorrect, please check and re-enter')
        
        return False

@st.cache_resource  # 👈 Add the caching decorator
def file_loader(docs_path):
    for file in os.listdir(docs_path):
        if file.endswith('pdf'):
            pdf_path = docs_path + file
            pdf_loader = PyPDFLoader(pdf_path)
            documents.extend(pdf_loader.load())

        elif file.endswith('txt'):
            txt_path = docs_path + file
            txt_loader = TextLoader(txt_path)
            documents.extend(txt_loader.load())

        elif file.endswith('doc') or file.endswith('docx'):
            docx_path = docs_path + file
            docx_loader = Docx2txtLoader(docx_path)
            documents.extend(docx_loader.load())
    
    return documents


def chunks(documents):
    # we split the data into chunks of 1,000 characters, with an overlap
    # of 200 characters between the chunks, which helps to give better results
    # and contain the context of the information between chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs_split = text_splitter.split_documents(documents)

    return docs_split


def embeddings(docs_split):
    vectordb = faiss.FAISS.from_documents(
        documents=docs_split,
        embedding=OpenAIEmbeddings(api_key=OPENAI_API_KEY),
    )

    vectordb.save_local(folder_path="FAISS_DB/faiss_index/")
    
    return vectordb


def chains(vectordb):
    from langchain.chains import ConversationalRetrievalChain
    from langchain_openai import ChatOpenAI

    qa_chain = ConversationalRetrievalChain.from_llm(
        ChatOpenAI(api_key=OPENAI_API_KEY),
        vectordb.as_retriever(search_kwargs={'k': 6}),
        return_source_documents=True
    )

    return conversation(qa_chain)


def conversation(qa_chain):
    import sys

    chat_history = []
    while True:
        # this prints to the terminal, and waits to accept an input from the user
        query = input('Prompt: ')
        # give us a way to exit the script
        if query == 'exit' or query == 'quit' or query == 'q':
            print('Exiting')
            # delete docs
            for file in os.listdir('docs/'):
                os.remove(f'docs/{file}')
            # delete vectordb files
            for file in os.listdir('FAISS_DB/faiss_index/'):
                os.remove(f'FAISS_DB/faiss_index/{file}')
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
        

############################################################
## STREAMLIT UI #### 

import os
import streamlit as st
from streamlit_extras.stylable_container import stylable_container

## Import htmlTemplates from local file
from original_app.htmlTemplates import bot_template, user_template, css

from core import file_loader

def streamlit_ui():
    API_KEY_CONFIRMED = False
    st.set_page_config(
        page_title="Docify",
        page_icon=":pushpin:",
        layout="wide",
        initial_sidebar_state="auto",
        menu_items={
            'About': "# This is a header. This is an extremely* cool app!"
        }
    )



    # Custom HTML (imported) for styling of chatbot for user, bot and overall CSS
    st.write(css, unsafe_allow_html=True)


    # initialise session state before use
    if "persistent_conversation" not in st.session_state:
        st.session_state.persistent_conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
        
        
    # Initialise API key first via sidebar but allowing to ask questions
    side_bar_container = st.container()


    with side_bar_container:
        with st.sidebar:
            
            # Insert API KEY in sidebar box
            OPENAI_API_KEY = st.text_input('Enter OPENAI API Key here:', placeholder='API Key begins with: "sk-"  ', type="password")
            run_ai_vectordb_task_bool = True
            
            
            if OPENAI_API_KEY:
                if api_key_check(OPENAI_API_KEY): # check for API key
                    API_KEY_CONFIRMED = True
                    # reveal box to upload files
                    uploaded_files = st.file_uploader("Choose a CSV file", accept_multiple_files=True, disabled=False)
                    run_ai_vectordb_task_bool = False
                    
                    
            # deny uploading of files
            elif OPENAI_API_KEY == "":
                uploaded_files = st.file_uploader("Choose a CSV file", accept_multiple_files=True, disabled=True)
                run_ai_vectordb_task_bool = True
            
            # set button  
            if st.button('Run Docify', disabled=run_ai_vectordb_task_bool):
                file_loader(uploaded_files)


            # FAQ TEXT
            st.header(':green[FAQ]')
            st.write('- OPENAI API KEY required to query data.')
            st.write('- There is a cost assosiated to embeddings (indexing) your data and running   queries, even against your own files.')
            st.write('- Data is retrieved purely from your documents. Public datasets are not used  here')
            st.write('- Your data will be sent to OPENAI LLMs via back-end API calls. Be mindful of sending sensitive/personal/client specific data. \
                    \nSee data privacy notice: https://openai.com/policies/privacy-policy')


    # Page title
    st.title("🦜️🔗 Docify GPT")


    #Ask user for query
    query_prompt_container = st.container()
    with query_prompt_container:
        with stylable_container(
            key="query_prompt_container",
            css_styles="""
            {
                position: fixed;
                bottom: 3rem;
            }
            """
        ):
            query_prompt = st.text_input('What are you looking for?', placeholder='Search inside my docs... ')
            # Fetch convo history answer from Convo QA Chain
            if query_prompt and API_KEY_CONFIRMED:
                # Take history of convo and create the next element
                conversation = get_convo_chain(initialize_vectorstore())

                # persist convo history - to avoid the entire app reloading (vars re-initialising on every button clicked)
                st.session_state.persistent_conversation = conversation

                with st.spinner('fetching answer...'):

                # Return query answers to the screen
                    #handle_userinput(query_prompt)
    
                    response = st.session_state.persistent_conversation({'question': query_prompt})
                    # Add session state if set to none, and thereafter if session state exists then
                    # extend the chat history state as msgs are received
                    if st.session_state.chat_history is None:
                        st.session_state.chat_history = response['chat_history']
                    else:
                        st.session_state.chat_history.extend(response['chat_history'])
                        
                    for item, message in reversed(list(enumerate(st.session_state.chat_history))): #reversed array to display messages top down instead of bo
                        if item % 2 == 0: #using modulo to take messages which are odd numbers in chat history 
                            st.write(user_template.replace("{{MSG}}", f"ME: {message.content}"), unsafe_allow_html=True)
                        else:
                            st.write(bot_template.replace("{{MSG}}", f"AI: {message.content}"), unsafe_allow_html=True)           


            elif query_prompt and not API_KEY_CONFIRMED:
                st.write("Please insert API Key and try again...")







if __name__ == "__main__":
    main()