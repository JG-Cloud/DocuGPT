import os, time

# suppress python warning messages
import warnings
warnings.filterwarnings("ignore")

# Langchain depedencies
from langchain_openai import OpenAI
from langchain_community.llms import OpenAI
# from langchain_community.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

## Import OPENAI embeddings
# from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings

## Import Index with vector DBS/stores
from langchain_community.vectorstores import FAISS

## Import data loader from local file
# from data_loader import vectordb_loader

## Import htmlTemplates from local file
from original_app.htmlTemplates import bot_template, user_template, css

# web framework
import streamlit as st
from streamlit_extras.stylable_container import stylable_container


## vars
# vectorstore path
vectorstore_path = "./FAISS_DB/faiss_index/"
model = "text-embedding-ada-002"

API_KEY_CONFIRMED = False


### data_loader

## Import data loaders for a specific doc or Directory
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import TextLoader

# from langchain_community.document_loaders import UnstructuredFileLoader

## Import embeddings
# from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings


## Import character/text splitter
from langchain.text_splitter import CharacterTextSplitter
## end of data_loader


def api_key_check(OPENAI_API_KEY):
    if (OPENAI_API_KEY).startswith('sk'):
        st.write(':white_check_mark: Key looks correct')
        
        os.environ['OPENAI_API_KEY'] = f"{OPENAI_API_KEY}"
    
        return True
    
    else:
        OPENAI_API_KEY = ""
        st.write(':x: Key is incorrect, please check and re-enter')
        
        return False


# set embeddings
def embeddings():
    embeddings = OpenAIEmbeddings(model=model)
    
    return embeddings

def load_document(uploaded_files):
    if uploaded_files is not None:
        for file in uploaded_files:
            documents = [file.read().decode()]
            
            progress_bar = st.progress(0, text='Loading...')
            for percent_complete in range(100):
                time.sleep(0.01)
                progress_bar.progress(percent_complete + 1, text='Loading...')
            time.sleep(1)
            progress_bar.empty()
            
            st.write("filename:", file.name)
            
            return documents


def initialize_vectorstore():
    # print(os.path.dirname(vectorstore_path))
    if os.path.exists(f'{vectorstore_path}'):
        dir = os.listdir(f"{vectorstore_path}")
        print(f"len_dir: {len(dir)}")
        if len(dir) == 0:
            # Creating new db/index - importing func from vectordb_loader.py
            db = vectordb_loader()
        else:
            # if files already exist, just load the existing db in the path
            db = FAISS.load_local(f"{vectorstore_path}", embeddings())
    
        return db

## data_loader
def vectordb_loader():
    # # define embeddings model
    print(f"working")
    embeddings = OpenAIEmbeddings(model=model)

    # Doc loader - load on app startup only
    loader = TextLoader(load_document())
    docs = loader.load()

    print(len(docs))
    
    # # text_splitter
    print(f"text splitting")
    text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=25)
    texts = text_splitter.create_documents(docs)

    
    # # create/load vectorstore to use as index
    # Guidance: https://python.langchain.com/docs/modules/data_connection/retrievers/# vectorstore db persistence TBC

    # load split text into vectorstore, as set embedding
    vector_db = FAISS.from_documents(
        texts,
        embedding=embeddings,
    )
    vector_db.save_local(f"{vectorstore_path}")
    
    return vector_db

### end of data_loader


##  expose this index in a retriever interface.
def retriever():
    retriever = initialize_vectorstore().as_retriever(search_kwargs={"k":2})
    return retriever


#convo chain
def get_convo_chain(vectorstore):
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    convo_chain = ConversationalRetrievalChain.from_llm(
        llm=OpenAI(),
        retriever=retriever(),
        memory=memory
    )
    
    return convo_chain


# handle user input
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

#################################################
# main - streamlit logic/web config
def main():
    st.set_page_config(
        page_title="Jatin's private Doc QA App",
        page_icon=":pushpin:",
        layout="wide",
        initial_sidebar_state="auto",
        menu_items={
            'About': "# This is a header. This is an *extremely* cool app!"
        }
    )

    # Custom HTML (imported) for styling of chatbot for user, bot and overall CSS
    st.write(css, unsafe_allow_html=True)

    # initialise session state before use
    if "persistent_conversation" not in st.session_state:
        st.session_state.persistent_conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    # setting file vars
    file_read = None
    
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
                load_document(uploaded_files)

                
            # FAQ TEXT
            st.header(':green[FAQ]')
            st.write('- OPENAI API KEY required to query data.')
            st.write('- There is a cost assosiated to embeddings (indexing) your data and running   queries, even against your own files.')
            st.write('- Data is retrieved purely from your documents. Public datasets are not used  here')
            st.write('- Your data will be sent to OPENAI LLMs via back-end API calls. Be mindful of     sending sensitive/personal/client specific data. \
                    \nSee data privacy notice: https://openai.com/policies/privacy-policy')


    # Page title
    st.title("🦜️🔗 Docify GPT")

    # Ask user for query
    # query_prompt_container = st.container()
    # with query_prompt_container:
    #     with stylable_container(
    #         key="query_prompt_container",
    #         css_styles="""
    #         {
    #             position: fixed;
    #             bottom: 3rem;
    #         }
    #         """
    #     ):
    query_prompt = st.text_input('What are you looking for?', placeholder='Search inside my docs... ')
    # Fetch convo history answer from Convo QA Chain
    if query_prompt and API_KEY_CONFIRMED:
        # Take history of convo and create the next element
        conversation = get_convo_chain(initialize_vectorstore())

        # persist convo history - to avoid the entire app reloading (vars re-initialising on every button clicked)
        st.session_state.persistent_conversation = conversation
        
        with st.spinner('fetching answer...'):

            # Return query answers to the screen
            handle_userinput(query_prompt)

    elif query_prompt and not API_KEY_CONFIRMED:
        st.write("Please insert API Key and try again...")

main()