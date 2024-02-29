import os


# suppress python warning messages
import warnings
warnings.filterwarnings("ignore")

# Langchain depedencies
from langchain_openai import OpenAI
from langchain_community.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

## Import OPENAI embeddings
# from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings

## Import Index with vector DBS/stores
from langchain_community.vectorstores import FAISS

## Import data loader from local file
from data_loader import data_loader

## Import htmlTemplates from local file
from htmlTemplates import bot_template, user_template, css

# web framework
import streamlit as st
from streamlit_extras.stylable_container import stylable_container

## vars
# vectorstore path
vectorstore_path = "./FAISS_DB/faiss_index/"
model = "text-embedding-ada-002"

### functions

# set embeddings
def embeddings():
    embeddings = OpenAIEmbeddings(model=model)
    
    return embeddings


def initialize_vectorstore(API_KEY = None):
    if os.path.exists(f'{vectorstore_path}'):
        dir = os.listdir(f"{vectorstore_path}")
        if len(dir) == 0:
            # Creating new db/index - importing func from data_loader.py
            db = data_loader(API_KEY)
        else:
            # if files already exist, just load the existing db in the path
            db = FAISS.load_local(f"{vectorstore_path}", embeddings())
    
    return db


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


### ORIGINAL MISTAKE LEARNINGS
# # handle user input
# def handle_userinput(query_prompt):
#     response = st.session_state.persistent_conversation({'question': query_prompt})
    
#     ### I was assigning the response from the AI to st.session_state.chat_history each time, 
#     ### which would overwrite the previous history. If you want to maintain the history, 
#     ### you should append the response to the existing chat history instead of assigning it directly.
#     ### using extend() method
#     st.session_state.chat_history = response['chat_history']

    
#     for item, message in enumerate(st.session_state.chat_history):
#         if item % 2 == 0: #using modulo to take messages which are odd numbers in chat history 
#             st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
#         else:
#             st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
              

# main - streamlit logic/web config
def main():
    st.set_page_config(
        page_title="Jatin's private ChatGPT App",
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

    # initialise vars before use outside of loop
    API_KEY_CONFIRMED = None
    
    # Initialise API key first via sidebar but allowing to ask questions
    side_bar_container = st.container()
    
    with side_bar_container:
        with st.sidebar:

            # Insert API KEY in sidebar box  
            OPENAI_API_KEY = st.text_input('Enter OPENAI API Key here:', placeholder='API Key begins with: "sk-"  ', type="password")

            if OPENAI_API_KEY:
                if (OPENAI_API_KEY).startswith('sk'):
                    st.write(':white_check_mark: Key looks correct')
                    API_KEY_CONFIRMED = True
                    os.environ['OPENAI_API_KEY'] = f"{OPENAI_API_KEY}"

                    # # Create/Load vectorstore
                    initialize_vectorstore()

                else:
                    OPENAI_API_KEY = ""
                    st.write(':x: Key is incorrect, please check and re-enter')

            # box to upload files
            uploaded_files = st.file_uploader("Choose a CSV file", accept_multiple_files=True)
            
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    bytes_data = uploaded_file.read()
                    st.write("filename:", uploaded_file.name)
                    st.write(bytes_data)
                    
                    # data_loader(OPENAI_API_KEY)
                    
                # initialize_vectorstore() # Create/Load vectorstore
                

            # # Refresh/Create Index
            # st.header(':yellow[Update index]')
            # if st.button('Refresh Index'):
            #     with st.spinner('Refreshing...'):
            #         time.sleep(5)
            #         st.write('Testing')

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
                conversation = get_convo_chain(initialize_vectorstore(os.environ['OPENAI_API_KEY']))

                # persist convo history - to avoid the entire app reloading (vars re-initialising on every button clicked)
                st.session_state.persistent_conversation = conversation
                
                with st.spinner('fetching answer...'):

                    # Return query answers to the screen
                    handle_userinput(query_prompt)

            elif query_prompt and not API_KEY_CONFIRMED:
                st.write("Please insert API Key and try again...")
        

main()