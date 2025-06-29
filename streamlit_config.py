import streamlit as st
from tpuf import search_dew_turbopuffer


def setup_steamlit():
    st.set_page_config(
        page_title="Data Engineering Weekly Search",
        page_icon="🔍",
        layout="centered"
    )

    st.title("🔍 Data Engineering Weekly Search")
    st.markdown("Search through the indexed articles from Data Engineering Weekly using Turbopuffer.")

    query = st.text_input("Enter your search query here:", placeholder="e.g., data governance best practices")

    if st.button("Search"):
        if query:
            with st.spinner("Searching Turbopuffer..."):
                results = search_dew_turbopuffer(query, num_results=5)

            if results:
                st.subheader(f"Search Results for '{query}':")
                for i, result in enumerate(results):
                    st.markdown(f"---")
                    st.markdown(f"**{i + 1}. {result['title']}** (Distance: `{result['distance']:.4f}`)")
                    st.write(f"URL: [{result['url']}]({result['url']})")
                    st.write("Snippet:")
                    st.info(result['content_snippet'])  # Display snippet in an info box
            else:
                st.write("No results found for your query. Try a different one!")
        else:
            st.warning("Please enter a query to search.")

    st.markdown("---")
    st.caption("Powered by Turbopuffer and OpenAI Embeddings.")
