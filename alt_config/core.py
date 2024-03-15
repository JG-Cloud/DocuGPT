# tips from : https://betterprogramming.pub/building-a-multi-document-reader-and-chatbot-with-langchain-and-chatgpt-d1864d47e339

import os, tempfile
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_community.vectorstores import faiss
from langchain_openai import OpenAIEmbeddings

from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory


import streamlit as st




def main():
    streamlit_ui()
    


def api_key_check(api_key):
    global OPENAI_API_KEY
    if (api_key).startswith('sk'):
        st.write(':white_check_mark: Key looks correct')
        
        os.environ['OPENAI_API_KEY'] = f"{api_key}"
        OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
        return True
    
    else:
        OPENAI_API_KEY = ""
        st.write(':x: Key is incorrect, please check and re-enter')
        
        return False

@st.cache_resource(ttl="1h")  # 👈 Add the caching decorator
def file_loader(uploaded_files):
    documents = []
    temp_path = tempfile.TemporaryDirectory()
    for file in uploaded_files:
        if 'pdf' in file.name:
            pdf_path = os.path.join(temp_path.name, file.name)
            with open(pdf_path, "wb") as f:
                f.write(file.getvalue())
            pdf_loader = PyPDFLoader(pdf_path)
            documents.extend(pdf_loader.load())

        elif 'txt' in file.name:
            txt_path = os.path.join(temp_path.name, file.name)
            with open(txt_path, "wb") as f:
                f.write(file.getvalue())
            txt_loader = TextLoader(txt_path)
            documents.extend(txt_loader.load())

        elif 'doc' in file.name or 'docx' in file.name:
            docx_path = os.path.join(temp_path.name, file.name)
            with open(docx_path, "wb") as f:
                f.write(file.getvalue())
            docx_loader = Docx2txtLoader(docx_path)
            documents.extend(docx_loader.load())
    
    # we split the data into chunks of 1,000 characters, with an overlap
    # of 200 characters between the chunks, which helps to give better results
    # and contain the context of the information between chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs_split = text_splitter.split_documents(documents)

    # embeddings
    vectordb = faiss.FAISS.from_documents(
        documents=docs_split,
        embedding=OpenAIEmbeddings(api_key=OPENAI_API_KEY),
    )

    vectordb.save_local(folder_path="FAISS_DB/faiss_index/")

# load vectordb
def initialize_vectorstore():
    if os.path.exists('FAISS_DB/faiss_index/'):
        # if files already exist, just load the existing db in the path
        db = faiss.FAISS.load_local(folder_path='FAISS_DB/faiss_index/', embeddings=OpenAIEmbeddings(api_key=OPENAI_API_KEY))
    
    return db


# retriever
def retriever():
    retriever = initialize_vectorstore().as_retriever(search_kwargs={'k': 6})
    
    return retriever


def get_convo_chain():
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        input_key='question',
        output_key='answer'
    )

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(api_key=OPENAI_API_KEY),
        retriever=retriever(),
        return_source_documents=True,
        memory=memory
    )

    return qa_chain



# handle user input from streamlit ui
def handle_userinput(query_prompt):
    response = st.session_state.persistent_conversation({'question': query_prompt})
    # Add session state if set to none, and thereafter if session state exists then
    # extend the chat history state as msgs are received
    if st.session_state.chat_history is None:
        st.session_state.chat_history = response['chat_history']
    else:
        st.session_state.chat_history.extend(response['chat_history'])
    
    for item, message in reversed(list(enumerate(st.session_state.chat_history))): #reversed array to display messages top down instead of bottom up
        if item % 2 == 0: #using modulo to take messages which are odd numbers in chat history 
            st.write(user_template.replace("{{MSG}}", f"ME: {message.content}"), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace("{{MSG}}", f"AI: {message.content}"), unsafe_allow_html=True)
        

############################################################
## STREAMLIT UI #### 

import streamlit as st
from streamlit_extras.stylable_container import stylable_container

## Import htmlTemplates from local file
from htmlTemplates import bot_template, user_template, css


def streamlit_ui():
    API_KEY_CONFIRMED = False
    st.set_page_config(
        page_title="DocuGPT",
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
                    uploaded_files = st.file_uploader("Choose PDF, TXT, DOCX files", accept_multiple_files=True, disabled=False)
                    run_ai_vectordb_task_bool = False
                    
                    # set button
                    if st.button('Run DocuGPT', disabled=run_ai_vectordb_task_bool):
                        file_loader(uploaded_files)


            # deny uploading of files
            elif OPENAI_API_KEY == "":
                uploaded_files = st.file_uploader("Choose PDF, TXT, DOCX files", disabled=True)
                run_ai_vectordb_task_bool = True
            
            
            

            # FAQ TEXT
            st.header(':green[FAQ]')
            st.write('- OPENAI API KEY required to query data.')
            st.write('- There is a cost assosiated to embeddings (indexing) your data and running   queries, even against your own files.')
            st.write('- Data is retrieved purely from your documents. Public datasets are not used  here')
            st.write('- Your data will be sent to OPENAI LLMs via back-end API calls. Be mindful of sending sensitive/personal/client specific data. \
                    \nSee data privacy notice: https://openai.com/policies/privacy-policy')


    # Page title
    st.title("🦜️🔗 DocuGPT")


    #Ask user for query
    query_prompt_container = st.container()
    with query_prompt_container:
        # with stylable_container(
        #     key="query_prompt_container",
        #     css_styles="""
        #     {
        #         position: fixed;
        #         bottom: 3rem;
        #     }
        #     """
        # ):
        query_prompt = st.text_input('What are you looking for?', placeholder='Search inside my docs... ')
        # Fetch convo history answer from Convo QA Chain
        if query_prompt and API_KEY_CONFIRMED:
            # Take history of convo and create the next element
            conversation = get_convo_chain()

            # persist convo history - to avoid the entire app reloading (vars re-initialising on every button clicked)
            st.session_state.persistent_conversation = conversation

            with st.spinner('fetching answer...'):

            # Return query answers to the screen
                handle_userinput(query_prompt)

        elif query_prompt and not API_KEY_CONFIRMED:
            st.write("Please insert API Key and try again...")



main()