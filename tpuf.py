import os
import turbopuffer as tpuff
from embedding_logic import get_embedding

tpuf_client = tpuff.Turbopuffer(api_key=os.getenv("TURBOPUFFER_API_KEY"), region=os.getenv("TURBOPUFFER_REGION"), )
index_name = "dew_articles"


def store_in_tpuf(embedded_data):

    upsert_columns_data = {
        "id": [],
        "vector": [],
        # Dynamically add metadata attribute keys here
        "url": [],
        "title": [],
        "chunk_index": [],
        "content": []
    }

    for doc in embedded_data:
        if 'embedding' in doc and doc['embedding'] is not None:
            upsert_columns_data["id"].append(doc['chunk_id'])
            upsert_columns_data["vector"].append(doc['embedding'])

            # Populate metadata attributes
            metadata = doc['metadata']
            upsert_columns_data["url"].append(metadata.get('url'))
            upsert_columns_data["title"].append(metadata.get('title'))
            upsert_columns_data["chunk_index"].append(metadata.get('chunk_index'))
            upsert_columns_data["content"].append(metadata.get('content'))
        else:
            print(f"Skipping chunk {doc.get('chunk_id', 'N/A')} due to missing or None embedding.")

    if not upsert_columns_data["id"]:  # Check if any IDs were actually added
        print("No valid vectors to write after filtering.")
        return

    # Get the index (Turbopuffer creates it if it doesn't exist)
    index = tpuff.Turbopuffer().namespace(namespace=index_name)

    try:
        index.write(
            upsert_columns=upsert_columns_data,
            distance_metric='cosine_distance',  # Or 'euclidean_squared' depending on your needs
        )
        print(f"Successfully wrote {len(upsert_columns_data['id'])} chunks to Turbopuffer namespace '{index_name}'.")

    except Exception as e:
        print(f"Error upserting to Turbopuffer: {e}")


def search_dew_turbopuffer(query_text, num_results=5):
    """
    Searches the Turbopuffer index for relevant articles.
    """
    # 1. Embed the user's query using the same embedding model used for articles
    query_embedding = get_embedding(query_text)
    if not query_embedding:
        print("Could not generate query embedding.")
        return []

    # 2. Get the Turbopuffer index instance
    # This 'index_name' should match the one used during ingestion
    index = tpuff.Turbopuffer().namespace(namespace=index_name)

    try:
        # 3. Perform the vector similarity search
        results = index.query(
            # The 'rank_by' parameter is a tuple: (ranking_type, ranking_function, [vector or text query])
            rank_by=("vector", "ANN", query_embedding),  # ANN for Approximate Nearest Neighbor
            top_k=num_results,
            # You can also explicitly request attributes if not all are returned by default
            include_attributes=['url', 'title', 'chunk_index', 'content']
        )

        # 4. Process and format the results from Turbopuffer's response
        search_results_formatted = []
        if results and results.rows:

            for row_obj in results.rows:  # Each 'row_obj' is a 'Row' object
                # Access properties using dot notation on the Row object
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
