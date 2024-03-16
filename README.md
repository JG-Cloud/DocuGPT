# DocuGPT - a webapp to talk with your documents
#### Video Demo: https://youtu.be/pW5YDOtv2dQ
#### Description: Upload any PDF, TXT, DOCX file to the web-app and ask questions about the content using OpenAI LLMs

DocuGPT is a webapp tool built with Streamlit and OpenAI to enable conversational question and answer with AI of information from your documents. It allows you to upload your chosen documents (PDF, TXT or word docs), interactively search and retrieve information from your files using OpenAI's language models. The chat history will be retained during your session  and cleared thereafter. Any data uploaded or queried is kept private as per OpenAI's privacy policy.

## Features

- **Document Loading**: Upload PDF, TXT, or DOCX files to index their contents.
- **Conversational Retrieval**: Interact with the tool using conversational prompts to retrieve relevant information from your documents.
- **API Key Integration**: DocuGPT requires an OpenAI API key for indexing and querying documents.
- **Data Privacy**: Your data remains private and is only used for retrieval within the tool.

## How to Use

1. **Get OpenAI API Key**: Sign up for OpenAI and get your API Key.
2. **Run DocuGPT**: Insert your OpenAI API Key in the sidebar and upload your documents.
3. **Query Documents**: Enter your search query in the prompt to retrieve relevant information.

## Setup

1. Clone the repository.
2. Install dependencies using `pip install -r requirements.txt`.
3. Run the application using `streamlit run core.py`.
4. Insert your OpenAI API Key and start querying your documents.

## Design decisions
- Initially, I had trouble trying to add any uploaded files via streamlit to the vector database to be split,embedded and chunked. The streamlit file uploader uses bytes-IO and caches the uploaded file in memory. I couldn't work out how to stream this into a vectordb. I eventually resorted to saving the uploaded file from memory to a local directory before embedding. This wasn't scalable and through some googling I discovered the inbuilt 'tempfile' python module which allowed me to store the files in a temp directory which were removed once the application was stopped or refreshed.

- I started to split the webapp code into smaller files but couldn't find a way of tying streamlit code into the Langchain code. Decided to combine the app code into a single file for now with a view to split at a later date

## Files
- core.py: Contains Langchain application, vectordb and streamlit UI python code.
- htmltemplates: Contains the css required for chatbot portion
- FAISS_DB: A folder location for the vectordb temp files
- Other folders: Maintain old code, a collection of webpage links which aided in my troubleshooting/ideas and test files.

## FAQ

- **Why API Key?**: The app requires an API key to access OpenAI's language models for document indexing and retrieval.
- **Cost**: There are costs associated with using OpenAI's services for embedding documents and running queries.
- **Data Usage**: DocuGPT solely uses your uploaded documents for indexing and retrieval. Public datasets are not utilized.
- **Privacy Policy**: Refer to OpenAI's [privacy policy](https://openai.com/policies/privacy-policy) for information on data handling and privacy.

## Dependencies

- Python 3.8+
- Streamlit
- Langchain
- Faiss
- OpenAI API keys

## Features

- **Document Loading**: Upload PDF, TXT, or DOCX files to index their contents.
- **Conversational Retrieval**: Interact with the tool using conversational prompts to retrieve relevant information from your documents.
- **API Key Integration**: Requires an OpenAI API Key to query data effectively.
- **Data Privacy**: Your data remains private and is only used for retrieval within the tool.

## How to Use

1. **Get OpenAI API Key**: Sign up for OpenAI and get your API Key.
2. **Run DocuGPT**: Insert your OpenAI API Key in the sidebar and upload your documents.
3. **Query Documents**: Enter your search query in the prompt to retrieve relevant information.


## Future development ideas
- Add directory browser/selector to choose a directory on your local desktop, to upload files from there.
- Add tabs on main page to choose between uploading files and selecting a directory to upload from
- Add more file types to upload and query
- Add OAuth to login with Google or Facebook identities, and store user preferences
- Add light/dark mode
- Add option to choose a different LLM/provider via drop down menu
- Add cost of query/embedding 


## Contributing

Contributions are welcome! If you have any ideas for improvements, feel free to open an issue or submit a pull request.

## Disclaimer

- Using DocuGPT incurs costs associated with embedding (indexing) your data and running queries.
- Data privacy: Your documents are only used for retrieval within the tool and are not shared with third parties.

## License

This project is licensed under the [MIT License](LICENSE).
