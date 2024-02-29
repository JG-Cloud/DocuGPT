# suppress python warning messages
import warnings
warnings.filterwarnings("ignore")

### dependencies

## Import data loaders for a specific doc or Directory
from langchain_community.document_loaders import UnstructuredFileLoader

## Import embeddings
# from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings

## Import Index with vector DBS/stores
from langchain_community.vectorstores import FAISS

## Import character/text splitter
from langchain.text_splitter import CharacterTextSplitter

## import app.py
from app import bytes_data

## vars
model = "text-embedding-ada-002"

# Enable to save to disk & reuse the model (for repeated queries on the same data)


uploaded_file_dataloader = bytes_data


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
    loader = UnstructuredFileLoader(f"{uploaded_file_dataloader}")
    docs = loader.load()    
    
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