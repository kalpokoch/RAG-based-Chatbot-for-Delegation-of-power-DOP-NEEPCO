# %%writefile policy_vector_db.py

import os
import json
import torch
import logging
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# --- Basic Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Class Definition ---
class PolicyVectorDB:
    def __init__(self, persist_directory: str):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory, settings=Settings(allow_reset=True))
        self.collection_name = "neepco_dop_policies"

        self.embedding_model = SentenceTransformer(
            'BAAI/bge-large-en-v1.5',
            device='cuda' if torch.cuda.is_available() else 'cpu'
        )
        logger.info(f"Embedding model loaded on device: {self.embedding_model.device}")
        
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def _flatten_metadata(self, metadata: Dict) -> Dict:
        return {key: str(value) for key, value in metadata.items()}

    def add_chunks(self, chunks: List[Dict]):
        if not chunks:
            logger.info("No chunks provided to add.")
            return

        existing_ids = set(self.collection.get(include=[])['ids'])
        new_chunks = [chunk for chunk in chunks if chunk.get('id') and chunk['id'] not in existing_ids]

        if not new_chunks:
            logger.info("All chunks already exist in the database.")
            return
        
        logger.info(f"Adding {len(new_chunks)} new chunks to the database...")
        batch_size = 32
        for i in range(0, len(new_chunks), batch_size):
            batch = new_chunks[i:i + batch_size]
            texts = [chunk['text'] for chunk in batch]
            ids = [chunk['id'] for chunk in batch]
            metadatas = [self._flatten_metadata(chunk['metadata']) for chunk in batch]
            
            embeddings = self.embedding_model.encode(texts, show_progress_bar=False).tolist()
            
            self.collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
        logger.info(f"✅ Finished adding {len(new_chunks)} chunks.")

    def search(self, query_text: str, top_k: int = 5) -> List[Dict]:
        query_embedding = self.embedding_model.encode([query_text]).tolist()
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        search_results = []
        if results and results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                relevance_score = 1 - results['distances'][0][i]
                if relevance_score > 0.3:
                    search_results.append({
                        'text': doc,
                        'metadata': results['metadatas'][0][i],
                        'relevance_score': relevance_score
                    })
        return search_results

# --- Helper Function ---
def ensure_db_populated(db_instance: PolicyVectorDB, chunks_file_path: str):
    """Checks if the DB is empty and populates it if needed."""
    try:
        if db_instance.collection.count() == 0:
            logger.info("Vector database is empty. Populating...")
            if not os.path.exists(chunks_file_path):
                logger.error(f"Chunks file not found at {chunks_file_path}. Cannot populate DB.")
                return False
            with open(chunks_file_path, 'r', encoding='utf-8') as f:
                chunks_to_add = json.load(f)
            db_instance.add_chunks(chunks_to_add)
        else:
            logger.info("Vector database already contains data.")
        return True
    except Exception as e:
        logger.error(f"Error during DB population: {e}", exc_info=True)
        return False

# --- Execution Block for testing ---
if __name__ == "__main__":
    DB_PATH = "./chroma_db"
    CHUNKS_PATH = "./processed_chunks.json"

    logger.info("Initializing and populating the vector database...")
    vector_db = PolicyVectorDB(persist_directory=DB_PATH)
    is_ready = ensure_db_populated(vector_db, CHUNKS_PATH)
    
    if is_ready:
        logger.info("✅ Database is ready. Performing a test search.")
        test_query = "What is the policy for steel procurement?"
        search_results = vector_db.search(test_query, top_k=2)
        print(f"\n--- Test Search Results for: '{test_query}' ---")
        for result in search_results:
            print(result)
    else:
        logger.error("❌ Database setup failed.")