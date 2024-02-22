# # python standard mods
import platform

# suppress python warning messages
import warnings
warnings.filterwarnings("ignore")

### dependencies

## Import data loaders for a specific doc or Directory
from langchain_community.document_loaders import TextLoader, DirectoryLoader, UnstructuredWordDocumentLoader, UnstructuredPDFLoader

## Import embeddings
# from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings

## Import Index with vector DBS/stores
from langchain_community.vectorstores import FAISS

## Import character/text splitter
from langchain.text_splitter import CharacterTextSplitter


## vars
model = "text-embedding-ada-002"

# Enable to save to disk & reuse the model (for repeated queries on the same data)

if 'mac' in platform.platform():
    test_dir = '/Users/jatingandhi/Downloads/test_dir'
else:
    test_dir = '/mnt/c/Users/jgandhi/OneDrive - Ensono/Downloads/test_dir'

# vectorstore path
vectorstore_path = "./FAISS_DB/faiss_index/"



# body

def data_loader(OPENAI_API_KEY = None):
    # # define embeddings model
    #Check OPENAI API Key EXISTS
    if OPENAI_API_KEY:
        embeddings = OpenAIEmbeddings(model=model)
    else:
        API_KEY = input("Enter OPENAI API KEY:\n")
        embeddings = OpenAIEmbeddings(openai_api_key=f"{API_KEY}", model=model)
    
    # Doc loader - load on app startup only
    dir_loader = DirectoryLoader(f"{test_dir}", show_progress=True, use_multithreading=True)
    docs = dir_loader.load()    
    
    # # text_splitter
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(docs)    
    
    
    # # create/load vectorstore to use as index
    # Guidance: https://python.langchain.com/docs/modules/data_connection/retrievers/# vectorstore db persistence TBC

    # load split text into vectorstore, as set embedding
    db = FAISS.from_documents(
        texts,
        embedding=embeddings,
    )
    db.save_local("./FAISS_DB/faiss_index")   
    
    return db


if __name__ == "__main__":
    data_loader()