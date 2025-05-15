import os
import openai
from dotenv import load_dotenv
from pinecone import Pinecone

# Load env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Config
embedding_model = "text-embedding-3-small"
index_name = os.getenv("PINECONE_INDEX")
namespace = "main"
top_k = 5
llm_model = "gpt-4"

index = pc.Index(index_name)

def get_query_embedding(query: str):
    response = openai.Embedding.create(
        input=[query],
        model=embedding_model
    )
    return response['data'][0]['embedding']

def retrieve_relevant_chunks(query: str):
    query_vector = get_query_embedding(query)
    result = index.query(vector=query_vector, top_k=top_k, include_metadata=True, namespace=namespace)
    return result['matches']

def build_prompt(user_query: str, retrieved_chunks: list):
    context_blocks = []
    for chunk in retrieved_chunks:
        section = chunk['metadata'].get('section', 'Unknown section')
        content = chunk['metadata'].get('content', '')
        context_blocks.append(f"{section}\n{content}")
    context_text = "\n\n---\n\n".join(context_blocks)

    return f"""You are a helpful assistant that answers based only on the user manual content provided below.

User Question: {user_query}

Relevant Context:
{context_text}

Answer the question strictly based on the context above. If the answer is not found, respond with 'I couldn’t find the relevant information.'.
"""

def generate_answer(prompt: str):
    response = openai.ChatCompletion.create(
        model=llm_model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant answering based on technical user documentation."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return response['choices'][0]['message']['content']

def rag_chat_response(user_query: str):
    chunks = retrieve_relevant_chunks(user_query)
    prompt = build_prompt(user_query, chunks)
    return generate_answer(prompt)