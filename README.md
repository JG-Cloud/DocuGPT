# DocuGPT - a webapp to talk with your documents

#### Video Demo: 
#### Description: Upload any PDF, TXT, DOCX file to the web-app and ask questions about the content using OpenAI LLMs

DocuGPT is a tool built with Streamlit and OpenAI to enable conversational retrieval of information from your documents. It allows you to interactively search and retrieve information from your PDF, TXT, and DOCX files using OpenAI's language models.

## Features

- **Document Loading**: Upload PDF, TXT, or DOCX files to index their contents.
- **Conversational Retrieval**: Interact with the tool using conversational prompts to retrieve relevant information from your documents.
- **API Key Integration**: Requires an OpenAI API Key to query data effectively.
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
Initially, I had trouble trying to add any uploaded files via streamlit to the vector database to be split,embedded and chunked. The streamlit file uploader uses bytes-IO and caches the uploaded file in memory. I couldn't work out how to stream this into a vectordb. I eventually resorted to saving the uploaded file from memory to a local dorectory. This wasn't scalable and through some googling I discovered the inbuilt 'tempfile' python module which allowed me to store the files in a temp directory which were removed once the application was stopped or refreshed.

## Contributing

Contributions are welcome! If you have any ideas for improvements, feel free to open an issue or submit a pull request.

## Disclaimer

- Using DocuGPT incurs costs associated with embedding (indexing) your data and running queries.
- Data privacy: Your documents are only used for retrieval within the tool and are not shared with third parties.

## License

This project is licensed under the [MIT License](LICENSE).
ormation from your documents. It allows you to interactively search and retrieve information from your PDF, TXT, and DOCX files using OpenAI's language models.

## Features

- **Document Loading**: Upload PDF, TXT, or DOCX files to index their contents.
- **Conversational Retrieval**: Interact with the tool using conversational prompts to retrieve relevant information from your documents.
- **API Key Integration**: Requires an OpenAI API Key to query data effectively.
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

## Contributing

Contributions are welcome! If you have any ideas for improvements, feel free to open an issue or submit a pull request.

## Disclaimer

- Using DocuGPT incurs costs associated with embedding (indexing) your data and running queries.
- Data privacy: Your documents are only used for retrieval within the tool and are not shared with third parties.

## License

This project is licensed under the [MIT License](LICENSE).
