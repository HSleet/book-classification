I created this project because I wanted to sort my digital PDF books by topic. The initial idea was copying every book to a folder for its respective topic, be it AI, backend development, cybersecurity, cooking, horror, and so on, but then I realized, most books can cover multiple categories, so to avoid duplicating books I got the idea to index the books and build some kind of easy access tool to get my books sorted for each category. Maybe just structuring folders to match categories and subcategories down to 2 levels of categories, and storing shortcuts on each. That can prove ineffective though, since when switching or running it in a different OS may not see the shortcuts properly.

For this, the first thing I have to do is to gather all books under a directory, and get their full path, name and some info about it, maybe passing the first 100 pages through an ML model. For this I don't actually need all the metadata, only the title, but it may come in handy.

## Plan: Digital Bookshelf Classification CLI Tool

Build a multi-stage CLI tool that classifies books using metadata retrieval → embedding generation → clustering → LLM-based naming. The system will search for summaries via multiple APIs/sources, fall back to LLM inference for missing data, then apply unsupervised clustering with semantic labeling.

### Steps

1. **Extend Book model** with new fields for summary, categories, subcategories, confidence scores, and metadata source tracking (which API provided the summary).

2. **Build summary retrieval layer** that queries multiple APIs sequentially (Google Books API, Open Library API, ISBNdb) using ISBN-first strategy, then title/author fallback, storing both API summaries when available.

3. **Implement LLM inference fallback** using a lightweight model (e.g., Ollama local or OpenAI API) to generate synthetic summaries for books with no internet-available data.

4. **Create embedding generation module** that converts (title + summary + author) into vectors using a pre-trained model like sentence-transformers or OpenAI embeddings.

5. **Build clustering pipeline** that groups embeddings using HDBSCAN or K-means, then uses LLM to generate semantic cluster names with category/subcategory hierarchies.

6. **Develop CLI interface** with commands: `index` (scan directory), `classify` (process books), `view` (display shelf by category), `export` (save to JSON/CSV).

7. **Structure project** with modular packages: `summary_retriever/`, `embeddings/`, `clustering/`, `models/`, `cli/`, config files, and unit tests.

### Further Considerations

1. **Summary API strategy** - Start with free APIs (Open Library, Google Books) before paid tiers (ISBNdb). Prioritize ISBN lookups; should we implement caching to avoid re-querying?

2. **LLM selection** - Local option (Ollama, Mistral 7B) vs. API-based (OpenAI GPT-4 or Claude). Local is free/offline; API is higher quality. Recommendation: hybrid approach with local fallback.

3. **Embedding model** - Sentence-transformers (`all-mpnet-base-v2`) is free/local; OpenAI embeddings are high-quality but paid. Suggest sentence-transformers for MVP.

4. **Clustering parameters** - HDBSCAN auto-selects cluster count (better for unknown categories); K-means requires tuning. Should we auto-detect optimal number or let users configure?

5. **Category hierarchy depth** - Fixed (category → subcategory) or flexible multi-level? Current plan assumes 2 levels; confirm scope.