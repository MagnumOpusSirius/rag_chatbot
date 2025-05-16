import os
from openai import OpenAI
from dotenv import load_dotenv
from pinecone import Pinecone

# Load env
load_dotenv()
#openai.api_key = os.getenv("OPENAI_API_KEY")
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Config
embedding_model = "text-embedding-3-small"
index_name = os.getenv("PINECONE_INDEX")
namespace = "main"
top_k = 5
llm_model = "gpt-4"

index = pc.Index(index_name)

client = OpenAI()
def get_query_embedding(query: str):
    response = client.embeddings.create(
        input=[query],
        model=embedding_model
    )
    return response.data[0].embedding

def retrieve_relevant_chunks(query, top_k=5):
    query_vector = get_query_embedding(query)

    index = pc.Index(index_name)
    results = index.query(vector=query_vector, top_k=top_k, include_metadata=True, namespace=namespace)

    print("\n[DEBUG] Retrieved Chunks:")
    for match in results.matches:
        print(f"Score: {match.score:.4f}\nContent: {match.metadata.get('content', '')[:300]}...\n---")

    chunks = [match.metadata for match in results.matches]

    return chunks


chat_history = []

def build_prompt(user_query: str, retrieved_chunks: list, history: list):
    context_blocks = []
    for chunk in retrieved_chunks:
        section = chunk.get('section', 'Unknown section')
        content = chunk.get('content', '')
        context_blocks.append(f"From '{chunk.get('filename', '')}', page {chunk.get('page', '?')}:\nSection: {section}\n\n{content}")
    context_text = "\n\n---\n\n".join(context_blocks)
    
    history_text = ""
    for turn in history:
        history_text += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n\n"
        
    return f"""You are a helpful assistant that answers based only on the user manual content provided below.

Chat History:
{history_text}

Relevant Context:
{context_text}

User Question: {user_query}

Answer the question mostly based on the context above. Even if the documentation does not provide a specific definition or explanation still provide closer results. If the answer is not really found, respond with 'I couldn’t find the relevant information.'.
"""

def generate_answer(prompt: str):
    response = client.chat.completions.create(
        model=llm_model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant answering based on technical user documentation."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content

def rag_chat_response(user_query: str):
    chunks = retrieve_relevant_chunks(user_query)
    prompt = build_prompt(user_query, chunks, chat_history)
    answer = generate_answer(prompt)
    chat_history.append({"user": user_query, "assistant": answer})
    return answer