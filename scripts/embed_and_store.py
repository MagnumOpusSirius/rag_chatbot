import os
import json
import openai
import numpy as np
from tqdm import tqdm
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables
load_dotenv()

# Initialize clients
openai.api_key = os.getenv("OPENAI_API_KEY")
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Configuration
index_name = os.getenv("PINECONE_INDEX")
namespace = "main"
embedding_model = "text-embedding-3-small"  # or "text-embedding-3-small"
dimension = 1536  # 3072 for large, 1536 for small

# Create index if it doesn't exist
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric="cosine",
        spec={
            "serverless": {
                "cloud": "aws",
                "region": "us-east-1"
            }
        }
    )
    print(f"Created new index: {index_name}")

index = pc.Index(index_name)

# Load all JSON files
chunk_dir = "data/processed_chunks_json"
all_chunks = []

print(f"📦 Reading chunks from: {chunk_dir}")
for filename in os.listdir(chunk_dir):
    if filename.endswith(".json"):
        filepath = os.path.join(chunk_dir, filename)
        with open(filepath, "r") as f:
            chunks = json.load(f)
            all_chunks.extend(chunks)

print(f"🔍 Total chunks to process: {len(all_chunks)}")

# Embedding function
def get_embedding(text):
    response = openai.embeddings.create(
        input=text,
        model=embedding_model
    )
    return response.data[0].embedding

# Prepare data with embeddings
pinecone_data = []
for i, chunk in enumerate(tqdm(all_chunks, desc="Generating embeddings")):
    if chunk.get("content"):
        try:
            embedding = get_embedding(chunk["content"].strip())
            pinecone_data.append({
                "id": f"chunk-{i}",
                "values": embedding,
                "metadata": {
                    "text": chunk["content"].strip(),
                    "source": chunk.get("source", ""),
                    "section": chunk.get("section", ""),
                    "page": chunk.get("metadata", {}).get("page", 0),
                    "filename": chunk.get("metadata", {}).get("filename", "")
                }
            })
        except Exception as e:
            print(f"Error embedding chunk {i}: {str(e)}")
            continue

# Upload in batches
batch_size = 100  # Adjust based on your rate limits
success_count = 0

print(f"🚀 Uploading {len(pinecone_data)} vectors to Pinecone...")
for i in tqdm(range(0, len(pinecone_data), batch_size), desc="Uploading"):
    batch = pinecone_data[i:i + batch_size]
    try:
        index.upsert(vectors=batch, namespace=namespace)
        success_count += len(batch)
    except Exception as e:
        print(f"⚠️ Failed batch {i//batch_size}: {str(e)}")
        # Save failed batch for retry
        with open(f"failed_batch_{i//batch_size}.json", "w") as f:
            json.dump(batch, f)

print(f"✅ Successfully uploaded {success_count}/{len(pinecone_data)} vectors")
print(f"Index stats: {index.describe_index_stats()}")