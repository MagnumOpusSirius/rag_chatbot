rag-chatbot/
├── data/
│   ├── raw_pdfs/             # Original user guide/manual PDFs
│   └── processed_chunks/     # Text chunks with metadata (JSON or CSV)
│
├── embeddings/
│   └── vector_store/         # FAISS index or Pinecone setup
│
├── app/
│   ├── main.py               # Main entrypoint (Streamlit or CLI app)
│   ├── chat_memory.py        # Handles chat history and context windows
│   ├── rag_pipeline.py       # Core logic: retrieval + prompt + LLM
│   └── ui_utils.py           # UI helpers if using Streamlit
│
├── scripts/
│   ├── extract_text.py       # PDF to cleaned text
│   └── build_embeddings.py   # Chunk + embed + store vectors
│
├── config/
│   └── settings.yaml         # Model/API config, chunk size, etc.
│
├── requirements.txt          # Python dependencies
├── .env                      # API keys (OpenAI, Pinecone, etc.)
└── README.md                 # Project overview and instructions