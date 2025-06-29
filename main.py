import json
import os

from tpuf import store_in_tpuf
from embedding_logic import work_on_embedding
from streamlit_config import setup_steamlit

file_path = 'data/dew_list.json'
content_path = 'data/article_content.json'
embedding_path = 'data/embedding_file.json'


def search_query():
    from tpuf import search_dew_turbopuffer
    user_query = "data goverance"
    search_results = search_dew_turbopuffer(user_query, num_results=3)

    if search_results:
        for i, result in enumerate(search_results):
            print(f"\nResult {i + 1} (Distance: {result['distance']:.4f}):")
            print(f"  Title: {result['title']}")
            print(f"  URL: {result['url']}")
            print(f"  Snippet: {result['content_snippet'][:300]}...")  # Display first 300 chars of chunk
    else:
        print("No search results found.")


def check_if_embedding_over():
    if os.path.exists(embedding_path):
        with open(embedding_path, 'r') as f:
            embedding_data = json.load(f)
            print("upsert encoding to tpuf")
            store_in_tpuf(embedding_data)
    else:
        work_on_embedding(file_path, content_path, embedding_path)


check_if_embedding_over()
setup_steamlit()
