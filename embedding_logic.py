import hashlib
import time

from openai import OpenAI
import os
import json

from get_article_content import get_data
from chunk import chunk_text

client = OpenAI()



def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    try:
        response = client.embeddings.create(input=[text], model=model)
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None


def work_on_embedding(file_path, content_path, embedding_path):
    if os.path.exists(content_path):
        print("work on embedding..")
        with open(content_path, 'r') as f:
            data = json.load(f)

        documents_with_embeddings = []
        for doc in data:
            print("working on: " + doc['url'])
            chunks = chunk_text(doc['content'], max_tokens=250, overlap_tokens=50)
            for chunk_idx, chunk_content in enumerate(chunks):
                embedding = get_embedding(chunk_content)
                if embedding:
                    chunk_id = hashlib.sha256(f"{doc['url']}-{chunk_idx}".encode('utf-8')).hexdigest()
                    documents_with_embeddings.append({
                        'chunk_id': chunk_id,
                        'embedding': embedding,
                        'metadata': {
                            'url': doc['url'],
                            'title': doc['title'],
                            'chunk_index': chunk_idx,
                            'content': chunk_content
                        }
                    })
                else:
                    print(f"  Warning: Could not get embedding for chunk {chunk_idx} of {doc['url']}. Skipping.")

            time.sleep(2)

        with open(embedding_path, 'w') as f:
            json.dump(documents_with_embeddings, f)
    else:
        get_data(file_path, content_path)
