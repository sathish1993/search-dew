
"""
Splits text into chunks, roughly by tokens (words).
This is a simple word-based chunker.
"""
def chunk_text(text, max_tokens=250, overlap_tokens=50):
    words = text.split()
    chunks = []
    current_chunk_words = []

    for i in range(len(words)):
        current_chunk_words.append(words[i])
        if len(current_chunk_words) >= max_tokens:
            chunks.append(" ".join(current_chunk_words))
            current_chunk_words = current_chunk_words[max_tokens - overlap_tokens:]

    if current_chunk_words: # Add any remaining words as the last chunk
        chunks.append(" ".join(current_chunk_words))

    return chunks