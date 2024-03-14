import os
import streamlit as st
from streamlit_extras.stylable_container import stylable_container

## Import htmlTemplates from local file
from htmlTemplates import bot_template, user_template, css

from core import file_loader


def api_key_check(OPENAI_API_KEY):
    if (OPENAI_API_KEY).startswith('sk'):
        st.write(':white_check_mark: Key looks correct')
        
        os.environ['OPENAI_API_KEY'] = f"{OPENAI_API_KEY}"
    
        return True
    
    else:
        OPENAI_API_KEY = ""
        st.write(':x: Key is incorrect, please check and re-enter')
        
        return False


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