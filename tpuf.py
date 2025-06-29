import os
import turbopuffer as tpuff
from embedding_logic import get_embedding

tpuf_client = tpuff.Turbopuffer(api_key=os.getenv("TURBOPUFFER_API_KEY"), region=os.getenv("TURBOPUFFER_REGION"), )
index_name = "dew_articles"


def store_in_tpuf(embedded_data):

    upsert_columns_data = {
        "id": [],
        "vector": [],
        "url": [],
        "title": [],
        "chunk_index": [],
        "content": []
    }

    for doc in embedded_data:
        if 'embedding' in doc and doc['embedding'] is not None:
            upsert_columns_data["id"].append(doc['chunk_id'])
            upsert_columns_data["vector"].append(doc['embedding'])

            metadata = doc['metadata']
            upsert_columns_data["url"].append(metadata.get('url'))
            upsert_columns_data["title"].append(metadata.get('title'))
            upsert_columns_data["chunk_index"].append(metadata.get('chunk_index'))
            upsert_columns_data["content"].append(metadata.get('content'))
        else:
            print(f"Skipping chunk {doc.get('chunk_id', 'N/A')} due to missing or None embedding.")

    if not upsert_columns_data["id"]:
        print("No valid vectors to write after filtering.")
        return

    index = tpuff.Turbopuffer().namespace(namespace=index_name)

    try:
        index.write(
            upsert_columns=upsert_columns_data,
            distance_metric='cosine_distance',
        )
        print(f"Successfully wrote {len(upsert_columns_data['id'])} chunks to Turbopuffer namespace '{index_name}'.")

    except Exception as e:
        print(f"Error upserting to Turbopuffer: {e}")


def search_dew_turbopuffer(query_text, num_results=5):

    query_embedding = get_embedding(query_text)
    if not query_embedding:
        print("Could not generate query embedding.")
        return []

    index = tpuff.Turbopuffer().namespace(namespace=index_name)
    try:
        results = index.query(
            rank_by=("vector", "ANN", query_embedding),  # ANN for Approximate Nearest Neighbor
            top_k=num_results,
            include_attributes=['url', 'title', 'chunk_index', 'content']
        )


        search_results_formatted = []
        if results and results.rows:
            for row_obj in results.rows:
                result_item = {
                    "id": row_obj.id,
                    "distance": getattr(row_obj, '$dist', None),
                    "url": getattr(row_obj, 'url', 'N/A'),
                    "title": getattr(row_obj, 'title', 'N/A'),
                    "content_snippet": getattr(row_obj, 'content', 'No snippet available')
                }
                search_results_formatted.append(result_item)
        return search_results_formatted
    except Exception as e:
        print(f"Error querying Turbopuffer: {e}")
        return []
